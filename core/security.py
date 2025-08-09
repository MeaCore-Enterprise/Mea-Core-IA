"""
Módulo de seguridad y autoprotección para MEA-Core-IA.
"""

"""
Módulo de seguridad y autoprotección para MEA-Core-IA.
"""
from typing import List

class SecurityModule:
    """
    Módulo de seguridad: detecta y almacena amenazas.
    """
    def __init__(self) -> None:
        self.threats: List[str] = []

    def detect_threat(self, event: str) -> bool:
        """Devuelve True si detecta una amenaza en el evento."""
        if "ataque" in event.lower():
            self.threats.append(event)
            return True
        return False

    def get_threats(self) -> List[str]:
        """Devuelve la lista de amenazas detectadas."""
        return self.threats

# Ejemplo de uso:
# sec = SecurityModule()
# print(sec.detect_threat("ataque de red"))
# print(sec.get_threats())
