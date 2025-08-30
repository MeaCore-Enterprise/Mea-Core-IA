"""
Módulo de curiosidad y motivación intrínseca para MEA-Core-IA.

Este módulo está diseñado para dotar a la IA de un impulso para explorar
y aprender de forma proactiva.
"""

from typing import Any, Set
import random

class CuriosityModule:
    """Simula la curiosidad a través de la recompensa por la novedad.

    Mantiene un registro de los "estados" que ha visitado y genera una
    recompensa intrínseca mayor cuando se encuentra con uno nuevo.
    """
    def __init__(self) -> None:
        """Inicializa el módulo de curiosidad.
        
        Crea un conjunto para almacenar los estados ya conocidos.
        """
        self.known_states: Set[Any] = set()

    def intrinsic_reward(self, state: Any) -> float:
        """Calcula una recompensa basada en la novedad de un estado.

        Si el estado no ha sido visitado antes, lo añade al conjunto de estados
        conocidos y devuelve una recompensa alta (1.0). Si ya era conocido,
        devuelve una recompensa baja (0.1).

        Args:
            state (Any): Una representación del estado a evaluar.

        Returns:
            float: El valor de la recompensa intrínseca.
        """
        if state not in self.known_states:
            self.known_states.add(state)
            return 1.0
        return 0.1

    def explore(self) -> str:
        """Sugiere una acción exploratoria aleatoria.

        Returns:
            str: Una cadena de texto que representa una acción para explorar.
        """
        actions = ["leer documento", "analizar código", "buscar información"]
        return random.choice(actions)
