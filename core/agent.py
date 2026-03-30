import asyncio
import os
from .vector_memory import VectorMemory
from .node import SwarmNode

try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("[Advertencia] llama-cpp-python no está instalado. Ejecutando en MOCK mode.")

class MeaAgent:
    """
    El cerebro de MEA V2. Maneja conexiones a la memoria, se coordina
    con el nodo P2P y ejecuta el modelo de lenguaje de forma asíncrona.
    """
    def __init__(self, node: SwarmNode, memory: VectorMemory):
        self.node = node
        self.memory = memory
        
        # Register Swarm Listeners
        self.node.on("memory_sync", self._handle_remote_memory)
        self.node.on("query_request", self._handle_query_request)

        # Configuración del LLM
        self.llm = None
        self.model_path = os.getenv("LLM_MODEL_PATH", "./models/model.gguf")
        if LLAMA_AVAILABLE:
            self._load_model()
            
    def _load_model(self):
        try:
            print(f"[Agent] Intentando cargar LLM desde {self.model_path}...")
            # Cargar el modelo. n_ctx define la memoria a corto plazo de la charla.
            self.llm = Llama(model_path=self.model_path, n_ctx=2048, n_threads=4, verbose=False)
            print("[Agent] LLM cargado exitosamente.")
        except Exception as e:
            print(f"[Agent] Fallo al cargar LLM: {e}. Por favor, usa run_download.py para descargar el modelo.")
            self.llm = None

    async def _handle_remote_memory(self, payload):
        print(f"[Agent] [SWARM] Recibiendo memoria remota: {payload.get('content')}")
        self.memory.add_memory(payload.get('content'), metadata={"source": "remote_node"})

    async def _handle_query_request(self, payload):
        query = payload.get("query")
        reply_to = payload.get("reply_to")
        print(f"[Agent] [SWARM] El nodo remoto solicitó contexto para: {query}")
        results = self.memory.search_memory(query, n_results=1)
        if results:
            await self.node.broadcast("query_response", {
                "target": reply_to,
                "answer": results[0]
            })

    async def learn(self, fact):
        print(f"[Agent] Aprendiendo nuevo hecho: {fact}")
        self.memory.add_memory(fact, metadata={"source": "local_user"})
        # Sincronizar el hecho con todos los demás PCs en el Enjambre
        await self.node.broadcast("memory_sync", {"content": fact})

    def _generate_response_sync(self, prompt, max_tokens=256):
        """
        Bloque síncrono que ejecuta la inferencia pesada del LLM.
        Se llamará desde un thread aparte para no bloquear la red asíncrona.
        """
        if not self.llm:
            return "(Error interno: El modelo IA no está cargado. Se detectó una falla en el motor Llama.cpp)."
        
        output = self.llm(prompt, max_tokens=max_tokens, stop=["Usuario:", "User:", "\n\n", "</s>"], echo=False)
        return output['choices'][0]['text'].strip()

    async def process_input(self, text):
        print(f"[Agent] Procesando: {text}")
        
        # 1. Buscar en memoria RAM/Local (Chroma Vector DB)
        memories = self.memory.search_memory(text)
        context = " | ".join(memories) if memories else "No hay recuerdos previos sobre esto."
        
        if not self.llm:
            return f"[Modo Mock] Escuché: '{text}'. Contexto recuperado: '{context}'. Descarga el modelo para activar la IA real."
        
        # 2. Construir Prompt con Formato (Ej: estilo Llama-3 / ChatML)
        prompt = (
            f"<|system|>\nEres MEA, una Inteligencia Artificial operando en una red distribuida (Enjambre). "
            f"Responde al usuario de forma clara y concisa en español. "
            f"Usa el siguiente contexto recuperado de tu memoria para formar tu respuesta si es útil: {context}</s>\n"
            f"<|user|>\n{text}</s>\n"
            f"<|assistant|>\n"
        )
        
        # 3. Inferir Asincrónicamente (Envía el trabajo a un Thread de la CPU para no trabar FastAPI/Redis)
        print("[Agent] Evaluando el cerebro profundo (LLM)...")
        response = await asyncio.to_thread(self._generate_response_sync, prompt)
        
        return response
