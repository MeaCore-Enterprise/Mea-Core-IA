import os
import sys

# Add parent directory to path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from pydantic import BaseModel
from core.node import SwarmNode
from core.vector_memory import VectorMemory
from core.agent import MeaAgent

app = FastAPI(title="MEA-Core V2 Distributed API Gateway")

# Global instances
node = None
memory = None
agent = None

@app.on_event("startup")
async def startup_event():
    global node, memory, agent
    
    # In a real environment, redis_url comes from ENV vars
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    node = SwarmNode(redis_url=redis_url)
    await node.connect()
    
    memory = VectorMemory(persist_directory="./data/chroma_db")
    agent = MeaAgent(node=node, memory=memory)

@app.on_event("shutdown")
async def shutdown_event():
    global node
    if node:
        await node.disconnect()

class InputRequest(BaseModel):
    text: str

@app.post("/chat")
async def chat(request: InputRequest):
    """
    Endpoint for users to chat with the AI.
    """
    response = await agent.process_input(request.text)
    return {"reply": response}

@app.post("/learn")
async def learn(request: InputRequest):
    """
    Force the AI to learn a fact and broadcast it to the swarm.
    """
    await agent.learn(request.text)
    return {"status": "Learned and synced"}
