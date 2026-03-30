import pytest
from unittest.mock import MagicMock, patch

# Añadir el directorio raíz al path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cerebro import Brain, SKLEARN_AVAILABLE, EXPERTA_AVAILABLE
from core.memoria import MemoryStore
from core.conocimiento import KnowledgeManager

# --- Fixtures básicas (similares a test_brain.py) ---

@pytest.fixture
def basic_responses():
    """Provee un diccionario de respuestas básico."""
    return {
        "respuestas_especificas": {
            "pregunta clave": ["respuesta de regla simple"],
            "intencion ml": ["respuesta de ml"]
        },
        "plantillas_generales": ["fallback general"]
    }

@pytest.fixture
def mock_dependencies():
    """Mocks de las dependencias del Cerebro."""
    mock_memory = MagicMock(spec=MemoryStore)
    mock_knowledge = MagicMock(spec=KnowledgeManager)
    mock_memory.get_memory.return_value = []
    mock_knowledge.query.return_value = {}
    return {
        "memory": mock_memory,
        "knowledge": mock_knowledge,
        "replication_controller": MagicMock(),
        "ethics_core": MagicMock()
    }

# --- Pruebas de Fallback ---

@pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn no está instalado")
@patch('core.cerebro.ReasoningEngine')
def test_fallback_from_ml_to_rule_engine(MockReasoningEngine, basic_responses, mock_dependencies):
    """Prueba que el cerebro cae a 'rule_engine' si 'ml' falla."""
    # Configurar el mock del motor de reglas para que devuelva una respuesta específica
    mock_rule_engine_instance = MockReasoningEngine.return_value
    mock_rule_engine_instance.run_engine.return_value = "respuesta de rule_engine"

    # Configurar el cerebro en modo 'ml'
    settings = {"brain": {"mode": "ml"}}
    brain = Brain(settings, basic_responses, **mock_dependencies)
    
    # Simular un fallo en el modelo ML
    brain.model = MagicMock()
    brain.model.predict.side_effect = Exception("Fallo de predicción de ML")

    # Ejecutar
    response = brain.get_response("entrada de usuario")

    # Verificar
    brain.model.predict.assert_called_once()
    mock_rule_engine_instance.run_engine.assert_called_once()
    assert response == ["respuesta de rule_engine"]

@pytest.mark.skipif(not EXPERTA_AVAILABLE, reason="experta no está instalado")
def test_fallback_from_rule_engine_to_simple_rule(basic_responses, mock_dependencies):
    """Prueba que el cerebro cae a regla simple si 'rule_engine' falla."""
    # Configurar el cerebro en modo 'rule_engine'
    settings = {"brain": {"mode": "rule_engine"}}
    brain = Brain(settings, basic_responses, **mock_dependencies)

    # Simular un fallo en el motor de reglas
    brain.reasoning_engine.run_engine = MagicMock(side_effect=Exception("Fallo del motor de reglas"))

    # Ejecutar con una entrada que coincida con una regla simple
    response = brain.get_response("pregunta clave")

    # Verificar
    brain.reasoning_engine.run_engine.assert_called_once()
    assert response == ["respuesta de regla simple"]

@pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn no está instalado")
@patch('core.cerebro.ReasoningEngine')
def test_full_fallback_to_general_template(MockReasoningEngine, basic_responses, mock_dependencies):
    """Prueba la cadena completa de fallbacks hasta la plantilla general."""
    # Configurar mocks para que todos los sistemas fallen
    mock_rule_engine_instance = MockReasoningEngine.return_value
    mock_rule_engine_instance.run_engine.side_effect = Exception("Fallo de RE")

    settings = {"brain": {"mode": "ml"}}
    brain = Brain(settings, basic_responses, **mock_dependencies)
    brain.model = MagicMock()
    brain.model.predict.side_effect = Exception("Fallo de ML")

    # Asegurarse de que la memoria y el conocimiento no devuelvan nada
    brain.memory.get_memory.return_value = []
    brain.knowledge.query.return_value = {}
    brain.engine = None # Desactivar motor de embeddings

    # Ejecutar con una entrada que no coincida con ninguna regla simple
    response = brain.get_response("entrada completamente desconocida")

    # Verificar que se intentaron los modos primarios
    brain.model.predict.assert_called_once()
    # El mock de la instancia se crea dentro de la inicialización de Brain
    # por lo que necesitamos acceder a él a través del mock de la clase.
    brain.reasoning_engine.run_engine.assert_called_once()
    
    # Verificar que la respuesta es la plantilla general
    assert response == ["fallback general"]
