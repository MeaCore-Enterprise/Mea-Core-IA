# core/engine.py


import json
import os
from typing import Any, Callable, Dict

CONFIG_PATH = "data/config.json"


class MEAEngine:
    def __init__(self) -> None:
        self.config: Dict[str, Any] = {}
        self.commands: Dict[str, Callable[[], None]] = {
            "saludar": self.saludar,
            "ayuda": self.mostrar_ayuda,
            "salir": self.salir
        }

    def cargar_config(self) -> None:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            print("[!] Archivo de configuración no encontrado.")

    def saludar(self) -> None:
        nombre: str = str(self.config.get("nombre", "Usuario"))
        print(f"¡Hola, {nombre}! Soy MEA-Core IA.")

    def mostrar_ayuda(self) -> None:
        print("Comandos disponibles:")
        for comando in self.commands:
            print(f" - {comando}")

    def salir(self) -> None:
        print("Cerrando MEA-Core IA. ¡Hasta luego!")
        exit()


    def ejecutar(self) -> None:
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
