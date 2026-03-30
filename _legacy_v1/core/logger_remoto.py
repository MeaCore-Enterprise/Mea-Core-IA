from typing import List, Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class RemoteLogger:
    """Gestiona el envío de conversaciones a un servidor remoto para su análisis.

    Esta clase es responsable de enviar los intercambios entre el usuario y el bot
    a un endpoint HTTP si la funcionalidad está activada en la configuración.
    Es tolerante a fallos: se desactiva si la librería `requests` no está
    instalada o si la URL del servidor no está configurada.
    """
    def __init__(self, settings: Dict[str, Any]):
        """Inicializa el logger remoto a partir de la configuración.

        Args:
            settings (Dict[str, Any]): El diccionario de configuración principal
                                      del que se extraerá la sección `remote_learning`.
        """
        self.config = settings.get("remote_learning", {})
        self.enabled = self.config.get("enabled", False)
        self.server_url = self.config.get("server_url")

        if self.enabled and not self.server_url:
            print("[Advertencia] El aprendizaje remoto está activado pero no se ha configurado 'server_url'.")
            self.enabled = False
        
        if self.enabled and not REQUESTS_AVAILABLE:
            print("[Advertencia] El módulo 'requests' no está instalado. El aprendizaje remoto se ha desactivado.")
            print("             Para usar esta función, ejecuta: pip install requests")
            self.enabled = False

    def log(self, user_input: str, bot_output: List[str]):
        """Si está activado, envía la conversación al servidor remoto vía POST.

        Args:
            user_input (str): La entrada del usuario.
            bot_output (List[str]): La respuesta del bot (como lista de cadenas).
        """
        if not self.enabled or not REQUESTS_AVAILABLE:
            return

        payload = {
            "user_input": user_input,
            "bot_output": bot_output
        }

        try:
            response = requests.post(self.server_url, json=payload, timeout=5)
            if response.status_code != 200:
                print(f"[Error de Aprendizaje Remoto] El servidor devolvió el código de estado {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[Error de Aprendizaje Remoto] No se pudo conectar al servidor: {e}")
