

import sqlite3
import time
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List

# --- Configuración ---
DB_PATH = "D:/IA/Mea-Core/central_memory.db"

# --- Modelo de Datos ---
class Conversation(BaseModel):
    user_input: str
    bot_output: List[str]

# --- Aplicación FastAPI ---
app = FastAPI(
    title="Mea-Core Central Learning API",
    description="API para recibir y almacenar conversaciones para el aprendizaje centralizado de Mea-Core.",
    version="1.0.0"
)

# --- Base de Datos ---
def init_db():
    """Inicializa la base de datos del servidor central."""
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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
@app.post("/api/learn")
async def learn_from_conversation(conversation: Conversation):
    """
    Recibe una conversación y la guarda en la base de datos central.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        now = time.time()
        bot_output_str = "\n".join(conversation.bot_output)
        
        conn.execute("""
        INSERT INTO conversations (timestamp, user_input, bot_output)
        VALUES (?, ?, ?)
        """, (now, conversation.user_input, bot_output_str))
        
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Conversación almacenada."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.on_event("startup")
async def startup_event():
    """Se ejecuta al iniciar el servidor."""
    print("Iniciando servidor Mea-Core...")
    init_db()
    print(f"Base de datos central inicializada en: {DB_PATH}")
    print("Endpoint de aprendizaje disponible en: /api/learn")

# --- Para ejecutar el servidor --- 
# Abre una terminal en el directorio MEA-Core-IA y ejecuta:
# uvicorn server.main:app --reload

