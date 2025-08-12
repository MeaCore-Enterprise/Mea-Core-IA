import json
from typing import Dict, Any

SETTINGS_PATH = "config/settings.json"
RESPONSES_PATH = "config/responses.json"

class SettingsManager:
    """
    Gestiona la carga y guardado de la configuración y respuestas del bot.
    """
    def __init__(self, settings_path: str = SETTINGS_PATH, responses_path: str = RESPONSES_PATH):
        self.settings_path = settings_path
        self.responses_path = responses_path
        self.settings = self._load_settings()
        self.responses = self._load_responses()

    def _load_settings(self) -> Dict[str, Any]:
        """Carga el archivo de configuración."""
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] No se encontró el archivo de configuración en {self.settings_path}")
            return {}

    def _load_responses(self) -> Dict[str, Any]:
        """Carga el archivo de respuestas."""
        try:
            with open(self.responses_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] No se encontró el archivo de respuestas en {self.responses_path}")
            return {}

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de la configuración."""
        return self.settings.get(key, default)

    def get_responses(self) -> Dict[str, Any]:
        """Obtiene el diccionario de respuestas."""
        return self.responses

    def set_value(self, key_path: str, value: Any):
        """Establece un valor en una ruta de claves anidadas (ej. 'swarm.replication_enabled')."""
        keys = key_path.split('.')
        data = self.settings
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value
        self._save_settings()

    def _save_settings(self):
        """Guarda la configuración actual en el archivo JSON."""
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"[ERROR] No se pudo guardar la configuración en {self.settings_path}: {e}")