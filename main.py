import sys
import os
import subprocess
import time
import json
import logging

# --- Configuración del Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# --- Comprobación y Configuración Automática ---

def install_requirements():
    """Instala dependencias si no están presentes."""
    logging.info("Verificando dependencias...")
    try:
        # Ocultar la salida si todo está bien para un arranque más limpio
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("Dependencias verificadas.")
    except subprocess.CalledProcessError:
        logging.error("Falló la instalación de dependencias. Por favor, ejecuta 'pip install -r requirements.txt' manualmente.")
        sys.exit(1)

def initialize_knowledge_base():
    """Inicializa la base de conocimiento si es necesario."""
    kb_path = os.path.join("data", "knowledge_base.db")
    if not os.path.exists(kb_path):
        logging.info("Base de conocimiento no encontrada. Inicializando...")
        try:
            from tools.import_manifestos import main as import_main
            import_main()
            logging.info("Base de conocimiento inicializada con éxito.")
        except Exception as e:
            logging.error(f"No se pudo inicializar la base de conocimiento: {e}")
            sys.exit(1)

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
        logging.info("El servidor central ya está en ejecución.")
    except requests.ConnectionError:
        logging.info("Servidor central no detectado. Iniciando en segundo plano...")
        try:
            # Iniciar el servidor como un proceso separado
            subprocess.Popen([sys.executable, "-m", "uvicorn", "server.main:app"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2) # Darle un par de segundos para que arranque
            logging.info("Servidor iniciado.")
        except Exception as e:
            logging.error(f"No se pudo iniciar el servidor automáticamente: {e}")
            logging.warning("Por favor, inícialo manualmente en otra terminal con: uvicorn server.main:app")

# --- Punto de Entrada Principal ---

def main():
    """
    Punto de entrada principal que automatiza todo e inicia el bot.
    """
    logging.info("--- Verificando entorno de Mea-Core ---")
    install_requirements()
    initialize_knowledge_base()

    try:
        # Cargar settings para decidir si iniciar el servidor
        from core.gestor_configuracion import SettingsManager
        settings_manager = SettingsManager()
        settings = settings_manager.settings
        
        if not settings:
            logging.error("No se pudo cargar la configuración. Revisa el archivo 'config/settings.json'.")
            sys.exit(1)
            
        start_server_if_needed(settings)

        logging.info("--- Entorno verificado. Iniciando IA... ---")
        from bots.cli_bot import CliBot
        bot = CliBot()
        bot.run()

    except FileNotFoundError as e:
        logging.error(f"Archivo crítico no encontrado: {e}. Asegúrate de que todos los archivos de configuración y datos estén en su lugar.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Error al leer un archivo de configuración JSON: {e}. Revisa la sintaxis.")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Ocurrió un error fatal durante la inicialización de la IA: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
