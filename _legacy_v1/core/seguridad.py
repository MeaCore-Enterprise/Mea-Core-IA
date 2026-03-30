"""
Módulo de seguridad y autoprotección para MEA-Core-IA.

Este módulo contiene funcionalidades básicas para la detección de amenazas
y el registro de eventos de seguridad.
"""
from typing import List

class SecurityModule:
    """Proporciona métodos para la detección y gestión de amenazas.

    Actualmente, implementa una detección de amenazas muy simple basada en
    palabras clave, pero está diseñado para ser extendido con lógicas más
    robustas.
    """
    def __init__(self) -> None:
        """Inicializa el módulo de seguridad y la lista de amenazas detectadas."""
        self.threats: List[str] = []

    def detect_threat(self, event: str) -> bool:
        """Analiza una cadena de texto para detectar una posible amenaza.

        Si la palabra "ataque" está en el evento, se considera una amenaza,
        se registra y devuelve True.

        Args:
            event (str): La cadena de texto que describe el evento a analizar.

        Returns:
            bool: True si se detecta una amenaza, False en caso contrario.
        """
        if "ataque" in event.lower():
            self.threats.append(event)
            return True
        return False

    def get_threats(self) -> List[str]:
        """Devuelve la lista de todas las amenazas detectadas en la sesión.

        Returns:
            List[str]: Una lista de cadenas, donde cada una es una amenaza registrada.
        """
        return self.threats

# Ejemplo de uso:
# sec = SecurityModule()
# print(sec.detect_threat("ataque de red"))
# print(sec.get_threats())
