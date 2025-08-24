# core/engine.py

import json
import os
from typing import Any, Callable, Dict

CONFIG_PATH = "data/config.json"

class MEAEngine:
    """Motor principal para una interfaz de línea de comandos (CLI) simple.

    Gestiona la configuración, los comandos disponibles y el bucle principal de
    interacción con el usuario.
    """
    def __init__(self) -> None:
        """Inicializa el motor, preparando el diccionario de configuración y comandos."""
        self.config: Dict[str, Any] = {}
        self.commands: Dict[str, Callable[[], None]] = {
            "saludar": self.saludar,
            "ayuda": self.mostrar_ayuda,
            "salir": self.salir
        }

    def cargar_config(self) -> None:
        """Carga la configuración desde el archivo JSON especificado en CONFIG_PATH."""
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            print("[!] Archivo de configuración no encontrado.")

    def saludar(self) -> None:
        """Imprime un saludo personalizado usando el nombre de la configuración."""
        nombre: str = str(self.config.get("nombre", "Usuario"))
        print(f"¡Hola, {nombre}! Soy MEA-Core IA.")

    def mostrar_ayuda(self) -> None:
        """Muestra en la consola todos los comandos disponibles."""
        print("Comandos disponibles:")
        for comando in self.commands:
            print(f" - {comando}")

    def salir(self) -> None:
        """Imprime un mensaje de despedida y termina la ejecución del programa."""
        print("Cerrando MEA-Core IA. ¡Hasta luego!")
        exit()

    def ejecutar(self) -> None:
        """Inicia el bucle principal del motor.

        Carga la configuración y luego espera continuamente la entrada del usuario
        para ejecutar el comando correspondiente.
        """
        print("Cargando MEA-Core IA...")
        self.cargar_config()

        while True:
            entrada: str = input(">> ").strip().lower()
            if entrada in self.commands:
                self.commands[entrada]()
            else:
                print("Comando no reconocido. Escribe 'ayuda' para ver opciones.")

if __name__ == "__main__":
    motor = MEAEngine()
    motor.ejecutar()
