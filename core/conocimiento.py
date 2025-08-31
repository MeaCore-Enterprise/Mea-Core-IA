import os
import re
import networkx as nx
import matplotlib.pyplot as plt
import sys
from typing import List, Tuple, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Importar el modelo y la base desde los módulos centralizados
from . import models

# Intentar importar rank-bm25
try:
    from rank_bm25 import BM25Okapi
    RANK_BM25_AVAILABLE = True
except ImportError:
    RANK_BM25_AVAILABLE = False

# --- Clase KnowledgeManager Refactorizada ---

class KnowledgeManager:
    """
    Gestiona la base de conocimiento, usando SQLAlchemy para hechos y NetworkX para relaciones.
    """

    def __init__(self, db_session: Session, graph_path="data/knowledge_graph.gml"):
        """Inicializa el grafo, el motor de búsqueda y construye el índice inicial."""
        self.graph_path = graph_path
        self._load_graph()

        self.corpus: List[str] = []
        self.bm25: Optional[BM25Okapi] = None
        if RANK_BM25_AVAILABLE:
            self._build_search_index(db_session)
        else:
            print("[Advertencia] rank_bm25 no está instalado. La búsqueda de conocimiento será básica.")

    def _load_graph(self):
        """Carga el grafo de conocimiento desde un archivo GML si existe."""
        if os.path.exists(self.graph_path):
            self.graph = nx.read_gml(self.graph_path)
        else:
            self.graph = nx.DiGraph()

    def _build_search_index(self, db: Session):
        """Construye o reconstruye el índice de búsqueda BM25 a partir de los hechos en la DB."""
        if not RANK_BM25_AVAILABLE:
            return
        
        facts = db.query(models.Fact).all()
        self.corpus = [fact.content for fact in facts]
        
        if self.corpus:
            tokenized_corpus = [doc.lower().split() for doc in self.corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
            print(f"[KnowledgeManager] Índice de búsqueda construido con {len(self.corpus)} hechos.")
        else:
            self.bm25 = None

    def add_fact(self, db: Session, fact_text: str):
        """
        Añade un hecho a la DB, actualiza el grafo y reconstruye el índice de búsqueda.
        """
        new_fact = models.Fact(content=fact_text)
        db.add(new_fact)
        try:
            db.commit()
            db.refresh(new_fact)
        except IntegrityError:
            db.rollback()
            return  # El hecho ya existe

        # Reconstruir el índice para incluir el nuevo hecho
        self._build_search_index(db)

        # Lógica del grafo no cambia
        # ...

    def query(self, db: Session, topic: str, top_n: int = 5) -> Dict[str, List[Any]]:
        """
        Consulta un tema utilizando BM25 para los hechos y búsqueda directa para relaciones.
        """
        results: Dict[str, List[Any]] = {
            'ranked_facts': [],
            'relations': []
        }

        # 1. Buscar hechos relevantes con BM25
        if self.bm25 and self.corpus:
            tokenized_query = topic.lower().split()
            doc_scores = self.bm25.get_scores(tokenized_query)
            
            scored_docs = [(self.corpus[i], doc_scores[i]) for i in range(len(self.corpus)) if doc_scores[i] > 0]
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            top_docs = scored_docs[:top_n]

            if top_docs:
                max_score = top_docs[0][1]
                if max_score > 0:
                    results['ranked_facts'] = [(doc, score / max_score) for doc, score in top_docs]

        # Fallback a LIKE si BM25 no está disponible o no da resultados
        if not results['ranked_facts']:
            facts = db.query(models.Fact).filter(models.Fact.content.like(f'%{topic}%')).limit(top_n).all()
            results['ranked_facts'] = [(fact.content, 0.5) for fact in facts]

        # 2. Lógica del grafo no cambia
        # ...
        
        return results

    def save_graph(self):
        """Guarda el estado del grafo de conocimiento en el archivo GML."""
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        nx.write_gml(self.graph, self.graph_path)
        print(f"[KnowledgeManager] Grafo guardado en {self.graph_path}")

    # El resto de métodos del grafo (add_relation, visualize_graph) no necesitan cambios significativos
    # ya que no interactúan con la base de datos de hechos.