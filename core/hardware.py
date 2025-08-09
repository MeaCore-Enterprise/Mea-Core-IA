"""
Módulo de integración de hardware y diseño generativo para MEA-Core-IA.
"""
from typing import Dict, Any

class HardwareModule:
    def __init__(self) -> None:
        self.devices: Dict[str, Any] = {}

    def add_device(self, name: str, info: Any) -> None:
        self.devices[name] = info

    def get_devices(self) -> Dict[str, Any]:
        return self.devices
