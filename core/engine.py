# core/engine.py

import json
import os

CONFIG_PATH = "data/config.json"

class MEAEngine:
    def __init__(self):
        self.config = {}
        self.commands = {
            "saludar": self.saludar,
            "ayuda": self.mostrar_ayuda,
            "salir": self.salir
        }

    def cargar_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                self.config = json.load(f)
        else:
            print("[!] Archivo de configuración no encontrado.")

    def saludar(self):
        nombre = self.config.get("nombre", "Usuario")
        print(f"👋 ¡Hola, {nombre}! Soy MEA-Core IA.")

    def mostrar_ayuda(self):
        print("🧠 Comandos disponibles:")
        for comando in self.commands:
            print(f" - {comando}")

    def salir(self):
        print("👋 Cerrando MEA-Core IA. ¡Hasta luego!")
        exit()

    def ejecutar(self):
        print("📦 Cargando MEA-Core IA...")
        self.cargar_config()

        while True:
            entrada = input(">> ").strip().lower()
            if entrada in self.commands:
                self.commands[entrada]()
            else:
                print("❌ Comando no reconocido. Escribe 'ayuda' para ver opciones.")

if __name__ == "__main__":
    motor = MEAEngine()
    motor.ejecutar()
