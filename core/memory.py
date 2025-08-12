

import sqlite3
import time
import os
import uuid
from typing import Optional, Dict, List, Any

DB_PATH: str = "data/mea_memory.db"

class MemoryStore:
    def __init__(self, path: str = DB_PATH) -> None:
        if path != ":memory:":
            os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(path, check_same_thread=False)
        self._init_tables()

    def _init_tables(self) -> None:
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT, updated_at REAL)
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY, timestamp REAL, user_input TEXT, bot_output TEXT)
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS instance (key TEXT PRIMARY KEY, value TEXT)
        """)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS replications (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            created_at REAL
        )""")
        self.conn.commit()

    def get_instance_id(self) -> str:
        cursor = self.conn.execute("SELECT value FROM instance WHERE key = 'instance_id'")
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            instance_id = str(uuid.uuid4())
            self.conn.execute("INSERT INTO instance (key, value) VALUES (?, ?)", ('instance_id', instance_id))
            self.conn.commit()
            return instance_id

    def log_replication(self, clone_id: str, path: str) -> None:
        self.conn.execute(
            "INSERT INTO replications (id, path, created_at) VALUES (?, ?, ?)",
            (clone_id, path, time.time())
        )
        self.conn.commit()

    def set(self, key: str, value: str) -> None:
        now: float = time.time()
        self.conn.execute("INSERT INTO kv(key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at", (key, value, now))
        self.conn.commit()

    def get(self, key: str) -> Optional[str]:
        cur = self.conn.execute("SELECT value FROM kv WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else None

    def dump_all(self) -> Dict[str, str]:
        cur = self.conn.execute("SELECT key, value FROM kv")
        return {k: v for k, v in cur.fetchall()}

    def log_conversation(self, user_input: str, bot_output: List[str]) -> None:
        now: float = time.time()
        bot_output_str = "\n".join(bot_output)
        self.conn.execute("INSERT INTO conversations (timestamp, user_input, bot_output) VALUES (?, ?, ?)", (now, user_input, bot_output_str))
        self.conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        """Devuelve estadísticas sobre el contenido de la memoria."""
        kv_count = self.conn.execute("SELECT COUNT(*) FROM kv").fetchone()[0]
        conv_count = self.conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
        return {
            "key_value_pairs": kv_count,
            "conversations_logged": conv_count
        }
