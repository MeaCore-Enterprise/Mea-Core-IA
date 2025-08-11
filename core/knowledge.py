import sqlite3
import os
from typing import List, Tuple

DB_PATH = "data/knowledge_base.db"

class KnowledgeBase:
    """
    Gestiona la base de datos de conocimiento (principios, hechos, etc.).
    """
    def __init__(self, path: str = DB_PATH):
        if path != ":memory:":
            os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS principles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_document TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL UNIQUE
        )""")
        self.conn.commit()

    def add_principle(self, source: str, category: str, content: str) -> None:
        """Añade un nuevo principio a la base de datos, evitando duplicados."""
        try:
            self.conn.execute(
                "INSERT INTO principles (source_document, category, content) VALUES (?, ?, ?)",
                (source, category, content)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            # El principio ya existe, no hacemos nada.
            pass

    def get_principles_by_category(self, category: str) -> List[Tuple[str, str, str]]:
        """Busca principios que coincidan parcialmente con una categoría."""
        cursor = self.conn.execute(
            "SELECT source_document, category, content FROM principles WHERE category LIKE ?",
            (f'%{category}%',)
        )
        return cursor.fetchall()

    def get_all_principles(self) -> List[Tuple[str, str, str]]:
        """Devuelve todos los principios de la base de datos."""
        cursor = self.conn.execute("SELECT source_document, category, content FROM principles")
        return cursor.fetchall()