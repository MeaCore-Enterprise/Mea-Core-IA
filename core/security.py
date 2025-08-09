"""
Módulo de seguridad y autoprotección para MEA-Core-IA.
"""
from typing import List

class SecurityModule:
    def __init__(self) -> None:
        self.threats: List[str] = []

    def detect_threat(self, event: str) -> bool:
        # Simula detección de amenazas
        if "ataque" in event.lower():
            self.threats.append(event)
            return True
        return False

    def get_threats(self) -> List[str]:
        return self.threats
