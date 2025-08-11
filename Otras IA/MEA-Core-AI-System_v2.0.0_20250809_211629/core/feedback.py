from collections import Counter
from typing import List, Dict
from .tokenize import tokenize

class QueryLearner:
    """Implements Rocchio feedback and pseudo-relevance feedback for query expansion"""
    
    def __init__(self, alpha=1.0, beta=0.75, gamma=0.15, top_terms=5):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.top_terms = top_terms
        self.term_weights: Dict[str, float] = {}  # Global term weight accumulator

    def expand_with_prf(self, top_docs: List[str]) -> List[str]:
        """Expand query using pseudo-relevance feedback"""
        counts = Counter()
        for text in top_docs:
            counts.update(tokenize(text))
        best = [t for t,_ in counts.most_common(self.top_terms)]
        return best

    def apply_feedback(self, query_terms: List[str], pos_docs: List[str], neg_docs: List[str]) -> Dict[str, float]:
        """Apply Rocchio feedback algorithm"""
        q = Counter(query_terms)
        pos = Counter()
        for d in pos_docs: 
            pos.update(tokenize(d))
        neg = Counter()
        for d in neg_docs: 
            neg.update(tokenize(d))
        
        # Normalize term frequencies
        def norm(counter):
            total = sum(counter.values()) or 1
            return {t: c/total for t,c in counter.items()}
        
        w = {}
        for t,v in norm(q).items(): 
            w[t] = w.get(t,0) + self.alpha*v
        for t,v in norm(pos).items(): 
            w[t] = w.get(t,0) + self.beta*v
        for t,v in norm(neg).items(): 
            w[t] = w.get(t,0) - self.gamma*v
        
        # Accumulate global weights
        for t,v in w.items():
            self.term_weights[t] = self.term_weights.get(t, 0.0) + v
        return self.term_weights

    def rerank_terms(self, terms: List[str]) -> List[str]:
        """Rerank terms based on learned weights"""
        return sorted(terms, key=lambda t: self.term_weights.get(t, 0.0), reverse=True)
