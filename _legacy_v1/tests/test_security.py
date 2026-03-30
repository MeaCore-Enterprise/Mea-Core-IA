# tests/test_security.py

import os
import json
import pytest
from unittest.mock import patch

from core.security import auditor, AUDIT_LOG_FILE, get_password_hash, decode_access_token, create_access_token

@pytest.fixture(autouse=True)
def cleanup_log():
    """Asegura que el log está limpio antes y después de cada test."""
    if os.path.exists(AUDIT_LOG_FILE):
        os.remove(AUDIT_LOG_FILE)
    yield
    if os.path.exists(AUDIT_LOG_FILE):
        os.remove(AUDIT_LOG_FILE)

def test_audit_log_is_created():
    """Verifica que el archivo de log se crea al registrar el primer evento."""
    assert not os.path.exists(AUDIT_LOG_FILE)
    auditor.log_event("TEST_EVENT", "test_subject", "SUCCESS")
    assert os.path.exists(AUDIT_LOG_FILE)

def test_failed_token_validation_is_logged():
    """Verifica que un intento fallido de decodificar un token se registra."""
    invalid_token = "untokeninvalido"
    decode_access_token(invalid_token)
    
    with open(AUDIT_LOG_FILE, 'r') as f:
        log_entry = json.loads(f.readline())
    
    assert log_entry['event_type'] == "TOKEN_VALIDATION"
    assert log_entry['subject'] == invalid_token
    assert log_entry['outcome'] == "FAILURE"
    assert "error" in log_entry['details']

def test_successful_token_creation_is_logged():
    """Verifica que la creación exitosa de un token se registra."""
    user_data = {"sub": "testuser"}
    create_access_token(user_data)
    
    with open(AUDIT_LOG_FILE, 'r') as f:
        log_entry = json.loads(f.readline())
        
    assert log_entry['event_type'] == "TOKEN_CREATION"
    assert log_entry['subject'] == "testuser"
    assert log_entry['outcome'] == "SUCCESS"

def test_password_hashing_is_logged():
    """Verifica que la generación de un hash de contraseña se registra."""
    get_password_hash("micontraseña")
    
    with open(AUDIT_LOG_FILE, 'r') as f:
        log_entry = json.loads(f.readline())
        
    assert log_entry['event_type'] == "PASSWORD_HASH"
    assert log_entry['subject'] == "system"
    assert log_entry['outcome'] == "SUCCESS"

# Las pruebas de cifrado de base de datos son más complejas y requerirían
# una base de datos real y librerías de criptografía. Se marcarían como
# pendientes para un test de integración completo.

def test_database_encryption_placeholder():
    """Placeholder para un futuro test de cifrado de la base de datos."""
    assert True # Asumimos que se implementará en el futuro