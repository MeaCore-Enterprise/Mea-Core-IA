"""
Plugin demo: logger
Registra cada mensaje recibido en un archivo local.
"""
import time

LOG_PATH = "data/plugin_logger.log"

_running = True

def run():
    """Inicia el bucle principal del plugin, registrando las entradas del usuario."""
    global _running
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[START] Logger iniciado a {time.ctime()}\n")
        while _running:
            msg = input("[logger] Ingresa mensaje para log (exit para salir): ").strip()
            if msg.lower() == "exit":
                break
            f.write(f"[{time.ctime()}] {msg}\n")
            f.flush()
        f.write(f"[STOP] Logger detenido a {time.ctime()}\n")

def stop():
    """Detiene el bucle principal del plugin."""
    global _running
    _running = False
