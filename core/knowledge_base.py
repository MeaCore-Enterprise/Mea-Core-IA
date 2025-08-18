# KnowledgeBase: BM25F, Word2Vec y búsqueda semántica local
from rank_bm25 import BM25Okapi
from gensim.models import Word2Vec
from typing import List, Dict
import numpy as np


class KnowledgeBase:
    def __init__(self, documents: List[str]):
        self.documents = documents
        self.tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = None
        self.w2v = None
        if self.tokenized_docs:
            self.bm25 = BM25Okapi(self.tokenized_docs)
            self._train_word2vec()

    def _train_word2vec(self):
        self.w2v = Word2Vec(self.tokenized_docs, vector_size=50, window=5, min_count=1, workers=2)

    def bm25_search(self, query: str, top_n=5) -> List[str]:
        if not self.bm25:
            return []
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        ranked = np.argsort(scores)[::-1][:top_n]
        return [self.documents[i] for i in ranked]

    def semantic_search(self, query: str, top_n=5) -> List[str]:
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
        self.documents.append(doc)
        self.tokenized_docs.append(doc.split())
        if self.tokenized_docs:
            self.bm25 = BM25Okapi(self.tokenized_docs)
            self._train_word2vec()
