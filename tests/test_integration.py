import pytest
from unittest.mock import MagicMock

# Import components needed for the integration test
from core.brain import Brain
from core.memory_store import MemoryStore
from core.knowledge_base import KnowledgeBase

@pytest.fixture
def integration_test_setup():
    """
    Sets up a realistic environment for integration testing.
    It provides a Brain instance with mocked dependencies.
    """
    # Basic configuration for the test
    settings = {
        "brain": {
            "mode": "rule"  # Start with a simple mode
        }
    }
    responses = {
        "saludos": ["Hola"],
        "respuestas_especificas": {
            "pregunta simple": ["respuesta simple"]
        },
        "plantillas_generales": ["No sé sobre '{input}'"]
    }

    # Mock the dependencies
    mock_memory = MagicMock(spec=MemoryStore)
    mock_kb = MagicMock(spec=KnowledgeBase)

    # Configure the mock for the knowledge base
    # When semantic_search is called with any arguments, return a specific list
    mock_kb.semantic_search.return_value = ["Este es un resultado de la base de conocimiento."]
    # Make bm25_search return nothing to isolate the semantic search test
    mock_kb.bm25_search.return_value = []


    # Create the Brain instance with mocked dependencies
    brain = Brain(
        settings=settings,
        responses=responses,
        memory=mock_memory,
        knowledge_base=mock_kb,
        swarm_controller=None # Not needed for this test
    )

    return brain, mock_kb, mock_memory

def test_full_flow_with_kb_query(integration_test_setup):
    """
    Tests a full interaction flow where the Brain needs to consult the Knowledge Base.
    """
    brain, mock_kb, mock_memory = integration_test_setup

    # 1. Define a user input that is not a greeting or a specific question
    user_input = "Háblame sobre la arquitectura del sistema"

    # 2. Process the message
    response = brain.get_response(user_input)

    # 3. Verify the interaction with the Knowledge Base
    # Assert that the semantic_search method on the mock_kb was called exactly once
    mock_kb.semantic_search.assert_called_once_with(user_input.lower(), top_n=2)

    # 4. Verify the final response
    # Check that the response from the mock KB is included in the final output
    assert "Este es un resultado de la base de conocimiento." in response[1] # The response is formatted, so check for inclusion

# TODO: Add more integration tests:
# - Test that memory is queried for context.
# - Test that the rule_engine mode integrates correctly with other components.
# - Test the flow when a goal is active.
# - Test the complete flow from a bot (e.g., cli_bot) to the brain and back.