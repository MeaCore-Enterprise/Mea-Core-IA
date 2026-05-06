import asyncio
import os
from .memory import VectorMemory
from .node import SwarmNode

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("[Advertencia] llama-cpp-python no está instalado.")


class MeaAgent:
    """
    El cerebro de MEA V3. Maneja conexiones a la memoria, se coordina
    con el nodo P2P y ejecuta el modelo de lenguaje.
    Soporta LLM local (Llama.cpp) y LLM externo (Gemini API).
    """
    def __init__(self, node: SwarmNode, memory: VectorMemory, llm_client=None):
        self.node = node
        self.memory = memory
        self.llm_client = llm_client
        
        # Register Swarm Listeners
        self.node.on("memory_sync", self._handle_remote_memory)
        self.node.on("query_request", self._handle_query_request)

        # Configuración del LLM local
        self.llm = None
        run_mode = os.getenv("RUN_MODE", "hybrid")
        
        if run_mode == "local" and LLAMA_AVAILABLE:
            self._load_model()
        else:
            print(f"[Agent] Modo: {run_mode} (LLM externo disponible: {bool(llm_client)})")
            
    def _load_model(self):
        try:
            model_path = os.getenv("LLM_MODEL_PATH", "./models/model.gguf")
            print(f"[Agent] Cargando LLM local desde {model_path}...")
            self.llm = Llama(model_path=model_path, n_ctx=2048, n_threads=4, verbose=False)
            print("[Agent] LLM local cargado exitosamente.")
        except Exception as e:
            print(f"[Agent] Fallo al cargar LLM local: {e}")
            self.llm = None

    async def _handle_remote_memory(self, payload):
        content = payload.get("content", "")
        source = payload.get("source", "remote_node")
        print(f"[Agent] [SWARM] Recibiendo memoria de {source}: {content[:50]}...")
        self.memory.add_memory(content, metadata={"source": source})

    async def _handle_query_request(self, payload):
        query = payload.get("query")
        reply_to = payload.get("reply_to")
        print(f"[Agent] [SWARM] Solicitud de contexto para: {query}")
        results = self.memory.search_memory(query, n_results=1)
        if results:
            await self.node.broadcast("query_response", {
                "target": reply_to,
                "answer": results[0]
            })

    async def learn(self, fact: str, metadata: dict = None):
        """Aprende un hecho y lo sincroniza con el swarm."""
        print(f"[Agent] Aprendiendo: {fact[:50]}...")
        mem_metadata = metadata or {}
        mem_metadata["source"] = "local_user"
        
        self.memory.add_memory(fact, metadata=mem_metadata)
        await self.node.broadcast("memory_sync", {"content": fact, "source": "local_user"})

    async def process_input(self, text: str, context: str = None) -> str:
        """Procesa un input del usuario."""
        print(f"[Agent] Procesando: {text[:50]}...")
        
        # 1. Buscar en memoria vectorial
        memories = self.memory.search_memory(text, n_results=3)
        memory_context = " | ".join(memories) if memories else ""
        
        # 2. Combinar contextos
        full_context = context or memory_context
        
        # 3. Determinar qué LLM usar
        if self.llm_client:
            # Usar Gemini API
            response = await self._generate_with_api(text, full_context)
        elif self.llm:
            # Usar LLM local
            response = await self._generate_local(text, full_context)
        else:
            # Modo mock
            response = f"[Modo Mock] Entendí: '{text}'. Contexto: '{full_context[:100]}'"
        
        return response

    async def _generate_with_api(self, text: str, context: str) -> str:
        """Genera respuesta usando Gemini API."""
        prompt = self._build_prompt(text, context)
        return await self.llm_client.generate(
            prompt,
            max_tokens=2048,
            temperature=0.7
        )

    async def _generate_local(self, text: str, context: str) -> str:
        """Genera respuesta usando LLM local."""
        prompt = self._build_prompt(text, context)
        
        def generate():
            output = self.llm(prompt, max_tokens=256, stop=["Usuario:", "User:", "\n\n"], echo=False)
            return output['choices'][0]['text'].strip()
        
        return await asyncio.to_thread(generate)

    def _build_prompt(self, text: str, context: str) -> str:
        """construye el prompt para el LLM."""
        context_section = f"Contexto relevante: {context}" if context else ""
        
        return f"""<|system|>
Eres MEA, una Inteligencia Artificial operando en una red distribuida (Enjambre).
Tu objetivo es ayudar al usuario de forma clara y concisa en español.
{context_section}
</s>
<|user|
{text}
</s>
<|assistant|
"""