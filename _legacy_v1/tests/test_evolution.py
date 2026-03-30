# tests/test_evolution.py

import os
import json
import pytest

from core.evolution import EvolutionChamber, SuggestionStatus, ChangeType, SUGGESTIONS_FILE

@pytest.fixture
def evolution_chamber() -> EvolutionChamber:
    # Asegurarse de que el archivo de sugerencias no exista al empezar
    if os.path.exists(SUGGESTIONS_FILE):
        os.remove(SUGGESTIONS_FILE)
    
    chamber = EvolutionChamber()
    yield chamber
    
    # Limpiar después del test
    if os.path.exists(SUGGESTIONS_FILE):
        os.remove(SUGGESTIONS_FILE)

def test_propose_change_on_slow_performance(evolution_chamber: EvolutionChamber):
    """Verifica que se genera una propuesta cuando el rendimiento es bajo."""
    slow_metrics = {"avg_memory_query_time": 0.8}
    evolution_chamber.analyze_performance(slow_metrics)
    
    pending = evolution_chamber.get_pending_suggestions()
    assert len(pending) == 1
    assert pending[0]['status'] == SuggestionStatus.PROPOSED.value
    assert "0.80s" in pending[0]['description']

def test_no_proposal_on_good_performance(evolution_chamber: EvolutionChamber):
    """Verifica que no se generan propuestas si el rendimiento es bueno."""
    good_metrics = {"avg_memory_query_time": 0.1}
    evolution_chamber.analyze_performance(good_metrics)
    
    pending = evolution_chamber.get_pending_suggestions()
    assert len(pending) == 0

def test_supervised_approval_flow(evolution_chamber: EvolutionChamber):
    """Prueba el flujo completo: propuesta -> aprobación -> implementación (simulada)."""
    # 1. Se genera una propuesta
    slow_metrics = {"avg_memory_query_time": 0.9}
    evolution_chamber.analyze_performance(slow_metrics)
    pending = evolution_chamber.get_pending_suggestions()
    assert len(pending) == 1
    suggestion_id = pending[0]['id']

    # 2. Se intenta aplicar sin aprobación (no debería hacer nada)
    evolution_chamber.apply_approved_changes()
    # Recargamos desde el archivo para estar seguros
    evolution_chamber._load_suggestions()
    suggestion = next(s for s in evolution_chamber.suggestions if s.id == suggestion_id)
    assert suggestion.status == SuggestionStatus.PROPOSED

    # 3. Se aprueba la propuesta
    evolution_chamber.approve_suggestion(suggestion_id)
    suggestion = next(s for s in evolution_chamber.suggestions if s.id == suggestion_id)
    assert suggestion.status == SuggestionStatus.APPROVED

    # 4. Se aplica el cambio aprobado (ahora sí debería cambiar el estado)
    evolution_chamber.apply_approved_changes()
    suggestion = next(s for s in evolution_chamber.suggestions if s.id == suggestion_id)
    assert suggestion.status == SuggestionStatus.IMPLEMENTED

def test_suggestions_are_persisted(evolution_chamber: EvolutionChamber):
    """Verifica que las sugerencias se guardan y se cargan correctamente."""
    slow_metrics = {"avg_memory_query_time": 0.7}
    evolution_chamber.analyze_performance(slow_metrics)
    
    # Crear una nueva instancia para forzar la carga desde el archivo
    new_chamber = EvolutionChamber()
    pending = new_chamber.get_pending_suggestions()
    assert len(pending) == 1
    assert pending[0]['status'] == SuggestionStatus.PROPOSED.value
