import time
import uuid
import json
import collections
from typing import Optional, Dict, List, Any

from sqlalchemy.orm import Session
from sqlalchemy import delete

# Importar los modelos desde el archivo centralizado
from . import models

# --- Clase MemoryStore Refactorizada ---

class MemoryStore:
    """
    Gestiona la memoria de la IA usando SQLAlchemy para la persistencia.
    Mantiene cachés en memoria para un acceso rápido.
    """
    def __init__(self, short_term_limit=100, lru_cache_size=50):
        """
        Inicializa las cachés en memoria. No gestiona conexiones de DB.
        """
        self.short_term = collections.deque(maxlen=short_term_limit)
        self.lru_cache = collections.OrderedDict()
        self.lru_cache_size = lru_cache_size

    def log_episode(self, db: Session, type: str, source: str, data: Dict[str, Any], long_term: bool = True) -> Dict:
        """Registra un evento (episodio) en la memoria."""
        episode_id = str(uuid.uuid4())
        timestamp = time.time()
        
        new_episode_data = {
            'id': episode_id,
            'timestamp': timestamp,
            'type': type,
            'source': source,
            'data': data,
            'access_count': 0
        }

        if long_term:
            db_episode = models.EpisodicMemory(**new_episode_data)
            db.add(db_episode)
            db.commit()
        else:
            self.short_term.append(new_episode_data)
        
        self._update_lru(episode_id, new_episode_data)
        return new_episode_data

    def get_memory(self, db: Session, query: str, context: Optional[List[str]] = None, top_n: int = 5) -> List[Dict]:
        """Busca recuerdos relevantes en la memoria episódica a largo plazo."""
        all_db_memories = db.query(models.EpisodicMemory).order_by(models.EpisodicMemory.timestamp.desc()).limit(1000).all()
        long_term_dicts = [mem.__dict__ for mem in all_db_memories]

        all_memories = list(self.short_term) + long_term_dicts
        scored_memories = []

        for mem in all_memories:
            score = 0
            mem_content_lower = json.dumps(mem.get('data', '')).lower()
            if query.lower() in mem_content_lower:
                score += 2
            
            if score > 0:
                scored_memories.append((mem, score))

        scored_memories.sort(key=lambda x: x[1], reverse=True)
        results = [mem for mem, score in scored_memories[:top_n]]

        # Incrementar contador de acceso para los resultados encontrados en la DB
        for r in results:
            if 'id' in r and not isinstance(r, dict):
                r['access_count'] += 1
                db.query(models.EpisodicMemory).filter(models.EpisodicMemory.id == r['id']).update({'access_count': r['access_count']})
        db.commit()
        
        return results

    def reset_memory(self, db: Session):
        """
        Limpia COMPLETAMENTE toda la memoria episódica y de clave-valor de la DB.
        También limpia las cachés en memoria.
        """
        db.execute(delete(models.EpisodicMemory))
        db.execute(delete(models.KeyValueStore))
        db.commit()
        
        self.short_term.clear()
        self.lru_cache.clear()
        print("[Memoria] La memoria episódica y de clave-valor ha sido reseteada.")

    def _update_lru(self, key: str, value: Any):
        """Actualiza la caché LRU."""
        self.lru_cache[key] = value
        self.lru_cache.move_to_end(key)
        if len(self.lru_cache) > self.lru_cache_size:
            self.lru_cache.popitem(last=False)