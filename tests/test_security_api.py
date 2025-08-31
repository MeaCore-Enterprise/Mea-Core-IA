import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.app import app, get_db
from core import models
from core.database import Base

# --- Configuración de la Base de Datos de Prueba ---

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture de Setup y Teardown ---

@pytest.fixture(scope="module")
def db_session():
    """Fixture que gestiona la base de datos de prueba para el módulo."""
    # Limpiar y crear la base de datos una vez por módulo
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # --- SEMBRADO DE DATOS ESENCIALES ---
        # Añadir roles para que el registro de usuarios funcione
        default_roles = [models.Role(name='admin'), models.Role(name='dev'), models.Role(name='cliente')]
        db.add_all(default_roles)
        db.commit()
        yield db
    finally:
        db.close()

    # Limpiar al final
    os.remove("./test.db")

@pytest.fixture(scope="module")
def client(db_session):
    """Fixture que crea un TestClient con la base de datos de prueba."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass # La sesión se cierra en el fixture db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

# --- Tests ---

def test_register_user(client):
    """Prueba el registro de un nuevo usuario con éxito."""
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_register_existing_user(client):
    """Prueba que no se puede registrar un usuario con un nombre de usuario existente."""
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "another@example.com", "password": "testpassword"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "El nombre de usuario ya está registrado"}

def test_login_for_access_token(client):
    """Prueba el inicio de sesión exitoso y la obtención de un token."""
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_login_wrong_password(client):
    """Prueba el inicio de sesión con una contraseña incorrecta."""
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_read_current_user(client):
    """Prueba el acceso a una ruta protegida con un token válido."""
    token = test_login_for_access_token(client) # Obtener un token fresco
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_read_current_user_invalid_token(client):
    """Prueba el acceso a una ruta protegida con un token inválido."""
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 401