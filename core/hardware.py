"""
Módulo de integración de hardware para MEA-Core-IA.

Este módulo está diseñado para gestionar la información y el estado de
dispositivos de hardware externos con los que la IA podría interactuar.
"""
from typing import Dict, Any

class HardwareModule:
    """Gestiona un registro de dispositivos de hardware y su información.

    Actúa como una capa de abstracción simple para que el núcleo de la IA
    pueda ser consciente del hardware disponible.
    """
    def __init__(self) -> None:
        """Inicializa el módulo de hardware.
        
        Crea un diccionario para almacenar los dispositivos registrados.
        """
        self.devices: Dict[str, Any] = {}

    def add_device(self, name: str, info: Any) -> None:
        """Agrega un dispositivo y su información al registro.

        Args:
            name (str): El nombre del dispositivo (ej. "Raspberry Pi").
            info (Any): Un objeto o diccionario con información sobre el dispositivo
                        (ej. {"ip": "192.168.1.10"}).
        """
        self.devices[name] = info

    def get_devices(self) -> Dict[str, Any]:
        """Devuelve un diccionario con todos los dispositivos registrados.

        Returns:
            Dict[str, Any]: Un diccionario de los dispositivos.
        """
        return self.devices

# Ejemplo de uso:
# hw = HardwareModule()
# hw.add_device("Raspberry Pi", {"ip": "192.168.1.10"})
# print(hw.get_devices())
