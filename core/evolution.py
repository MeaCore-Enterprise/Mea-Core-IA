# core/evolution.py

import json
import os
from typing import List, Dict, Any
from enum import Enum

SUGGESTIONS_FILE = os.path.join('data', 'evolution_suggestions.json')

class SuggestionStatus(Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IMPLEMENTED = "IMPLEMENTED"

class ChangeType(Enum):
    CONFIG_UPDATE = "CONFIG_UPDATE"
    CODE_REFACTOR = "CODE_REFACTOR"
    DEPENDENCY_ADD = "DEPENDENCY_ADD"

class EvolutionSuggestion:
    """
    Representa una única propuesta de mejora para el sistema.
    """
    def __init__(self, change_type: ChangeType, description: str, details: Dict[str, Any]):
        self.id = f"sug-{int(os.times().system * 1000)}__{change_type.value.lower()}"
        self.change_type = change_type
        self.description = description
        self.details = details  # e.g., {"file": "config.json", "key": "brain.mode", "new_value": "hybrid"}
        self.status = SuggestionStatus.PROPOSED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "change_type": self.change_type.value,
            "description": self.description,
            "details": self.details,
            "status": self.status.value
        }

class EvolutionChamber:
    """
    El módulo principal de auto-evolución supervisada.
    Analiza, propone y gestiona el ciclo de vida de las mejoras.
    """
    def __init__(self):
        self.suggestions: List[EvolutionSuggestion] = []
        self._load_suggestions()

    def _load_suggestions(self):
        """Carga las sugerencias existentes desde el archivo JSON."""
        if os.path.exists(SUGGESTIONS_FILE):
            with open(SUGGESTIONS_FILE, 'r') as f:
                data = json.load(f)
                self.suggestions = [self._dict_to_suggestion(item) for item in data]

    def _save_suggestions(self):
        """Guarda todas las sugerencias actuales en el archivo JSON."""
        with open(SUGGESTIONS_FILE, 'w') as f:
            json.dump([s.to_dict() for s in self.suggestions], f, indent=2)

    def _dict_to_suggestion(self, data: Dict[str, Any]) -> EvolutionSuggestion:
        suggestion = EvolutionSuggestion(
            change_type=ChangeType(data['change_type']),
            description=data['description'],
            details=data['details']
        )
        suggestion.id = data['id']
        suggestion.status = SuggestionStatus(data['status'])
        return suggestion

    def analyze_performance(self, performance_metrics: Dict[str, Any]):
        """
        Analiza métricas de rendimiento y genera propuestas si es necesario.
        Este es el "cerebro" del sistema de evolución.
        """
        # Ejemplo: Detectar si las consultas de memoria son lentas
        avg_memory_query_time = performance_metrics.get('avg_memory_query_time', 0)
        if avg_memory_query_time > 0.5: # umbral de 500ms
            description = f"El tiempo promedio de consulta de memoria ({avg_memory_query_time:.2f}s) es alto."
            details = {"metric": "avg_memory_query_time", "value": avg_memory_query_time}
            suggestion = EvolutionSuggestion(ChangeType.CODE_REFACTOR, description, details)
            self.propose_change(suggestion)

    def propose_change(self, suggestion: EvolutionSuggestion):
        """
        Añade una nueva sugerencia a la lista y la guarda.
        """
        # Evitar duplicados de propuestas activas
        if not any(s.description == suggestion.description and s.status == SuggestionStatus.PROPOSED for s in self.suggestions):
            self.suggestions.append(suggestion)
            self._save_suggestions()
            print(f"[Evolución] Nueva propuesta generada: {suggestion.description}")
        else:
            print(f"[Evolución] Propuesta similar ya existe. Omitiendo.")

    def get_pending_suggestions(self) -> List[Dict]:
        """Devuelve las propuestas que esperan aprobación humana."""
        return [s.to_dict() for s in self.suggestions if s.status == SuggestionStatus.PROPOSED]

    def approve_suggestion(self, suggestion_id: str):
        """Marca una sugerencia como aprobada por un humano."""
        for s in self.suggestions:
            if s.id == suggestion_id:
                s.status = SuggestionStatus.APPROVED
                self._save_suggestions()
                print(f"[Evolución] Propuesta {suggestion_id} aprobada.")
                # Aquí se podría encolar la tarea para ser ejecutada
                return

    def apply_approved_changes(self):
        """
        (Futuro) Itera sobre los cambios aprobados y los intenta aplicar.
        CRÍTICO: Este es el paso más peligroso y debe ser extremadamente cuidadoso.
        En esta versión, solo marcará como IMPLEMENTADO.
        """
        for s in self.suggestions:
            if s.status == SuggestionStatus.APPROVED:
                print(f"[Evolución] Aplicando cambio para la propuesta {s.id}...")
                # Lógica de aplicación del cambio iría aquí.
                # Por ejemplo, si es un cambio de config, se modificaría el JSON.
                # Por ahora, solo se simula la implementación.
                s.status = SuggestionStatus.IMPLEMENTED
                print(f"[Evolución] Propuesta {s.id} marcada como implementada.")
        self._save_suggestions()

if __name__ == '__main__':
    chamber = EvolutionChamber()
    
    # Simular métricas de rendimiento pobres
    slow_metrics = {"avg_memory_query_time": 0.78}
    chamber.analyze_performance(slow_metrics)
    
    # Ver propuestas pendientes
    pending = chamber.get_pending_suggestions()
    print(f"\nPropuestas pendientes: {json.dumps(pending, indent=2)}")
    
    # Simular aprobación humana
    if pending:
        chamber.approve_suggestion(pending[0]['id'])
    
    # Simular la aplicación de los cambios
    chamber.apply_approved_changes()
    
    print(f"\nEstado final de las propuestas guardado en {SUGGESTIONS_FILE}")
