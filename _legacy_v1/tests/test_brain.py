import pytest
from unittest.mock import MagicMock, patch

# --- Importaciones actualizadas ---
from core.cerebro import Brain
from core.memoria import MemoryStore
from core.conocimiento import KnowledgeManager
from core.etica import EthicsCore
# --- Fin de importaciones actualizadas ---


# Check for optional dependencies
try:
    from experta import KnowledgeEngine  # noqa: F401
    EXPERTA_AVAILABLE = True
except ImportError:
    EXPERTA_AVAILABLE = False

try:
    from sklearn.linear_model import LogisticRegression  # noqa: F401
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

@pytest.fixture
def basic_settings():
    """Provides a basic settings dictionary for the Brain."""
    return {
        "brain": {
            "mode": "rule" # Default to simple rule mode for most tests
        }
    }

@pytest.fixture
def basic_responses():
    """Provides a basic responses dictionary."""
    return {
        "saludos": ["Hola de prueba"],
        "despedidas": ["Adiós de prueba"],
        "respuestas_especificas": {
            "pregunta clave": ["respuesta clave"]
        },
        "plantillas_generales": ["No entiendo la entrada: {input}"]
    }

@pytest.fixture
def mock_dependencies():
    """Mocks the new unified dependencies of the Brain."""
    mock_memory = MagicMock(spec=MemoryStore)
    mock_knowledge = MagicMock(spec=KnowledgeManager)
    mock_ethics = MagicMock(spec=EthicsCore)

    # Mock the return value for search methods to simulate no results
    mock_knowledge.query.return_value = {'direct_facts': [], 'relations': []}
    mock_memory.get_memory.return_value = []
    # Mock the ethics check to always allow actions in tests
    mock_ethics.check_action.return_value = (True, None)

    return {
        "memory": mock_memory,
        "knowledge": mock_knowledge,
        "ethics": mock_ethics
    }

@pytest.fixture
def brain_instance(basic_settings, basic_responses, mock_dependencies):
    """Creates a Brain instance with mocked dependencies."""
    brain = Brain(
        settings=basic_settings,
        responses=basic_responses,
        **mock_dependencies
    )
    return brain

def test_brain_initialization(brain_instance):
    """Tests that the Brain initializes correctly with new dependencies."""
    assert brain_instance is not None
    assert brain_instance.mode == "rule"
    assert brain_instance.memory is not None
    assert brain_instance.knowledge is not None # Updated from knowledge_base

def test_get_greeting(brain_instance):
    """Tests that a greeting is correctly retrieved."""
    greeting = brain_instance.get_greeting()
    assert greeting == "Hola de prueba"

def test_get_farewell(brain_instance):
    """Tests that a farewell is correctly retrieved."""
    farewell = brain_instance.get_farewell()
    assert farewell == "Adiós de prueba"

def test_get_response_specific_rule(brain_instance):
    """Tests a response from a specific rule."""
    response = brain_instance.get_response("pregunta clave")
    assert response == ["respuesta clave"]

def test_get_response_general_template(brain_instance):
    """Tests a response using the general template for unknown input."""
    response = brain_instance.get_response("entrada desconocida")
    assert response == ["No entiendo la entrada: entrada desconocida"]

def test_get_response_from_knowledge(brain_instance):
    """Tests that the brain attempts to get a response from the new KnowledgeManager."""
    # Setup the mock to return a specific result for this test
    brain_instance.knowledge.query.return_value = {
        'direct_facts': ["Hecho de prueba"],
        'relations': ["Relación de prueba"]
    }
    
    response = brain_instance.get_response("consulta a la kb")
    
    # Verify that the query method was called
    brain_instance.knowledge.query.assert_called_with("consulta a la kb")
    
    # Verify that the response includes the knowledge results
    assert "[Hechos Relevantes]" in response
    assert "- Hecho de prueba" in response
    assert "[Relaciones Relevantes]" in response
    assert "- Relación de prueba" in response

@pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn is not installed")
def test_ml_mode_initialization(basic_responses, mock_dependencies):
    """Tests that the Brain initializes and trains a model in ML mode."""
    ml_settings = {"brain": {"mode": "ml"}}
    with patch('core.cerebro.make_pipeline') as mock_pipeline:
        mock_model = MagicMock()
        mock_pipeline.return_value = mock_model

        brain = Brain(settings=ml_settings, responses=basic_responses, **mock_dependencies)
        
        assert brain.mode == "ml"
        assert mock_model.fit.called
        assert brain.model is not None

@pytest.mark.skipif(not EXPERTA_AVAILABLE, reason="experta is not installed")
def test_rule_engine_mode_initialization(basic_responses, mock_dependencies):
    """Tests that the Brain initializes the ReasoningEngine in rule_engine mode."""
    engine_settings = {"brain": {"mode": "rule_engine"}}
    brain = Brain(settings=engine_settings, responses=basic_responses, **mock_dependencies)
    assert brain.mode == "rule_engine"
    assert brain.reasoning_engine is not None
    assert hasattr(brain.reasoning_engine, 'get_rules')
