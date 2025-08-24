# KnowledgeBase: BM25F, Word2Vec y búsqueda semántica local
from rank_bm25 import BM25Okapi
from gensim.models import Word2Vec
from typing import List, Dict
import numpy as np

class KnowledgeBase:
    """Gestiona una base de conocimiento en memoria para búsqueda de información.

    Esta clase almacena una colección de documentos y proporciona métodos para
    realizar búsquedas léxicas (BM25) y semánticas (Word2Vec) sobre ellos.
    """
    def __init__(self, documents: List[str]):
        """Inicializa la base de conocimiento con una lista de documentos.

        Args:
            documents (List[str]): Una lista de cadenas, donde cada cadena es un documento.
        """
        self.documents = documents
        self.tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = None
        self.w2v = None
        if self.tokenized_docs:
            self.bm25 = BM25Okapi(self.tokenized_docs)
            self._train_word2vec()

    def _train_word2vec(self):
        """(Privado) Entrena el modelo Word2Vec con los documentos tokenizados."""
        self.w2v = Word2Vec(self.tokenized_docs, vector_size=50, window=5, min_count=1, workers=2)

    def bm25_search(self, query: str, top_n=5) -> List[str]:
        """Realiza una búsqueda léxica usando el algoritmo BM25.

        Args:
            query (str): La consulta de búsqueda del usuario.
            top_n (int, optional): El número máximo de documentos a devolver. Defaults to 5.

        Returns:
            List[str]: Una lista de los documentos más relevantes según BM25.
        """
        if not self.bm25:
            return []
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        ranked = np.argsort(scores)[::-1][:top_n]
        return [self.documents[i] for i in ranked]

    def semantic_search(self, query: str, top_n=5) -> List[str]:
        """Realiza una búsqueda semántica usando vectores de Word2Vec.

        Calcula la similitud del coseno entre el vector de la consulta y el vector
        de cada documento.

        Args:
            query (str): La consulta de búsqueda del usuario.
            top_n (int, optional): El número máximo de documentos a devolver. Defaults to 5.

        Returns:
            List[str]: Una lista de los documentos más similares semánticamente.
        """
        if not self.w2v or not self.tokenized_docs:
            return []
        query_vecs = [self.w2v.wv[w] for w in query.split() if w in self.w2v.wv]
        if not query_vecs:
            return []
        query_vec = np.mean(query_vecs, axis=0)
        sims = []
        for i, doc in enumerate(self.tokenized_docs):
            doc_vecs = [self.w2v.wv[w] for w in doc if w in self.w2v.wv]
            if not doc_vecs:
                continue
            doc_vec = np.mean(doc_vecs, axis=0)
            sim = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec) + 1e-8)
            sims.append((i, sim))
        ranked = sorted(sims, key=lambda x: x[1], reverse=True)[:top_n]
        return [self.documents[i] for i, _ in ranked]

    def add_document(self, doc: str):
        """Añade un nuevo documento a la base de conocimiento y re-entrena los modelos.

        Args:
            doc (str): El nuevo documento a añadir.
        """
        self.documents.append(doc)
        self.tokenized_docs.append(doc.split())
        if self.tokenized_docs:
            # Re-inicializa y re-entrena los modelos con el nuevo documento.
            self.bm25 = BM25Okapi(self.tokenized_docs)
            self._train_word2vec()
