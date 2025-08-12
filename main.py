import sys
import os
import subprocess
import time
import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# --- Comprobación y Configuración Automática ---

def install_requirements():
    """Instala dependencias si no están presentes."""
    print("[Setup] Verificando dependencias...")
    try:
        # Ocultar la salida si todo está bien para un arranque más limpio
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[Setup] Dependencias verificadas.")
    except subprocess.CalledProcessError:
        print("[ERROR] Falló la instalación de dependencias.")
        sys.exit(1)

def initialize_knowledge_base():
    """Inicializa la base de conocimiento si es necesario."""
    kb_path = os.path.join("data", "knowledge_base.db")
    if not os.path.exists(kb_path):
        print("[Setup] Inicializando base de conocimiento...")
        from tools.import_manifestos import main as import_main
        import_main()

def start_server_if_needed(settings: dict):
    """Inicia el servidor FastAPI en segundo plano si está configurado y no está corriendo."""
    remote_config = settings.get("remote_learning", {})
    if not remote_config.get("enabled", False):
        return

    server_url = remote_config.get("server_url", "")
    if not server_url or not REQUESTS_AVAILABLE:
        return

    try:
        # Intentar conectar con el servidor para ver si ya está activo
        requests.get(server_url.replace("/api/learn", "/docs"), timeout=1)
        print("[Setup] El servidor central ya está en ejecución.")
    except requests.ConnectionError:
        print("[Setup] Servidor central no detectado. Iniciando en segundo plano...")
        try:
            # Iniciar el servidor como un proceso separado
            subprocess.Popen([sys.executable, "-m", "uvicorn", "server.main:app"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2) # Darle un par de segundos para que arranque
            print("[Setup] Servidor iniciado.")
        except Exception as e:
            print(f"[ERROR] No se pudo iniciar el servidor automáticamente: {e}")
            print("         Por favor, inícialo manualmente en otra terminal con: uvicorn server.main:app")

# --- Punto de Entrada Principal ---

def main():
    """
    Punto de entrada principal que automatiza todo e inicia el bot.
    """
    print("--- Verificando entorno de Mea-Core ---")
    install_requirements()
    initialize_knowledge_base()

    # Cargar settings para decidir si iniciar el servidor
    from core.settings_manager import SettingsManager
    settings_manager = SettingsManager()
    settings = settings_manager.settings
    if settings:
        start_server_if_needed(settings)

    print("--- Entorno verificado. Iniciando IA... ---")
    from bots.cli_bot import CliBot
    bot = CliBot()
    bot.run()

if __name__ == "__main__":
    main()