import uuid
import chromadb


class VectorMemory:
    """
    Memoria vectorial usando ChromaDB para búsqueda semántica.
    """
    def __init__(self, persist_directory="./data/chroma_db"):
        print("[Memory] Initializing Vector Database...")
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="mea_memory")

    def add_memory(self, content: str, metadata: dict = None) -> str:
        """Agrega un recuerdo a la memoria vectorial."""
        mem_id = str(uuid.uuid4())
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[mem_id]
        )
        return mem_id

    def search_memory(self, query: str, n_results: int = 3) -> list:
        """Busca recuerdos similares."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        if results and results.get("documents"):
            return results["documents"][0]
        return []

    def get_all_memories(self, limit: int = 100) -> list:
        """Retorna todos los recuerdos."""
        try:
            results = self.collection.get(limit=limit)
            return results.get("documents", [])
        except:
            return []

    def count_memories(self) -> int:
        """Cantidad de recuerdos."""
        try:
            return self.collection.count()
        except:
            return 0

    def reset(self):
        """Limpia toda la memoria."""
        try:
            self.client.delete_collection("mea_memory")
            self.collection = self.client.get_or_create_collection(name="mea_memory")
            print("[Memory] Wiped clean.")
        except Exception as e:
            print(f"[Memory] Failed to reset: {e}")