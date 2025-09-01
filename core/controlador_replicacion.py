"""
Módulo para la replicación del sistema MEA-Core en otros dispositivos.

Este módulo se encarga de detectar dispositivos externos (como unidades USB)
y copiar en ellos una versión funcional del sistema, generando una nueva
identidad para el clon.
"""
import os
import shutil
import uuid
import json
import time
from typing import List, Dict, Any

# --- Importación corregida ---
from core.memoria import MemoryStore

# Se asume que el código fuente está en el directorio padre del directorio 'core'
SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ReplicationController:
    """Gestiona la replicación (clonación) del sistema a nuevos dispositivos."""
    
    def __init__(self, settings: Dict[str, Any], memory: MemoryStore):
        """Inicializa el controlador de replicación.

        Args:
            settings (Dict[str, Any]): El diccionario de configuración del sistema.
            memory (MemoryStore): La instancia de MemoryStore para registrar eventos.
        """
        self.config = settings.get("swarm", {})
        self.replication_enabled = self.config.get("replication_enabled", False)
        self.scan_interval = self.config.get("scan_interval_seconds", 60)
        self.last_scan_time = 0
        self.memory = memory

    def _get_potential_devices(self) -> List[str]:
        """(Privado) Busca dispositivos externos (ej. unidades USB).

        Returns:
            List[str]: Una lista de rutas a los dispositivos potenciales.
        """
        # Esta es una simulación/ejemplo. En un sistema real, esto sería más complejo
        # y adaptado para cada SO (ej. /media/ para Linux, /Volumes/ para macOS).
        potential_drives = []
        if os.name == 'nt': # Para Windows
            import string
            available_drives = [f'{d}:\\' for d in string.ascii_uppercase if os.path.exists(f'{d}:\\')]
            # Excluir la unidad del sistema
            system_drive = os.environ.get("SystemDrive", "C:").upper()
            # --- Sintaxis corregida ---
            potential_drives = [d for d in available_drives if d.upper() != (system_drive + "\\")]
        # Aquí se añadiría la lógica para Linux y macOS
        return potential_drives

    def _generate_identity(self, parent_id: str) -> Dict[str, Any]:
        """(Privado) Genera una identidad única para un nuevo clon."""
        return {
            "id": str(uuid.uuid4()),
            "parent_id": parent_id,
            "created_at": time.time(),
            "version": "1.0.0" # Podría obtenerse del código fuente
        }

    def replicate_to_device(self, device_path: str):
        """Clona el sistema Mea-Core a un nuevo dispositivo."""
        target_dir = os.path.join(device_path, "Mea-Core_Clone")
        print(f"[Replicator] Detectado dispositivo potencial en {device_path}. Intentando replicar en {target_dir}...")

        try:
            # Evitar replicar dentro de un clon existente o del propio proyecto
            if os.path.exists(os.path.join(target_dir, "mea_identity.json")) or os.path.samefile(SOURCE_DIR, target_dir):
                print("[Replicator] El directorio de destino ya es una instancia de Mea-Core. Replicación cancelada.")
                return

            # Copiar todo el directorio del proyecto
            shutil.copytree(SOURCE_DIR, target_dir, ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.git*', 'Otras IA'))

            # Crear el archivo de identidad del clon
            parent_id = self.memory.get_instance_id()
            identity = self._generate_identity(parent_id)
            with open(os.path.join(target_dir, "mea_identity.json"), "w") as f:
                json.dump(identity, f, indent=2)

            # Registrar la creación del clon en la memoria del padre
            # --- Corregido para usar el nuevo método log_episode ---
            self.memory.log_episode(
                type='replication',
                source='replication_controller',
                data={'clone_id': identity['id'], 'path': target_dir}
            )
            
            print(f"[Replicator] ¡Éxito! Mea-Core replicado en {target_dir} con ID: {identity['id']}")

        except FileExistsError:
            print(f"[Replicator] El directorio {target_dir} ya existe. Replicación cancelada.")
        except Exception as e:
            print(f"[Replicator] Error durante la replicación a {device_path}: {e}")

    def run_replication_cycle(self):
        """Ciclo principal que busca dispositivos y se replica si está activado."""
        if not self.replication_enabled:
            return
        
        if time.time() - self.last_scan_time < self.scan_interval:
            return

        print("[Replicator] Buscando nuevos dispositivos para expansión...")
        self.last_scan_time = time.time()
        devices = self._get_potential_devices()
        
        if not devices:
            print("[Replicator] No se encontraron nuevos dispositivos.")
            return

        for device in devices:
            self.replicate_to_device(device)