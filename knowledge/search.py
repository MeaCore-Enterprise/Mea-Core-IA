"""
Knowledge Module - Web Search and RAG
Permite que el sistema busque información y amplíe su contexto.
"""
import os
import json
from typing import Dict, List, Optional


class WebSearch:
    """Búsqueda web integrada (usa DuckDuckGo/Exa)."""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("EXA_API_KEY")
        
    async def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Busca información en la web."""
        if not self.api_key:
            return self._mock_search(query, num_results)
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "query": query,
                "num_results": num_results,
                "type": "auto"
            }
            response = requests.post(
                "https://api.exa.ai/search",
                headers=headers,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("results", [])
        except Exception as e:
            print(f"[Search] Error: {e}")
        
        return self._mock_search(query, num_results)
    
    def _mock_search(self, query: str, num_results: int) -> List[Dict]:
        """Mock de búsqueda para desarrollo."""
        return [
            {
                "title": f"Resultado {i+1} para: {query}",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"Información relevante sobre {query}..."
            }
            for i in range(num_results)
        ]


class KnowledgeRAG:
    """RAG (Retrieval Augmented Generation) para conocimiento."""
    def __init__(self, vector_store=None, search: WebSearch = None):
        self.vector_store = vector_store
        self.search = search or WebSearch()
        self.knowledge_index = "knowledge_base"
        
    async def query(self, question: str, use_web: bool = True) -> Dict:
        """Responde una pregunta usando RAG + búsqueda web."""
        
        # 1. Buscar en memoria local
        local_results = self.vector_store.search_memory(question) if self.vector_store else []
        
        # 2. Buscar en web si es necesario
        web_results = []
        if use_web and (not local_results or len(local_results) < 2):
            web_results = await self.search.search(question, num_results=3)
            
            # Agregar a memoria local
            if self.vector_store and web_results:
                for result in web_results:
                    content = f"{result.get('title', '')}: {result.get('snippet', '')}"
                    self.vector_store.add_memory(
                        content,
                        metadata={"source": "web", "url": result.get("url")}
                    )
        
        return {
            "question": question,
            "local_results": local_results,
            "web_results": web_results,
            "context": self._build_context(local_results, web_results)
        }
    
    def _build_context(self, local: List, web: List) -> str:
        """Construye contexto para el LLM."""
        context_parts = []
        
        if local:
            context_parts.append("=== Memoria Local ===")
            context_parts.extend([f"- {r}" for r in local[:3]])
            
        if web:
            context_parts.append("\n=== Búsqueda Web ===")
            context_parts.extend([
                f"- {r.get('title', '')}: {r.get('snippet', '')}"
                for r in web[:3]
            ])
        
        return "\n".join(context_parts) if context_parts else "Sin contexto disponible."