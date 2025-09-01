import time
import uuid
import json
import collections
from typing import Optional, Dict, List, Any, Callable

from sqlalchemy.orm import Session
from sqlalchemy import delete, desc

# Importar los modelos y las funciones de cifrado
from . import models
from .security import encrypt_data, decrypt_data

# --- Clase MemoryStore Refactorizada ---

class MemoryStore:
    """
    Gestiona la memoria de la IA usando SQLAlchemy para la persistencia.
    Incluye lógica para la sincronización de memoria en un enjambre.
    """
    def __init__(self, short_term_limit=100, lru_cache_size=50):
        """
        Inicializa las cachés en memoria.
        El callback de broadcast se usará para enviar memorias al enjambre.
        """
        self.short_term = collections.deque(maxlen=short_term_limit)
        self.lru_cache = collections.OrderedDict()
        self.lru_cache_size = lru_cache_size
        self.broadcast_callback: Optional[Callable[[Dict], None]] = None

    def set_broadcast_callback(self, callback: Callable[[Dict], None]):
        """Establece la función a llamar para transmitir una memoria al enjambre."""
        self.broadcast_callback = callback

    def log_episode(self, db: Session, type: str, source: str, data: Dict[str, Any], priority: int = 0, long_term: bool = True) -> Dict:
        """
        Registra un evento (episodio) en la memoria.
        Si la prioridad es alta, lo transmite al enjambre.
        """
        episode_id = str(uuid.uuid4())
        timestamp = time.time()

        # Cifrar el contenido de los datos antes de guardarlos en la DB a largo plazo
        # La memoria a corto plazo los mantiene descifrados por rendimiento.
        data_to_store = data
        if long_term:
            json_data = json.dumps(data)
            data_to_store = encrypt_data(json_data)
        
        new_episode_data = {
            'id': episode_id,
            'timestamp': timestamp,
            'type': type,
            'source': source,
            'data': data_to_store, # Contendrá datos cifrados para long_term
            'priority': priority,
            'access_count': 0
        }

        if long_term:
            db_episode = models.EpisodicMemory(**new_episode_data)
            db.add(db_episode)
            db.commit()
            
            # Si la prioridad es > 0 y hay un callback, transmitir al enjambre.
            if priority > 0 and self.broadcast_callback:
                print(f"[Memoria] Transmitiendo recuerdo de alta prioridad (P{priority}) al enjambre.")
                self.broadcast_callback('memory_sync', new_episode_data)
        else:
            self.short_term.append(new_episode_data)
        
        self._update_lru(episode_id, new_episode_data)
        return new_episode_data

    def add_remote_episode(self, db: Session, episode_data: Dict[str, Any]):
        """
        Añade un episodio recibido de otro nodo del enjambre.
        No vuelve a transmitirlo para evitar bucles.
        """
        # Comprobar si el recuerdo ya existe para evitar duplicados
        existing = db.query(models.EpisodicMemory).filter_by(id=episode_data.get('id')).first()
        if existing:
            # Opcional: se podría actualizar si el nuevo tiene más información
            return

        print(f"[Memoria] Recibido recuerdo remoto {episode_data.get('id')} para almacenar.")
        db_episode = models.EpisodicMemory(**episode_data)
        db.add(db_episode)
        db.commit()
        self._update_lru(episode_data['id'], episode_data)


    def get_memory(self, db: Session, query: str, context: Optional[List[str]] = None, top_n: int = 5) -> List[Dict]:
        """Busca recuerdos relevantes, priorizando los de mayor prioridad y más recientes."""
        # Ordenar por prioridad y luego por timestamp
        all_db_memories = db.query(models.EpisodicMemory).order_by(
            desc(models.EpisodicMemory.priority), 
            desc(models.EpisodicMemory.timestamp)
        ).limit(1000).all()
        
        long_term_dicts = []
        for mem in all_db_memories:
            mem_dict = mem.__dict__
            # Descifrar el campo de datos si es de tipo bytes (cifrado)
            if isinstance(mem_dict.get('data'), bytes):
                decrypted_json = decrypt_data(mem_dict['data'])
                mem_dict['data'] = json.loads(decrypted_json)
            long_term_dicts.append(mem_dict)

        all_memories = list(self.short_term) + long_term_dicts
        scored_memories = []

        for mem in all_memories:
            score = 0
            mem_content_lower = json.dumps(mem.get('data', '')).lower()
            if query.lower() in mem_content_lower:
                score += 2
            
            # Añadir la prioridad a la puntuación
            score += mem.get('priority', 0)

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