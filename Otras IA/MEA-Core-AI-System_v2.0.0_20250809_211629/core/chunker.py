from typing import List, Dict
import re

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using punctuation markers"""
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p]

def make_chunks(text: str, target_chars: int = 1200, overlap_chars: int = 200) -> List[Dict]:
    """Create overlapping text chunks for better retrieval"""
    sents = split_into_sentences(text)
    chunks, buf = [], ""
    for s in sents:
        if len(buf) + len(s) + 1 <= target_chars:
            buf = (buf + " " + s).strip()
        else:
            if buf:
                chunks.append(buf)
            # Create overlap with previous chunk
            tail = buf[-overlap_chars:] if len(buf) > overlap_chars else buf
            buf = (tail + " " + s).strip()
    if buf:
        chunks.append(buf)
    return [{"text": c} for c in chunks]
