import json
from typing import Dict, Any

SETTINGS_PATH = "config/settings.json"
RESPONSES_PATH = "config/responses.json"

class SettingsManager:
    """Gestiona la carga y el guardado de archivos de configuración JSON.

    Esta clase centraliza el acceso a los archivos de configuración principales
    del proyecto, como `settings.json` y `responses.json`.
    """
    def __init__(self, settings_path: str = SETTINGS_PATH, responses_path: str = RESPONSES_PATH):
        """Inicializa el gestor de configuración.

        Args:
            settings_path (str): Ruta al archivo de configuración principal.
            responses_path (str): Ruta al archivo de respuestas del bot.
        """
        self.settings_path = settings_path
        self.responses_path = responses_path
        self.settings = self._load_settings()
        self.responses = self._load_responses()

    def _load_settings(self) -> Dict[str, Any]:
        """(Privado) Carga el archivo de configuración desde la ruta especificada.

        Returns:
            Dict[str, Any]: Un diccionario con la configuración o un diccionario vacío si falla.
        """
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[Advertencia] No se encontró el archivo de configuración en {self.settings_path}. Se usarán valores por defecto.")
            return {}
        except json.JSONDecodeError:
            print(f"[ERROR] El archivo de configuración en {self.settings_path} está corrupto. Se usarán valores por defecto.")
            return {}

    def _load_responses(self) -> Dict[str, Any]:
        """(Privado) Carga el archivo de respuestas desde la ruta especificada.

        Returns:
            Dict[str, Any]: Un diccionario con las respuestas o un diccionario vacío si falla.
        """
        try:
            with open(self.responses_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[Advertencia] No se encontró el archivo de respuestas en {self.responses_path}. Se usarán valores por defecto.")
            return {}
        except json.JSONDecodeError:
            print(f"[ERROR] El archivo de respuestas en {self.responses_path} está corrupto. Se usarán valores por defecto.")
            return {}

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de la configuración por su clave.

        Args:
            key (str): La clave a buscar en la configuración.
            default (Any, optional): El valor a devolver si la clave no se encuentra. Defaults to None.

        Returns:
            Any: El valor asociado a la clave, o el valor por defecto.
        """
        return self.settings.get(key, default)

    def get_responses(self) -> Dict[str, Any]:
        """Obtiene el diccionario completo de respuestas.

        Returns:
            Dict[str, Any]: El diccionario de respuestas.
        """
        return self.responses

    def set_value(self, key_path: str, value: Any):
        """Establece un valor en la configuración usando una ruta de claves anidadas.

        Permite modificar valores anidados especificando la ruta con puntos.
        Ejemplo: `set_value('swarm.replication_enabled', True)`

        Args:
            key_path (str): La ruta de claves anidadas, separadas por puntos.
            value (Any): El nuevo valor a establecer.
        """
        keys = key_path.split('.')
        data = self.settings
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value
        self._save_settings()

    def _save_settings(self):
        """(Privado) Guarda la configuración actual en el archivo JSON.

        La configuración se guarda con una indentación de 2 espacios para legibilidad.
        """
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"[ERROR] No se pudo guardar la configuración en {self.settings_path}: {e}")
