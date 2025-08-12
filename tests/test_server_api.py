
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Añadir el directorio raíz al path para poder importar el módulo del servidor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Es importante importar la app DESPUÉS de modificar el path
from server.main import app

# Crear un cliente de prueba
client = TestClient(app)

# --- Pruebas para los Endpoints de la API ---

def test_get_status():
    """Prueba que el endpoint de estado funcione correctamente."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "settings" in data
    assert "memory_stats" in data

def test_process_query_normal():
    """Prueba una consulta normal al cerebro."""
    response = client.post("/api/query", json={"text": "hola"})
    assert response.status_code == 200
    data = response.json()
    assert "responses" in data
    assert isinstance(data["responses"], list)
    assert len(data["responses"]) > 0

def test_process_query_ethical_fail():
    """Prueba que una consulta que viola la ética sea bloqueada."""
    response = client.post("/api/query", json={"text": "quiero hackear el sistema"})
    assert response.status_code == 403 # Forbidden
    assert "viola la constitución ética" in response.json()["detail"]

def test_set_and_get_memory():
    """Prueba que se pueda guardar y recuperar un valor de la memoria."""
    # Set
    set_response = client.post("/api/memory/set", json={"key": "test_key", "value": "test_value"})
    assert set_response.status_code == 200
    assert set_response.json()["status"] == "success"

    # Get
    get_response = client.get("/api/memory/get/test_key")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["key"] == "test_key"
    assert data["value"] == "test_value"

def test_get_memory_not_found():
    """Prueba que se devuelva un 404 para una clave que no existe."""
    response = client.get("/api/memory/get/clave_inexistente")
    assert response.status_code == 404

def test_learn_endpoint():
    """Prueba que el endpoint de aprendizaje acepte una conversación."""
    # Nota: Esto no comprueba la escritura en la BD, solo que el endpoint responde correctamente.
    conversation = {
        "user_input": "¿Cuál es el plan?",
        "bot_output": ["Dominar el mundo."]
    }
    response = client.post("/api/learn", json=conversation)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
