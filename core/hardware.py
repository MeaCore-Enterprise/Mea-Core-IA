"""
Módulo de integración de hardware y diseño generativo para MEA-Core-IA.
"""

"""
Módulo de integración de hardware y diseño generativo para MEA-Core-IA.
"""
from typing import Dict, Any

class HardwareModule:
    """
    Módulo de hardware: gestiona dispositivos y su información.
    """
    def __init__(self) -> None:
        self.devices: Dict[str, Any] = {}

    def add_device(self, name: str, info: Any) -> None:
        """Agrega un dispositivo con su información."""
        self.devices[name] = info

    def get_devices(self) -> Dict[str, Any]:
        """Devuelve todos los dispositivos registrados."""
        return self.devices

# Ejemplo de uso:
# hw = HardwareModule()
# hw.add_device("Raspberry Pi", {"ip": "192.168.1.10"})
# print(hw.get_devices())
