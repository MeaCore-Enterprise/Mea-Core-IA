import json
import os
from typing import Dict, List, Iterator

def ensure_dir(path: str):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)

def iter_jsonl(path: str) -> Iterator[Dict]:
    """Iterate over JSONL file"""
    if not os.path.exists(path): 
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def append_jsonl(path: str, obj: Dict):
    """Append object to JSONL file"""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
