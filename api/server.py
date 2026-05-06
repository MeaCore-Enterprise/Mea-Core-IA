import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

from mea.node import SwarmNode
from mea.memory import VectorMemory
from mea.gemini_client import GeminiClient
from mea.agent import MeaAgent
from agents import SwarmOrchestrator
from evolution import SelfModifier, EvolutionEvaluator
from knowledge import KnowledgeRAG, WebSearch


# Global instances
node = None
memory = None
llm_client = None
agent = None
swarm = None
evaluator = None
knowledge_rag = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global node, memory, llm_client, agent, swarm, evaluator, knowledge_rag
    
    # Initialize dependencies
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Connect to swarm network
    node = SwarmNode(redis_url=redis_url)
    try:
        await node.connect()
    except Exception as e:
        print(f"[Warning] Redis no conectado: {e}")
    
    # Initialize memory
    memory = VectorMemory(persist_directory="./data/chroma_db")
    
    # Initialize LLM client (Gemini or local)
    run_mode = os.getenv("RUN_MODE", "hybrid")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if run_mode in ("api", "hybrid") and gemini_key:
        llm_client = GeminiClient(api_key=gemini_key)
        print(f"[LLM] Usando Gemini API")
    else:
        # Fallback to local LLM
        from mea.agent import MeaAgent
        llm_client = None
        print(f"[LLM] Modo local (sin API)")
    
    # Create agent
    agent = MeaAgent(node=node, memory=memory, llm_client=llm_client)
    
    # Create swarm orchestrator
    swarm = SwarmOrchestrator(llm_client=llm_client, node=node)
    swarm.create_agents(n_explorers=2, n_workers=3, n_validators=1)
    
    # Create evaluator
    evaluator = EvolutionEvaluator()
    
    # Create knowledge RAG
    web_search = WebSearch()
    knowledge_rag = KnowledgeRAG(vector_store=memory, search=web_search)
    
    print(f"[MEA-Core V3] Inicializado en modo {run_mode}")
    
    yield
    
    # Cleanup
    if node:
        await node.disconnect()
    print(f"[MEA-Core V3] shutdown completo")


app = FastAPI(title="MEA-Core V3 Hive Mind API", lifespan=lifespan)


class ChatRequest(BaseModel):
    text: str
    use_swarm: bool = False
    use_knowledge: bool = True


class LearnRequest(BaseModel):
    text: str
    metadata: dict = {}


@app.get("/")
async def root():
    return {
        "name": "MEA-Core V3 Hive Mind",
        "version": "3.0.0",
        "status": "online"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "node_connected": node.is_running if node else False,
        "llm_configured": llm_client.is_configured() if llm_client else False
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    """Endpoint para chatear con la IA."""
    try:
        # Get knowledge context if enabled
        context = ""
        if request.use_knowledge and knowledge_rag:
            kb_result = await knowledge_rag.query(request.text, use_web=True)
            context = kb_result.get("context", "")
        
        # Use swarm if requested
        if request.use_swarm and swarm:
            result = await swarm.execute_task(request.text, {"context": context})
            return {
                "reply": result.get("result", ""),
                "confidence": result.get("confidence", 0),
                "mode": "swarm"
            }
        else:
            # Use single agent
            response = await agent.process_input(request.text, context=context)
            return {
                "reply": response,
                "mode": "single"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/learn")
async def learn(request: LearnRequest):
    """Fuerza a la IA a aprender un hecho y sincronizarlo."""
    try:
        await agent.learn(request.text, metadata=request.metadata)
        return {"status": "learned_and_synced"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/swarm/stats")
async def swarm_stats():
    """Estadísticas del swarm."""
    if not swarm:
        raise HTTPException(status_code=400, detail="Swarm no inicializado")
    return swarm.get_swarm_stats()


@app.post("/swarm/execute")
async def swarm_execute(request: ChatRequest):
    """Ejecuta una tarea a través del swarm."""
    if not swarm:
        raise HTTPException(status_code=400, detail="Swarm no inicializado")
    
    result = await swarm.execute_task(request.text)
    return result


@app.get("/knowledge/search")
async def knowledge_search(query: str, num_results: int = 5):
    """Búsqueda de conocimiento."""
    if not knowledge_rag:
        raise HTTPException(status_code=400, detail="Knowledge no inicializado")
    
    result = await knowledge_rag.query(query, use_web=True)
    return result


@app.get("/memory/search")
async def memory_search(query: str, n_results: int = 5):
    """Buscar en memoria local."""
    if not memory:
        raise HTTPException(status_code=400, detail="Memory no inicializado")
    
    results = memory.search_memory(query, n_results=n_results)
    return {"results": results}


@app.post("/memory/add")
async def memory_add(request: LearnRequest):
    """Agregar a memoria."""
    if not memory:
        raise HTTPException(status_code=400, detail="Memory no inicializado")
    
    mem_id = memory.add_memory(request.text, metadata=request.metadata)
    return {"status": "added", "memory_id": mem_id}


@app.post("/memory/reset")
async def memory_reset():
    """Resetear memoria."""
    if not memory:
        raise HTTPException(status_code=400, detail="Memory no inicializado")
    
    memory.reset()
    return {"status": "reset"}


@app.get("/config")
async def config():
    """Configuración actual."""
    return {
        "run_mode": os.getenv("RUN_MODE", "hybrid"),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "llm_model": os.getenv("LLM_MODEL_NAME", "local")
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)