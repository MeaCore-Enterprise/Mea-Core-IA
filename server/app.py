import json
from fastapi import FastAPI
from pydantic import BaseModel
from core.cerebro import Brain
from core.conocimiento import KnowledgeManager

# Cargar configuración
with open("config/settings.json", "r") as f:
    settings = json.load(f)

with open("config/responses.json", "r") as f:
    responses = json.load(f)

class QuestionRequest(BaseModel):
    question: str

app = FastAPI(title="Mea-Core Enterprise API")

# Inicializar Cerebro
cerebro = Brain(settings=settings, responses=responses)
kb = KnowledgeManager()

@app.get("/")
def root():
    return {"message": "Mea-Core-Enterprise API corriendo 🚀"}

@app.post("/ask")
def ask(request: QuestionRequest):
    respuesta = cerebro.get_response(request.question)
    return {"question": request.question, "answer": respuesta}
