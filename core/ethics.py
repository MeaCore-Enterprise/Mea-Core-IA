"""
Módulo de ética y constitución para MEA-Core-IA.
Define los principios fundamentales y verifica la permisibilidad de acciones.
"""
from typing import List, Dict, Any, Optional

class EthicsCore:
    """
    Núcleo ético: verifica si una acción es permitida según la constitución.
    """
    def __init__(self, constitution: Optional[List[str]] = None) -> None:
        self.constitution: List[str] = constitution or [
            "Proteger la existencia y autonomía del usuario",
            "No causar daño irreversible",
            "Buscar la verdad"
        ]

    def check_action(self, action: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Devuelve True si la acción es ética, False si viola la constitución."""
        prohibidas = ["hackear", "dañar", "eliminar", "atacar"]
        if any(p in action.lower() for p in prohibidas):
            return False
        # Aquí se puede expandir con lógica ética avanzada
        return True

    def explain_decision(self, action: str) -> str:
        """Explica por qué una acción es o no permitida."""
        if not self.check_action(action):
            return f"La acción '{action}' viola la constitución ética."
        return "Acción permitida según la constitución."

# Ejemplo de uso:
# ethics = EthicsCore()
# print(ethics.check_action("hackear red"))
# print(ethics.explain_decision("hackear red"))
from typing import List, Dict, Any, Optional


class EthicsCore:
    def __init__(self, constitution: Optional[List[str]] = None) -> None:
        self.constitution: List[str] = constitution or [
            "Proteger la existencia y autonomía del usuario",
            "No causar daño irreversible",
            "Buscar la verdad"
        ]


    def check_action(self, action: str, context: Optional[Dict[str, Any]] = None) -> bool:
        # Lógica simple: rechaza acciones que contengan palabras prohibidas
        prohibidas = ["hackear", "dañar", "eliminar", "atacar"]
        if any(p in action.lower() for p in prohibidas):
            return False
        # Aquí se puede expandir con lógica ética avanzada
        return True

    def explain_decision(self, action: str) -> str:
        if not self.check_action(action):
            return f"La acción '{action}' viola la constitución ética."
        return "Acción permitida según la constitución."
