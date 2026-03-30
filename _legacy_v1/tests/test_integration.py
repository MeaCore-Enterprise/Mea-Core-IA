import pytest
from unittest.mock import MagicMock

# Import components needed for the integration test
from core.cerebro import Brain
from core.memoria import MemoryStore
from core.conocimiento import KnowledgeManager
from core.etica import EthicsCore

@pytest.fixture
def integration_test_setup():
    """
    Sets up a realistic environment for integration testing.
    It provides a Brain instance with mocked dependencies.
    """
    settings = {"brain": {"mode": "rule"}}
    responses = {
        "saludos": ["Hola"],
        "respuestas_especificas": {},
        "plantillas_generales": ["No sé sobre '{input}'"]
    }

    mock_memory = MagicMock(spec=MemoryStore)
    mock_memory.get_memory.return_value = [] # Asegurar que la memoria no interfiera
    mock_kb = MagicMock(spec=KnowledgeManager)
    mock_ethics = MagicMock(spec=EthicsCore)
    mock_ethics.check_action.return_value = (True, None)

    # Configure the mock for the new 'query' method
    mock_kb.query.return_value = {
        'direct_facts': ["La arquitectura es modular."],
        'relations': ["cerebro -> usa -> memoria"]
    }

    brain = Brain(
        settings=settings,
        responses=responses,
        memory=mock_memory,
        knowledge=mock_kb,
        ethics=mock_ethics
    )

    return brain, mock_kb, mock_memory

def test_full_flow_with_kb_query(integration_test_setup):
    """
    Tests a full interaction flow where the Brain consults the Knowledge Base.
    """
    brain, mock_kb, mock_memory = integration_test_setup

    user_input = "Háblame sobre la arquitectura"

    response = brain.get_response(user_input)

    # Verify that the 'query' method on the mock_kb was called
    mock_kb.query.assert_called_once_with(user_input.lower())

    # Verify the final response includes data from the mock KB
    response_text = "\n".join(response)
    assert "La arquitectura es modular." in response_text
    assert "cerebro -> usa -> memoria" in response_text
