"""
Loader minimal para plugins: descubre módulos en ./plugins,
los carga en hilos controlados y aplica límites básicos.
Diseñado para entornos con pocos recursos.
"""

import importlib
import os
import sys
import threading
import traceback
from types import ModuleType
from typing import Dict, Optional, Any

PLUGINS_DIR: str = os.path.join(os.path.dirname(__file__), "..", "plugins")


class PluginHandle:
    def __init__(self, name: str, module: ModuleType) -> None:
        self.name: str = name
        self.module: ModuleType = module
        self.thread: Optional[threading.Thread] = None


class CoreLoader:
    def __init__(self) -> None:
        self.plugins: Dict[str, PluginHandle] = {}

    def discover(self) -> list[str]:
        if not os.path.exists(PLUGINS_DIR):
            os.makedirs(PLUGINS_DIR)
        files: list[str] = [f for f in os.listdir(PLUGINS_DIR) if f.endswith(".py")]
        return [os.path.splitext(f)[0] for f in files]

    def load(self, plugin_name: str) -> Optional[PluginHandle]:
        try:
            spec_name: str = f"plugins.{plugin_name}"
            if spec_name in sys.modules:
                importlib.reload(sys.modules[spec_name])
                module: ModuleType = sys.modules[spec_name]
            else:
                module: ModuleType = importlib.import_module(spec_name)
            handle = PluginHandle(plugin_name, module)
            self.plugins[plugin_name] = handle
            return handle
        except Exception:
            traceback.print_exc()
            return None

    def start(self, plugin_name: str, *args: Any, **kwargs: Any) -> bool:
        handle: Optional[PluginHandle] = self.plugins.get(plugin_name) or self.load(plugin_name)
        if not handle:
            return False
        if hasattr(handle.module, "run"):
            def runner() -> None:
                try:
                    handle.module.run(*args, **kwargs)
                except Exception:
                    traceback.print_exc()
            t = threading.Thread(target=runner, name=f"plugin-{plugin_name}", daemon=True)
            handle.thread = t
            t.start()
            return True
        return False

    def stop(self, plugin_name: str) -> bool:
        # Plugin should manage su propio stop signal; aquí solo da hint.
        handle: Optional[PluginHandle] = self.plugins.get(plugin_name)
        if handle and hasattr(handle.module, "stop"):
            try:
                handle.module.stop()
                return True
            except Exception:
                traceback.print_exc()
        return False
