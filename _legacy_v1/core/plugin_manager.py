# core/plugin_manager.py

import os
import importlib
from typing import List, Dict, Any, Callable

PLUGIN_DIR = "plugins"

class PluginManager:
    """
    Descubre, carga y gestiona plugins externos de forma dinámica.
    """
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.commands: Dict[str, Callable] = {}
        self.load_plugins()

    def load_plugins(self):
        """
        Busca y carga todos los módulos de plugin válidos desde el directorio de plugins.
        """
        if not os.path.isdir(PLUGIN_DIR):
            return

        for filename in os.listdir(PLUGIN_DIR):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"{PLUGIN_DIR}.{module_name}")
                    self.plugins[module_name] = module
                    print(f"[PluginManager] Plugin '{module_name}' cargado exitosamente.")
                    self._register_plugin_commands(module)
                except Exception as e:
                    print(f"[PluginManager] Error al cargar el plugin '{module_name}': {e}")

    def _register_plugin_commands(self, module: Any):
        """
        Registra los comandos que un plugin expone.
        Un plugin debe tener una variable `COMMANDS` que es un diccionario.
        """
        if hasattr(module, "COMMANDS") and isinstance(module.COMMANDS, dict):
            for command_name, function in module.COMMANDS.items():
                if callable(function):
                    self.commands[command_name] = function
                    print(f"  -> Comando registrado: '{command_name}'")
                else:
                    print(f"  -> Advertencia: El comando '{command_name}' no es una función válida.")

    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """
        Ejecuta un comando de un plugin si existe.
        """
        if command_name in self.commands:
            try:
                return self.commands[command_name](*args, **kwargs)
            except Exception as e:
                return f"Error al ejecutar el comando '{command_name}': {e}"
        else:
            return f"Comando '{command_name}' no encontrado."

    def list_commands(self) -> List[str]:
        """
        Devuelve una lista de todos los comandos disponibles.
        """
        return list(self.commands.keys())

if __name__ == '__main__':
    # Para probar, necesitaríamos crear un plugin de ejemplo en la carpeta /plugins
    # Por ejemplo, plugins/system_info.py
    
    print("--- Demo del Gestor de Plugins ---")
    # Suponiendo que el plugin de ejemplo existe y se ha cargado:
    
    # 1. Crear un plugin de ejemplo falso para la demo
    from unittest.mock import MagicMock
    mock_plugin_module = MagicMock()
    def get_cpu_usage(): return "CPU: 45%"
    def get_ram_usage(): return "RAM: 60%"
    mock_plugin_module.COMMANDS = {
        "get_cpu": get_cpu_usage,
        "get_ram": get_ram_usage
    }

    # 2. Iniciar el gestor y registrar el plugin falso
    manager = PluginManager()
    manager._register_plugin_commands(mock_plugin_module)

    # 3. Probar la ejecución de comandos
    print(f"Comandos disponibles: {manager.list_commands()}")
    cpu = manager.execute_command("get_cpu")
    ram = manager.execute_command("get_ram")
    print(f"Resultado de get_cpu: {cpu}")
    print(f"Resultado de get_ram: {ram}")
    
    # 4. Probar un comando inexistente
    error_msg = manager.execute_command("get_disk")
    print(f"Resultado de get_disk: {error_msg}")
