
import json
from typing import Dict, Any

SETTINGS_PATH = "config/settings.json"

class SettingsManager:
    """
    Gestiona la carga y guardado de la configuración del bot.
    """
    def __init__(self, path: str = SETTINGS_PATH):
        self.path = path
        self.settings = self._load()

    def _load(self) -> Dict[str, Any]:
        """Carga el archivo de configuración."""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] No se encontró el archivo de configuración en {self.path}")
            # Devolver un diccionario vacío o una configuración por defecto si no se encuentra
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de la configuración."""
        return self.settings.get(key, default)

    def set_value(self, key_path: str, value: Any):
        """Establece un valor en una ruta de claves anidadas (ej. 'swarm.replication_enabled')."""
        keys = key_path.split('.')
        data = self.settings
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value
        self._save()

    def _save(self):
        """Guarda la configuración actual en el archivo JSON."""
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"[ERROR] No se pudo guardar la configuración en {self.path}: {e}")
