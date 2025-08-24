
# MemoryStore: Memoria inteligente con consolidación, LRU y separación corto/largo plazo
import collections
import time
import uuid
from typing import Any, Dict, List, Tuple

class MemoryStore:
    """Gestiona la memoria de la IA, separada en corto y largo plazo.

    Utiliza una cola para la memoria a corto plazo (recuerdos recientes),
    una lista para la memoria a largo plazo y un diccionario ordenado como
    caché LRU (Least Recently Used) para un acceso rápido a los recuerdos
    consultados recientemente.
    """
    def __init__(self, short_term_limit=100, long_term_limit=1000, lru_cache_size=50):
        """Inicializa los distintos niveles de memoria.

        Args:
            short_term_limit (int): Número máximo de recuerdos en la memoria a corto plazo.
            long_term_limit (int): Límite (actualmente no implementado) para la memoria a largo plazo.
            lru_cache_size (int): Número máximo de elementos en la caché LRU.
        """
        self.short_term = collections.deque(maxlen=short_term_limit)
        self.long_term = []
        self.lru_cache = collections.OrderedDict()
        self.lru_cache_size = lru_cache_size
        self._instance_id = str(uuid.uuid4())

    def log_conversation(self, user_input: str, bot_output: list):
        """Registra una interacción completa (usuario y bot) en la memoria a corto plazo.

        Args:
            user_input (str): La entrada del usuario.
            bot_output (list): La respuesta del bot (como lista de cadenas).
        """
        self.add_memory(f"User: {user_input}", long_term=False)
        self.add_memory(f"Bot: {' | '.join(bot_output)}", long_term=False)

    def get_instance_id(self) -> str:
        """Devuelve el identificador único de esta instancia de MemoryStore."""
        return self._instance_id

    def add_memory(self, content: str, meta: Dict = None, long_term: bool = False) -> Dict:
        """Añade un recuerdo a la memoria a corto o largo plazo.

        Args:
            content (str): El contenido del recuerdo.
            meta (Dict, optional): Metadatos asociados al recuerdo. Defaults to None.
            long_term (bool, optional): Si es True, lo guarda en memoria a largo plazo.
                                      Defaults to False (corto plazo).
        
        Returns:
            Dict: El item de memoria creado, incluyendo su nuevo ID.
        """
        item = {
            'id': str(uuid.uuid4()),
            'content': content,
            'meta': meta or {},
            'timestamp': time.time()
        }
        if long_term:
            self.long_term.append(item)
        else:
            self.short_term.append(item)
        self._update_lru(content, item)
        return item

    def delete_memory(self, memory_id: str) -> bool:
        """Elimina un recuerdo específico de la memoria por su ID.

        Busca tanto en la memoria a corto como a largo plazo.

        Args:
            memory_id (str): El ID único del recuerdo a eliminar.

        Returns:
            bool: True si el recuerdo fue encontrado y eliminado, False en caso contrario.
        """
        # Buscar y eliminar en memoria a largo plazo
        initial_len = len(self.long_term)
        self.long_term = [m for m in self.long_term if m.get('id') != memory_id]
        if len(self.long_term) != initial_len:
            return True

        # Buscar y eliminar en memoria a corto plazo
        initial_len = len(self.short_term)
        self.short_term = collections.deque(
            (m for m in self.short_term if m.get('id') != memory_id),
            maxlen=self.short_term.maxlen
        )
        if len(self.short_term) != initial_len:
            return True

        return False

    def _update_lru(self, key: str, value: Any):
        """(Privado) Actualiza la caché LRU con el último elemento accedido."""
        self.lru_cache[key] = value
        self.lru_cache.move_to_end(key)
        if len(self.lru_cache) > self.lru_cache_size:
            self.lru_cache.popitem(last=False)

    def get_memory(self, query: str) -> List[Dict]:
        """Busca un recuerdo en la memoria a corto y largo plazo por contenido.

        Args:
            query (str): El texto a buscar dentro del contenido de los recuerdos.

        Returns:
            List[Dict]: Una lista de recuerdos que coinciden con la búsqueda.
        """
        # Búsqueda simple por substring
        results = [m for m in list(self.short_term) + self.long_term if query in m['content']]
        for r in results:
            self._update_lru(r['content'], r)
        return results

    def summarize(self, max_points=5) -> List[str]:
        """Genera un resumen simple de los recuerdos más recientes.

        Args:
            max_points (int, optional): Número máximo de puntos a incluir en el resumen. Defaults to 5.

        Returns:
            List[str]: Una lista de cadenas, cada una un punto clave del resumen.
        """
        all_mem = list(self.short_term) + self.long_term
        return [m['content'][:100] for m in all_mem[:max_points]]

    def clear_short_term(self):
        """Elimina todos los recuerdos de la memoria a corto plazo."""
        self.short_term.clear()

    def clear_long_term(self):
        """Elimina todos los recuerdos de la memoria a largo plazo."""
        self.long_term.clear()
