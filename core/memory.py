
import sqlite3
import time
from typing import Optional, Dict

DB_PATH: str = "data/mea_memory.db"


class MemoryStore:
    def __init__(self, path: str = DB_PATH) -> None:
        self.conn: sqlite3.Connection = sqlite3.connect(path, check_same_thread=False)
        self._init_tables()

    def _init_tables(self) -> None:
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS kv (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at REAL
        )""")
        self.conn.commit()

    def set(self, key: str, value: str) -> None:
        now: float = time.time()
        self.conn.execute("""
        INSERT INTO kv(key, value, updated_at) VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """, (key, value, now))
        self.conn.commit()

    def get(self, key: str) -> Optional[str]:
        cur = self.conn.execute("SELECT value FROM kv WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else None

    def dump_all(self) -> Dict[str, str]:
        cur = self.conn.execute("SELECT key, value FROM kv")
        return {k: v for k, v in cur.fetchall()}
