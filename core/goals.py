# core/goals.py

import uuid
from typing import List, Dict, Any, Optional
from enum import Enum

class GoalStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Goal:
    """
    Representa un único objetivo autogenerado por el sistema.
    """
    def __init__(self, description: str, source: str, details: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.description = description
        self.source = source  # De dónde vino el objetivo (e.g., 'curiosity', 'user')
        self.details = details # Información adicional, como el query del gap
        self.status = GoalStatus.PENDING
        self.sub_goals: List[Goal] = []

    def __repr__(self):
        return f"Goal(id={self.id}, status={self.status.value}, desc='{self.description}')"

class GoalManager:
    """
    Gestiona la creación, planificación y seguimiento de objetivos internos.
    """
    def __init__(self):
        self.active_goals: List[Goal] = []

    def create_goal_from_gap(self, knowledge_gap: str):
        """
        Crea un nuevo objetivo a partir de un gap de conocimiento.
        
        Args:
            knowledge_gap (str): La consulta que generó el gap.
        """
        description = f"Investigar y aprender sobre: '{knowledge_gap}'"
        details = {"query": knowledge_gap}
        new_goal = Goal(description, source="curiosity", details=details)
        
        # Evitar duplicados
        if not any(g.details.get('query') == knowledge_gap for g in self.active_goals):
            self.active_goals.append(new_goal)
            print(f"[Metas] Nuevo objetivo creado: {description}")
        else:
            print(f"[Metas] Ya existe un objetivo para el gap: '{knowledge_gap}'")

    def get_pending_goals(self) -> List[Goal]:
        """
        Devuelve una lista de todos los objetivos que están pendientes.
        """
        return [g for g in self.active_goals if g.status == GoalStatus.PENDING]

    def update_goal_status(self, goal_id: str, status: GoalStatus):
        """
        Actualiza el estado de un objetivo.
        """
        goal = self.find_goal_by_id(goal_id)
        if goal:
            goal.status = status
            print(f"[Metas] Estado del objetivo {goal_id} actualizado a {status.value}")
        else:
            print(f"[Metas] No se encontró el objetivo con ID {goal_id}")

    def find_goal_by_id(self, goal_id: str) -> Optional[Goal]:
        """
        Busca un objetivo en la lista de objetivos activos por su ID.
        """
        for goal in self.active_goals:
            if goal.id == goal_id:
                return goal
        return None

    def get_all_goals(self) -> List[Dict]:
        """
        Devuelve una representación en diccionario de todos los objetivos activos.
        Útil para visualización en la WebApp.
        """
        return [
            {
                "id": g.id,
                "description": g.description,
                "status": g.status.value,
                "source": g.source,
                "details": g.details
            }
            for g in self.active_goals
        ]

# Ejemplo de cómo se integraría con el sistema de curiosidad

def example_usage_flow():
    from .curiosity import CuriositySystem

    curiosity = CuriositySystem()
    goal_manager = GoalManager()

    # Simular la detección de un gap
    curiosity.identified_gaps.add("física de partículas")
    curiosity.identified_gaps.add("historia del arte renacentista")

    # El planificador principal revisa los gaps y crea objetivos
    gaps = curiosity.get_identified_gaps()
    for gap in gaps:
        goal_manager.create_goal_from_gap(gap)

    # Ver los objetivos pendientes
    pending_goals = goal_manager.get_pending_goals()
    print(f"\nObjetivos pendientes: {pending_goals}")

    # Simular que se completa un objetivo
    if pending_goals:
        goal_to_complete = pending_goals[0]
        goal_manager.update_goal_status(goal_to_complete.id, GoalStatus.COMPLETED)

    # Ver todos los objetivos para la UI
    all_goals_for_ui = goal_manager.get_all_goals()
    print(f"\nEstado de todos los objetivos para la UI:")
    import json
    print(json.dumps(all_goals_for_ui, indent=2))

if __name__ == '__main__':
    print("Ejecutando ejemplo de uso del gestor de metas...")
    example_usage_flow()
