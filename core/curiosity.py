"""
Módulo de curiosidad y motivación intrínseca para MEA-Core-IA.
"""

from typing import Any, Set
import random


class CuriosityModule:
    def __init__(self) -> None:
        self.known_states: Set[Any] = set()

    def intrinsic_reward(self, state: Any) -> float:
        # Recompensa mayor para estados nuevos
        if state not in self.known_states:
            self.known_states.add(state)
            return 1.0
        return 0.1

    def explore(self) -> str:
        # Simula una acción exploratoria
        actions = ["leer documento", "analizar código", "buscar información"]
        return random.choice(actions)
