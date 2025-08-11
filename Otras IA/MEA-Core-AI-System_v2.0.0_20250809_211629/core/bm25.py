import math
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
from .tokenize import tokenize

class BM25Index:
    """BM25 ranking function implementation for document retrieval"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.N = 0
        self.avgdl = 0.0
        self.df: Dict[str, int] = defaultdict(int)
        self.postings: Dict[str, List[Tuple[int, int]]] = defaultdict(list)  # term -> [(doc_id, tf)]
        self.doc_len: Dict[int, int] = {}  # doc_id -> length (in terms)
        self.docs: Dict[int, Dict] = {}    # doc_id -> {title, meta}

    def add_document(self, doc_id: int, text: str, meta: Dict = None):
        """Add a document to the index"""
        terms = tokenize(text)
        self.doc_len[doc_id] = len(terms)
        self.docs[doc_id] = meta if meta is not None else {}
        tf = Counter(terms)
        for term, c in tf.items():
            self.postings[term].append((doc_id, c))
        for term in tf.keys():
            self.df[term] += 1
        self.N += 1
        self.avgdl = (sum(self.doc_len.values()) / self.N) if self.N else 0.0

    def idf(self, term: str) -> float:
        """Calculate IDF score with smoothing"""
        df = self.df.get(term, 0)
        return math.log((self.N - df + 0.5) / (df + 0.5) + 1.0)

    def score(self, query_terms: List[str]) -> List[Tuple[int, float]]:
        """Score documents using BM25 algorithm"""
        scores: Dict[int, float] = defaultdict(float)
        q_tf = Counter(query_terms)
        for term in q_tf.keys():
            if term not in self.postings:
                continue
            idf = self.idf(term)
            for doc_id, f in self.postings[term]:
                dl = self.doc_len.get(doc_id, 0) or 1
                denom = f + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1))
                s = idf * (f * (self.k1 + 1)) / denom
                scores[doc_id] += s
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked
