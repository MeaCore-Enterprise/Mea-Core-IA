import pytest
from unittest.mock import MagicMock, patch

# Import the class to be tested
from core.brain import Brain

# Mock dependencies if they are complex to set up
from core.memory_store import MemoryStore
from core.knowledge_base import KnowledgeBase
from core.swarm_controller import SwarmController
from core.goals import GoalManager

# Check for optional dependencies
try:
    from experta import KnowledgeEngine
    EXPERTA_AVAILABLE = True
except ImportError:
    EXPERTA_AVAILABLE = False

try:
    from sklearn.linear_model import LogisticRegression
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
    """Mocks the external dependencies of the Brain."""
    mock_memory = MagicMock(spec=MemoryStore)
    mock_kb = MagicMock(spec=KnowledgeBase)
    mock_swarm = MagicMock(spec=SwarmController)
    
    # Mock the return value for search methods to simulate no results
    mock_kb.bm25_search.return_value = []
    mock_kb.semantic_search.return_value = []

    return {
        "memory": mock_memory,
        "knowledge_base": mock_kb,
        "swarm_controller": mock_swarm
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
    """Tests that the Brain initializes correctly."""
    assert brain_instance is not None
    assert brain_instance.mode == "rule"
    assert brain_instance.memory is not None
    assert brain_instance.knowledge_base is not None

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

def test_get_response_from_kb(brain_instance):
    """Tests that the brain attempts to get a response from the knowledge base."""
    # Setup the mock to return a specific result for this test
    brain_instance.knowledge_base.bm25_search.return_value = ["Resultado de KB"]
    
    response = brain_instance.get_response("consulta a la kb")
    
    # Verify that the search method was called
    brain_instance.knowledge_base.bm25_search.assert_called_with("consulta a la kb", top_n=3)
    
    # Verify that the response includes the KB result
    assert "[BM25] Resultados relevantes:" in response
    assert "- Resultado de KB" in response

@pytest.mark.skipif(not SKLEARN_AVAILABLE, reason="scikit-learn is not installed")
def test_ml_mode_initialization(basic_responses, mock_dependencies):
    """Tests that the Brain initializes and trains a model in ML mode."""
    ml_settings = {"brain": {"mode": "ml"}}
    with patch('core.brain.make_pipeline') as mock_pipeline:
        # Mock the pipeline and fit method
        mock_model = MagicMock()
        mock_pipeline.return_value = mock_model

        brain = Brain(settings=ml_settings, responses=basic_responses, **mock_dependencies)
        
        assert brain.mode == "ml"
        # Check that the training process was initiated
        assert mock_model.fit.called
        assert brain.model is not None

@pytest.mark.skipif(not EXPERTA_AVAILABLE, reason="experta is not installed")
def test_rule_engine_mode_initialization(basic_responses, mock_dependencies):
    """Tests that the Brain initializes the ReasoningEngine in rule_engine mode."""
    engine_settings = {"brain": {"mode": "rule_engine"}}
    brain = Brain(settings=engine_settings, responses=basic_responses, **mock_dependencies)
    assert brain.mode == "rule_engine"
    assert brain.reasoning_engine is not None
    # Check if it's an instance of a class that looks like the reasoning engine
    assert hasattr(brain.reasoning_engine, 'get_rules')

# TODO: Add more tests for the following functionalities:
# - Interaction with GoalManager
# - Active learning module integration
# - Memory consolidation (summarization, entity extraction)
# - Dynamic rule engine interaction (add_rule, list_rules)
# - Swarm controller interaction
# - Different scenarios for get_response combining all sources