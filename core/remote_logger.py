from typing import List, Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class RemoteLogger:
    """
    Gestiona el envío de conversaciones a un servidor remoto.
    """
    def __init__(self, settings: Dict[str, Any]):
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
        """Si está activado, envía la conversación al servidor."""
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