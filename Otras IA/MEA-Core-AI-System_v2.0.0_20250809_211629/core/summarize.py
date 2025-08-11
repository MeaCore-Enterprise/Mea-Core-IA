from typing import List
from .tokenize import tokenize

def score_sentence(sent: str, query_terms: List[str]) -> float:
    """Score sentence based on query term overlap"""
    terms = set(tokenize(sent))
    q = set(query_terms)
    overlap = len(terms & q)
    return overlap / (len(terms) or 1)

def summarize(texts: List[str], query_terms: List[str], max_sents: int = 4) -> str:
    """Create extractive summary from top chunks"""
    candidates = []
    for t in texts:
        for s in t.split(". "):
            if len(s.strip()) > 0:
                candidates.append((s.strip(), score_sentence(s, query_terms)))
    
    candidates.sort(key=lambda x: x[1], reverse=True)
    chosen = []
    seen = set()
    
    for s, _ in candidates:
        sig = s[:60]  # Avoid duplicate similar sentences
        if sig in seen: 
            continue
        seen.add(sig)
        chosen.append(s)
        if len(chosen) >= max_sents: 
            break
    
    return " ".join(chosen)
