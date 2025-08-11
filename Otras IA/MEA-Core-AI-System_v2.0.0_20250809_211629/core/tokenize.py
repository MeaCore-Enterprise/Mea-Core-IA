import re
from typing import List

_WORD_RE = re.compile(r"[a-záéíóúñü0-9']+", re.IGNORECASE)

def tokenize(text: str) -> List[str]:
    """Simple tokenization for Spanish and English text"""
    text = text.lower()
    return _WORD_RE.findall(text)
