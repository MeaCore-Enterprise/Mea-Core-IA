import sqlite3
import time
import os
import uuid
import json
import collections
from typing import Optional, Dict, List, Any

from core.gestor_configuracion import SettingsManager
from core.consolidador_memoria import MemoryConsolidator

class MemoryStore:
    """
    Gestiona la memoria de la IA, unificando la persistencia en SQLite,
    memoria por niveles (corto y largo plazo), olvido selectivo y consolidación.
    """
    def __init__(self, settings_manager: Optional[SettingsManager] = None, short_term_limit=100, lru_cache_size=50) -> None:
        """
        Inicializa la conexión a la base de datos, los niveles de memoria y el consolidador.
        """
        if settings_manager:
            db_path = settings_manager.get_setting("database.memory_db_path", "data/mea_memory.db")
        else:
            db_path = "data/mea_memory.db"

        self.short_term = collections.deque(maxlen=short_term_limit)
        self.lru_cache = collections.OrderedDict()
        self.lru_cache_size = lru_cache_size
        self.memory_consolidator = MemoryConsolidator()

        if db_path != ":memory:":
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self.long_term: List[Dict] = self._load_from_db()

    def _init_db(self) -> None:
        """Crea las tablas de la base de datos y actualiza el esquema si es necesario."""
        sql_kv = "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT, updated_at REAL)"
        sql_conversations = "CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY, timestamp REAL, user_input TEXT, bot_output TEXT)"
        sql_instance = "CREATE TABLE IF NOT EXISTS instance (key TEXT PRIMARY KEY, value TEXT)"
        sql_replications = "CREATE TABLE IF NOT EXISTS replications (id TEXT PRIMARY KEY, path TEXT NOT NULL, created_at REAL)"
        sql_episodic = ("CREATE TABLE IF NOT EXISTS episodic_memory ("
                        "id TEXT PRIMARY KEY, timestamp REAL NOT NULL, type TEXT NOT NULL, "
                        "source TEXT NOT NULL, data TEXT NOT NULL, "
                        "access_count INTEGER NOT NULL DEFAULT 0)")

        self.conn.execute(sql_kv)
        self.conn.execute(sql_conversations)
        self.conn.execute(sql_instance)
        self.conn.execute(sql_replications)
        self.conn.execute(sql_episodic)
        self._update_db_schema()
        self.conn.commit()

    def _update_db_schema(self):
        """Añade la columna access_count a la tabla episodic_memory si no existe."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(episodic_memory)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'access_count' not in columns:
                cursor.execute("ALTER TABLE episodic_memory ADD COLUMN access_count INTEGER NOT NULL DEFAULT 0")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo actualizar el esquema de la DB: {e}")

    def _load_from_db(self) -> List[Dict]:
        """Carga todos los recuerdos episódicos de largo plazo desde la DB."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, timestamp, type, source, data, access_count FROM episodic_memory ORDER BY timestamp ASC")
            rows = cursor.fetchall()
            memories = []
            for row in rows:
                memories.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'type': row[2],
                    'source': row[3],
                    'data': json.loads(row[4]),
                    'access_count': row[5]
                })
            return memories
        except (sqlite3.Error, json.JSONDecodeError) as e:
            print(f"[ERROR] No se pudo cargar la memoria desde la DB: {e}")
            return []

    def get_instance_id(self) -> str:
        """Obtiene el ID único de esta instancia de MEA, creándolo si no existe."""
        cursor = self.conn.execute("SELECT value FROM instance WHERE key = 'instance_id'")
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            instance_id = str(uuid.uuid4())
            self.conn.execute("INSERT INTO instance (key, value) VALUES (?, ?)", ('instance_id', instance_id))
            self.conn.commit()
            return instance_id

    def log_episode(self, type: str, source: str, data: Dict[str, Any], long_term: bool = True) -> Dict:
        """Registra un evento estructurado (episodio) en la memoria."""
        item = {
            'id': str(uuid.uuid4()),
            'timestamp': time.time(),
            'type': type,
            'source': source,
            'data': data,
            'access_count': 0
        }
        if long_term:
            self.long_term.append(item)
            self._add_episode_to_db(item)
        else:
            self.short_term.append(item)
        self._update_lru(item['id'], item)
        return item

    def _add_episode_to_db(self, item: Dict):
        """Añade un episodio a la base de datos."""
        try:
            data_json = json.dumps(item['data'])
            self.conn.execute(
                "INSERT INTO episodic_memory (id, timestamp, type, source, data, access_count) VALUES (?, ?, ?, ?, ?, ?)",
                (item['id'], item['timestamp'], item['type'], item['source'], data_json, item['access_count'])
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo añadir el episodio a la DB: {e}")

    def get_memory(self, query: str, context: Optional[List[str]] = None, top_n: int = 5) -> List[Dict]:
        """Busca recuerdos relevantes en la memoria episódica a largo plazo."""
        all_memories = list(self.short_term) + self.long_term
        scored_memories = []

        context_tokens = set()
        if context:
            for item in context:
                context_tokens.update(item.lower().split())

        for mem in all_memories:
            score = 0
            mem_content_lower = json.dumps(mem['data']).lower()
            
            if query.lower() in mem_content_lower:
                score += 2

            if context_tokens:
                mem_tokens = set(mem_content_lower.split())
                score += len(context_tokens.intersection(mem_tokens))

            if score > 0:
                scored_memories.append((mem, score))

        scored_memories.sort(key=lambda x: x[1], reverse=True)
        results = [mem for mem, score in scored_memories[:top_n]]

        for r in results:
            self._update_lru(r['id'], r)
            if r in self.long_term:
                r['access_count'] += 1
                self._increment_access_count_in_db(r['id'])
        
        return results

    def _increment_access_count_in_db(self, memory_id: str):
        """Incrementa el contador de acceso para un recuerdo en la DB."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE episodic_memory SET access_count = access_count + 1 WHERE id = ?", (memory_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo actualizar el contador de acceso en la DB: {e}")

    def forget_least_relevant(self, n_items: int = 1):
        """Olvida los 'n' recuerdos de largo plazo menos accedidos."""
        if not self.long_term or len(self.long_term) < n_items:
            return
        sorted_memory = sorted(self.long_term, key=lambda item: item.get('access_count', 0))
        items_to_forget = sorted_memory[:n_items]
        for item in items_to_forget:
            self.delete_episode(item['id'])

    def _delete_from_db(self, memory_id: str):
        """Elimina un recuerdo de la tabla episodic_memory."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM episodic_memory WHERE id = ?", (memory_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[ERROR] No se pudo borrar el recuerdo de la DB: {e}")

    def delete_episode(self, episode_id: str) -> bool:
        """
        Elimina un episodio específico de la memoria a largo plazo por su ID.
        """
        initial_len = len(self.long_term)
        self.long_term = [mem for mem in self.long_term if mem.get('id') != episode_id]
        if len(self.long_term) < initial_len:
            self._delete_from_db(episode_id)
            if episode_id in self.lru_cache:
                del self.lru_cache[episode_id]
            return True
        return False

    def _update_lru(self, key: str, value: Any):
        """Actualiza la caché LRU."""
        self.lru_cache[key] = value
        self.lru_cache.move_to_end(key)
        if len(self.lru_cache) > self.lru_cache_size:
            self.lru_cache.popitem(last=False)

    def clear_all_memory_for_testing(self):
        """Limpia toda la memoria para las pruebas."""
        with self.conn:
            self.conn.execute("DELETE FROM kv")
            self.conn.execute("DELETE FROM conversations")
            self.conn.execute("DELETE FROM episodic_memory")
            self.conn.execute("DELETE FROM instance")
            self.conn.execute("DELETE FROM replications")
        self.long_term.clear()
        self.short_term.clear()
        self.lru_cache.clear()

    def close_db(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            self.conn = None