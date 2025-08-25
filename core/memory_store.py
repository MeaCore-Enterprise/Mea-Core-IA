
import collections
import time
import uuid
import json
import sqlite3
import os
from typing import Any, Dict, List, Optional

class MemoryStore:
    """Gestiona la memoria de la IA, con persistencia en SQLite y olvido selectivo.

    Utiliza una cola para la memoria a corto plazo (en RAM), una lista para la
    memoria a largo plazo (sincronizada con una DB) que incluye un contador de
    acceso para determinar la relevancia, y una caché LRU.
    """
    def __init__(self, short_term_limit=100, lru_cache_size=50, db_path="data/memory.db"):
        """Inicializa los distintos niveles de memoria y la base de datos."""
        self.short_term = collections.deque(maxlen=short_term_limit)
        self.lru_cache = collections.OrderedDict()
        self.lru_cache_size = lru_cache_size
        self._instance_id = str(uuid.uuid4())
        self.db_path = db_path
        self.conn = None
        self._init_db()
        self.long_term = self._load_from_db()

    def _init_db(self):
        """(Privado) Inicializa la DB, crea la tabla y actualiza el esquema si es necesario."""
        try:
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
            self._update_db_schema()
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] Error en la base de datos: {e}")
            self.conn = None

    def _update_db_schema(self):
        """(Privado) Añade nuevas columnas a la tabla si no existen."""
        try:
            cursor = self.conn.cursor()
            # Comprobar si existe la columna access_count
            cursor.execute("PRAGMA table_info(long_term_memory)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'access_count' not in columns:
                print("[MemoryStore] Actualizando esquema de DB: añadiendo 'access_count'.")
                cursor.execute("ALTER TABLE long_term_memory ADD COLUMN access_count INTEGER NOT NULL DEFAULT 0")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo actualizar el esquema de la DB: {e}")

    def _load_from_db(self) -> List[Dict]:
        """(Privado) Carga todos los recuerdos de largo plazo desde la DB."""
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, content, meta, timestamp, access_count FROM long_term_memory ORDER BY timestamp ASC")
            rows = cursor.fetchall()
            memories = []
            for row in rows:
                memories.append({
                    'id': row[0],
                    'content': row[1],
                    'meta': json.loads(row[2]),
                    'timestamp': row[3],
                    'access_count': row[4]
                })
            print(f"[MemoryStore] Cargados {len(memories)} recuerdos de la memoria a largo plazo.")
            return memories
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo cargar la memoria desde la DB: {e}")
            return []

    def log_conversation(self, user_input: str, bot_output: list):
        event_content = json.dumps({'user': user_input, 'bot': bot_output})
        meta = {'type': 'event', 'event_type': 'conversation'}
        self.add_memory(event_content, meta=meta, long_term=False)

    def get_instance_id(self) -> str:
        return self._instance_id

    def add_memory(self, content: str, meta: Optional[Dict] = None, long_term: bool = False) -> Dict:
        """Añade un recuerdo. Si es a largo plazo, lo persiste en la DB."""
        item = {
            'id': str(uuid.uuid4()),
            'content': content,
            'meta': meta or {},
            'timestamp': time.time(),
            'access_count': 0
        }
        if long_term:
            self.long_term.append(item)
            self._add_to_db(item)
        else:
            self.short_term.append(item)
        self._update_lru(content, item)
        return item

    def _add_to_db(self, item: Dict):
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO long_term_memory (id, content, meta, timestamp, access_count) VALUES (?, ?, ?, ?, ?)",
                         (item['id'], item['content'], json.dumps(item['meta']), item['timestamp'], item['access_count']))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo añadir el recuerdo a la DB: {e}")

    def delete_memory(self, memory_id: str) -> bool:
        initial_len = len(self.long_term)
        self.long_term = [m for m in self.long_term if m.get('id') != memory_id]
        if len(self.long_term) != initial_len:
            self._delete_from_db(memory_id)
            return True
        initial_len = len(self.short_term)
        self.short_term = collections.deque(
            (m for m in self.short_term if m.get('id') != memory_id),
            maxlen=self.short_term.maxlen
        )
        return len(self.short_term) != initial_len

    def _delete_from_db(self, memory_id: str):
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
        """Busca un recuerdo y actualiza su contador de acceso si es de largo plazo."""
        results = [m for m in list(self.short_term) + self.long_term if query in m['content']]
        for r in results:
            self._update_lru(r['content'], r)
            # Si el recuerdo es de largo plazo, incrementar su contador de acceso
            if r in self.long_term:
                r['access_count'] += 1
                self._increment_access_count_in_db(r['id'])
        return results

    def _increment_access_count_in_db(self, memory_id: str):
        """(Privado) Incrementa el contador de acceso de un recuerdo en la DB."""
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE long_term_memory SET access_count = access_count + 1 WHERE id = ?", (memory_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo actualizar el contador de acceso en la DB: {e}")

    def forget_least_relevant(self, n_items: int = 1):
        """Encuentra y elimina los recuerdos menos relevantes de la memoria a largo plazo.

        La relevancia se mide por el contador de acceso (`access_count`).
        Los recuerdos con el contador más bajo se consideran menos relevantes.

        Args:
            n_items (int, optional): El número de recuerdos a olvidar. Defaults to 1.
        """
        if not self.long_term:
            return

        # Ordenar la memoria a largo plazo por el contador de acceso en orden ascendente
        sorted_memory = sorted(self.long_term, key=lambda item: item.get('access_count', 0))

        # Determinar los items a eliminar
        items_to_forget = sorted_memory[:n_items]

        if not items_to_forget:
            return

        print(f"[MemoryStore] Olvidando {len(items_to_forget)} recuerdo(s) menos relevante(s)...")
        for item in items_to_forget:
            self.delete_memory(item['id'])

    def clear_long_term(self):
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
        if self.conn:
            self.conn.close()
            self.conn = None
