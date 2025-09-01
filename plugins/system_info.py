# plugins/system_info.py

import platform
import psutil # Se necesitaría añadir 'psutil' a requirements.txt

# --- Funciones del Plugin ---

def get_os_info() -> str:
    """Devuelve información sobre el sistema operativo.""" 
    return f"Sistema: {platform.system()} {platform.release()}"

def get_cpu_usage() -> str:
    """Devuelve el porcentaje de uso de la CPU."""
    return f"Uso de CPU: {psutil.cpu_percent(interval=1)}%"

def get_memory_info() -> str:
    """Devuelve información sobre el uso de la memoria RAM."""
    mem = psutil.virtual_memory()
    return f"RAM Total: {mem.total // (1024**3)} GB, Usada: {mem.percent}%"

# --- Registro de Comandos ---
# El PluginManager buscará esta variable para registrar los comandos.

COMMANDS = {
    "os_info": get_os_info,
    "cpu_usage": get_cpu_usage,
    "memory_info": get_memory_info,
}
