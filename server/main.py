
# --- Modelos de Datos Pydantic ---
class RulePayload(BaseModel):
    condition: str
    action: str

# ...existing code...

# --- Endpoints de consolidación de memoria y motor de reglas dinámicas ---
@app.post("/api/memory/summarize", summary="Resumir conversación")
def summarize_conversation(payload: Query):
    summary = brain.resumir_conversacion(payload.text)
    return {"summary": summary}

@app.post("/api/memory/entities", summary="Extraer entidades clave")
def extract_entities(payload: Query):
    entities = brain.extraer_entidades(payload.text)
    return {"entities": entities}

@app.post("/api/rules/apply", summary="Aplicar reglas a un texto")
def apply_rules(payload: Query):
    result = brain.aplicar_reglas(payload.text)
    return {"result": result}

@app.post("/api/rules/add", summary="Agregar una nueva regla")
def add_rule(payload: RulePayload):
    brain.agregar_regla(payload.condition, payload.action)
    return {"status": "success"}

@app.get("/api/rules/list", summary="Listar reglas actuales")
def list_rules():
    rules = brain.listar_reglas()
    return {"rules": rules}
import sys
import os
import json
import time
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Añadir el directorio raíz al path para poder importar los módulos del core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings_manager import SettingsManager
from core.memory_store import MemoryStore
from core.ethics import EthicsCore
from core.brain import Brain
from core.knowledge_base import KnowledgeBase
from core.swarm_controller import SwarmController

# --- Modelos de Datos Pydantic ---
class Query(BaseModel):
    text: str
    context: Optional[List[str]] = None

class MemorySet(BaseModel):
    key: str
    value: Any

class LearnPayload(BaseModel):
    user_input: str
    bot_output: List[str]

print("Inicializando el núcleo de MEA-Core para el servidor...")
settings_manager = SettingsManager()
memory_store = MemoryStore()
knowledge_base = KnowledgeBase([])
swarm_controller = SwarmController(node_id="api")
ethics_core = EthicsCore()
brain = Brain(settings_manager.settings, settings_manager.get_responses(), memory=memory_store, knowledge_base=knowledge_base, swarm_controller=swarm_controller)

CENTRAL_DB_PATH = settings_manager.get_setting("remote_learning.central_db_path", "data/central_memory.db")
from fastapi import WebSocket, WebSocketDisconnect

# --- Aplicación FastAPI ---
app = FastAPI(
    title="MEA-Core API",
    description="API para interactuar con los módulos de MEA-Core IA.",
    version="2.0.0"
)

# --- WebSocket para consultas en tiempo real ---
@app.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "")
            context = data.get("context", None)
            if not ethics_core.check_action(text):
                await websocket.send_json({"error": ethics_core.explain_decision(text)})
                continue
            responses = brain.get_response(text, context)
            memory_store.log_conversation(user_input=text, bot_output=responses)
            await websocket.send_json({"responses": responses})
    except WebSocketDisconnect:
        print("[WebSocket] Cliente desconectado.")
    except Exception as e:
        await websocket.send_json({"error": str(e)})

# --- Base de Datos Central (para aprendizaje) ---
def init_central_db():
    db_dir = os.path.dirname(CENTRAL_DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(CENTRAL_DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        user_input TEXT,
        bot_output TEXT
    )""")
    conn.commit()
    conn.close()

# --- Endpoints de la API ---

@app.get("/api/status", summary="Obtener estado del sistema")
def get_status():
    """Devuelve el estado actual de los componentes del núcleo de la IA."""
    return {
        "status": "ok",
        "timestamp": time.time(),
        "settings": {
            "remote_learning_enabled": settings_manager.get_setting("remote_learning.enabled"),
            "swarm_replication_enabled": settings_manager.get_setting("swarm.replication_enabled"),
            "brain_mode": settings_manager.get_setting("brain.mode")
        },
        "memory_stats": memory_store.get_stats()
    }

@app.post("/api/query", summary="Procesar una consulta")
def process_query(query: Query):
    """Recibe una consulta, la procesa a través del cerebro y devuelve una respuesta."""
    if not ethics_core.check_action(query.text):
        raise HTTPException(status_code=403, detail=ethics_core.explain_decision(query.text))
    
    responses = brain.get_response(query.text, query.context)
    memory_store.log_conversation(user_input=query.text, bot_output=responses)
    return {"responses": responses}

@app.get("/api/memory/get/{key}", summary="Obtener valor de la memoria")
def get_memory(key: str):
    """Obtiene un valor de la memoria clave-valor de la instancia."""
    value = memory_store.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Clave no encontrada en la memoria.")
    return {"key": key, "value": value}

@app.post("/api/memory/set", summary="Establecer valor en la memoria")
def set_memory(payload: MemorySet):
    """Establece un valor en la memoria clave-valor de la instancia."""
    memory_store.set(payload.key, payload.value)
    return {"status": "success", "key": payload.key, "value": payload.value}

@app.post("/api/learn", summary="Almacenar conversación para aprendizaje")
def learn_from_conversation(payload: LearnPayload):
    """
    Recibe una conversación y la guarda en la base de datos central para aprendizaje futuro.
    """
    try:
        conn = sqlite3.connect(CENTRAL_DB_PATH)
        now = time.time()
        bot_output_str = "\n".join(payload.bot_output)
        
        conn.execute("INSERT INTO conversations (timestamp, user_input, bot_output) VALUES (?, ?, ?)", 
                     (now, payload.user_input, bot_output_str))
        
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Conversación almacenada."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")

@app.post("/api/memory/summarize", summary="Resumir conversación")
def summarize_conversation(payload: Query):
    summary = brain.resumir_conversacion(payload.text)
    return {"summary": summary}

@app.post("/api/memory/entities", summary="Extraer entidades clave")
def extract_entities(payload: Query):
    entities = brain.extraer_entidades(payload.text)
    return {"entities": entities}

@app.post("/api/rules/apply", summary="Aplicar reglas a un texto")
def apply_rules(payload: Query):
    result = brain.aplicar_reglas(payload.text)
    return {"result": result}

@app.post("/api/rules/add", summary="Agregar una nueva regla")
def add_rule(payload: RulePayload):
    brain.agregar_regla(payload.condition, payload.action)
    return {"status": "success"}

@app.get("/api/rules/list", summary="Listar reglas actuales")
def list_rules():
    rules = brain.listar_reglas()
    return {"rules": rules}

@app.on_event("startup")
async def startup_event():
    """Se ejecuta al iniciar el servidor."""
    print("Iniciando servidor MEA-Core...")
    init_central_db()
    print(f"Base de datos central inicializada en: {CENTRAL_DB_PATH}")
    print("API de MEA-Core lista.")

# Para ejecutar: uvicorn server.main:app --reload