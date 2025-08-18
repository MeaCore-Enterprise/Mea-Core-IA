
# MemoryStore: Memoria inteligente con consolidación, LRU y separación corto/largo plazo
import collections
import time
import uuid
from typing import Any, Dict, List, Tuple

class MemoryStore:
    def __init__(self, short_term_limit=100, long_term_limit=1000, lru_cache_size=50):
        self.short_term = collections.deque(maxlen=short_term_limit)
        self.long_term = []
        self.lru_cache = collections.OrderedDict()
        self.lru_cache_size = lru_cache_size
        self._instance_id = str(uuid.uuid4())

    def log_conversation(self, user_input: str, bot_output: list):
        # Guarda la conversación en memoria a largo plazo
        self.add_memory(f"User: {user_input}", long_term=False)
        self.add_memory(f"Bot: {' | '.join(bot_output)}", long_term=False)

    def get_instance_id(self):
        return self._instance_id

    def add_memory(self, content: str, meta: Dict = None, long_term: bool = False):
        item = {'content': content, 'meta': meta or {}, 'timestamp': time.time()}
        if long_term:
            self.long_term.append(item)
        else:
            self.short_term.append(item)
        self._update_lru(content, item)

    def _update_lru(self, key: str, value: Any):
        self.lru_cache[key] = value
        self.lru_cache.move_to_end(key)
        if len(self.lru_cache) > self.lru_cache_size:
            self.lru_cache.popitem(last=False)

    def get_memory(self, query: str) -> List[Dict]:
        # Búsqueda simple por substring
        results = [m for m in list(self.short_term) + self.long_term if query in m['content']]
        for r in results:
            self._update_lru(r['content'], r)
        return results

    def summarize(self, max_points=5) -> List[str]:
        # Resumir conversaciones largas en puntos clave (simple: primeras frases)
        all_mem = list(self.short_term) + self.long_term
        return [m['content'][:100] for m in all_mem[:max_points]]

    def clear_short_term(self):
        self.short_term.clear()

    def clear_long_term(self):
        self.long_term.clear()
