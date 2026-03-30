import uuid
import chromadb

class VectorMemory:
    """
    Manages semantic memories using ChromaDB for fast similarity search.
    """
    def __init__(self, persist_directory="./data/chroma_db"):
        print("[Memory] Initializing Vector Database...")
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="mea_memory")

    def add_memory(self, content, metadata=None):
        mem_id = str(uuid.uuid4())
        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[mem_id]
        )
        return mem_id

    def search_memory(self, query, n_results=3):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        if results and results.get("documents"):
            return results["documents"][0]
        return []

    def reset(self):
        try:
            self.client.delete_collection("mea_memory")
            self.collection = self.client.get_or_create_collection(name="mea_memory")
            print("[Memory] Wiped clean.")
        except Exception as e:
            print(f"[Memory] Failed to reset: {e}")
