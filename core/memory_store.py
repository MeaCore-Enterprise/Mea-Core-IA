
import collections
import time
import uuid
import json
import sqlite3
import os
from typing import Any, Dict, List, Optional

class MemoryStore:
    """Gestiona la memoria de la IA, con persistencia en SQLite.

    Utiliza una cola para la memoria a corto plazo (en RAM), una lista para la
    memoria a largo plazo (sincronizada con una DB) y una caché LRU.
    """
    def __init__(self, short_term_limit=100, lru_cache_size=50, db_path="data/memory.db"):
        """Inicializa los distintos niveles de memoria y la base de datos.

        Args:
            short_term_limit (int): Máximo de recuerdos en memoria a corto plazo.
            lru_cache_size (int): Máximo de elementos en la caché LRU.
            db_path (str): Ruta al archivo de la base de datos SQLite.
        """
        self.short_term = collections.deque(maxlen=short_term_limit)
        self.lru_cache = collections.OrderedDict()
        self.lru_cache_size = lru_cache_size
        self._instance_id = str(uuid.uuid4())
        self.db_path = db_path
        self.conn = None
        self._init_db()
        self.long_term = self._load_from_db()

    def _init_db(self):
        """(Privado) Inicializa la conexión a la DB y crea la tabla si no existe."""
        try:
            # Asegurarse de que el directorio de datos exista
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    meta TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] Error en la base de datos: {e}")
            self.conn = None

    def _load_from_db(self) -> List[Dict]:
        """(Privado) Carga todos los recuerdos de largo plazo desde la DB."""
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, content, meta, timestamp FROM long_term_memory ORDER BY timestamp ASC")
            rows = cursor.fetchall()
            memories = []
            for row in rows:
                memories.append({
                    'id': row[0],
                    'content': row[1],
                    'meta': json.loads(row[2]),
                    'timestamp': row[3]
                })
            print(f"[MemoryStore] Cargados {len(memories)} recuerdos de la memoria a largo plazo.")
            return memories
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo cargar la memoria desde la DB: {e}")
            return []

    def log_conversation(self, user_input: str, bot_output: list):
        """Registra una interacción completa como un evento estructurado."""
        event_content = json.dumps({'user': user_input, 'bot': bot_output})
        meta = {'type': 'event', 'event_type': 'conversation'}
        self.add_memory(event_content, meta=meta, long_term=False)

    def get_instance_id(self) -> str:
        """Devuelve el identificador único de esta instancia de MemoryStore."""
        return self._instance_id

    def add_memory(self, content: str, meta: Optional[Dict] = None, long_term: bool = False) -> Dict:
        """Añade un recuerdo a la memoria. Si es a largo plazo, lo persiste en la DB."""
        item = {
            'id': str(uuid.uuid4()),
            'content': content,
            'meta': meta or {},
            'timestamp': time.time()
        }
        if long_term:
            self.long_term.append(item)
            self._add_to_db(item)
        else:
            self.short_term.append(item)
        self._update_lru(content, item)
        return item

    def _add_to_db(self, item: Dict):
        """(Privado) Añade un item a la base de datos."""
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO long_term_memory (id, content, meta, timestamp) VALUES (?, ?, ?, ?)",
                         (item['id'], item['content'], json.dumps(item['meta']), item['timestamp']))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo añadir el recuerdo a la DB: {e}")

    def delete_memory(self, memory_id: str) -> bool:
        """Elimina un recuerdo por su ID, tanto en RAM como en la DB si es de largo plazo."""
        # Buscar y eliminar en memoria a largo plazo
        initial_len = len(self.long_term)
        self.long_term = [m for m in self.long_term if m.get('id') != memory_id]
        if len(self.long_term) != initial_len:
            self._delete_from_db(memory_id)
            return True

        # Buscar y eliminar en memoria a corto plazo
        initial_len = len(self.short_term)
        self.short_term = collections.deque(
            (m for m in self.short_term if m.get('id') != memory_id),
            maxlen=self.short_term.maxlen
        )
        return len(self.short_term) != initial_len

    def _delete_from_db(self, memory_id: str):
        """(Privado) Elimina un item de la base de datos por su ID."""
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM long_term_memory WHERE id = ?", (memory_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo borrar el recuerdo de la DB: {e}")

    def _update_lru(self, key: str, value: Any):
        self.lru_cache[key] = value
        self.lru_cache.move_to_end(key)
        if len(self.lru_cache) > self.lru_cache_size:
            self.lru_cache.popitem(last=False)

    def get_memory(self, query: str) -> List[Dict]:
        """Busca un recuerdo en la memoria a corto y largo plazo por contenido."""
        results = [m for m in list(self.short_term) + self.long_term if query in m['content']]
        for r in results:
            self._update_lru(r['content'], r)
        return results

    def clear_long_term(self):
        """Elimina todos los recuerdos de la memoria a largo plazo, tanto en RAM como en DB."""
        self.long_term.clear()
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM long_term_memory")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo limpiar la memoria a largo plazo de la DB: {e}")

    def close_db(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            self.conn = None
