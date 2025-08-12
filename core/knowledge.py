import sqlite3
import os
import re
from typing import List, Tuple

# Intentar importar rank_bm25, si no, se lanzará un error en el constructor
try:
    from rank_bm25 import BM25Okapi
    RANK_BM25_AVAILABLE = True
except ImportError:
    RANK_BM25_AVAILABLE = False

DB_PATH = "data/knowledge_base.db"

# Lista simple de stopwords en español para mejorar la calidad de la búsqueda
SPANISH_STOPWORDS = set([
    'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'con', 'por', 'su', 'para', 'como', 'no', 'un', 'una',
    'o', 'este', 'esta', 'estos', 'estas', 'ser', 'es', 'son', 'debe', 'deben', 'al', 'lo', 'las', 'sus', 'ese',
    'esos', 'esa', 'esas', 'si', 'porque', 'cuando', 'donde', 'quien', 'cual', 'cuales', 'muy', 'sin', 'sobre',
    'también', 'hasta', 'hay', 'desde', 'todo', 'todos', 'toda', 'todas', 'otro', 'otra', 'otros', 'otras', 'pero'
])

def tokenize(text: str) -> List[str]:
    """Convierte texto a una lista de tokens limpios y sin stopwords."""
    # Quitar puntuación y convertir a minúsculas
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Separar por espacios y filtrar stopwords
    return [word for word in text.split() if word not in SPANISH_STOPWORDS]

class KnowledgeBase:
    """
    Gestiona la base de datos de conocimiento y proporciona búsqueda semántica.
    """
    def __init__(self, path: str = DB_PATH):
        if not RANK_BM25_AVAILABLE:
            raise ImportError("La librería 'rank-bm25' no está instalada. Por favor, ejecute 'pip install rank-bm25'")

        if path != ":memory:":
            os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path)
        self._init_db()
        
        self.principles: List[Tuple[str, str, str]] = self.get_all_principles()
        self._build_index()

    def _build_index(self):
        """(Re)construye el índice de búsqueda a partir de los principios en memoria."""
        if self.principles:
            corpus = [p[2] for p in self.principles]
            tokenized_corpus = [tokenize(doc) for doc in corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
        else:
            self.bm25 = None

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
        """Añade un nuevo principio a la base de datos y reconstruye el índice."""
        try:
            self.conn.execute(
                "INSERT INTO principles (source_document, category, content) VALUES (?, ?, ?)",
                (source, category, content)
            )
            self.conn.commit()
            # Actualizar los principios en memoria y reconstruir el índice
            self.principles = self.get_all_principles()
            self._build_index()
        except sqlite3.IntegrityError:
            pass

    def get_principles_by_category(self, category: str) -> List[Tuple[str, str, str]]:
        cursor = self.conn.execute(
            "SELECT source_document, category, content FROM principles WHERE category LIKE ?",
            (f'%{category}%',)
        )
        return cursor.fetchall()

    def get_all_principles(self) -> List[Tuple[str, str, str]]:
        cursor = self.conn.execute("SELECT source_document, category, content FROM principles")
        return cursor.fetchall()

    def search(self, query: str, top_n: int = 3) -> List[Tuple[str, str, str]]:
        """
        Busca los principios más relevantes para una consulta usando BM25.
        """
        if not self.bm25:
            return []
        
        tokenized_query = tokenize(query)
        doc_scores = self.bm25.get_scores(tokenized_query)
        
        top_indexes = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_n]
        
        top_principles = [self.principles[i] for i in top_indexes if doc_scores[i] > 0]
        
        return top_principles