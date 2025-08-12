import sys
import os
import json
from typing import Any, List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory import MemoryStore
from core.ethics import EthicsCore
from core.brain import Brain
from core.remote_logger import RemoteLogger
from core.swarm import SwarmController
from core.settings_manager import SettingsManager

class CliBot:
    def __init__(self) -> None:
        self.settings_manager = SettingsManager()
        self.responses = self.settings_manager.get_responses()
        self.mem: MemoryStore = MemoryStore()
        self.ethics: EthicsCore = EthicsCore()
        self.brain: Brain = Brain(self.settings_manager.settings, self.responses)
        self.remote_logger: RemoteLogger = RemoteLogger(self.settings_manager.settings)
        self.swarm_controller: SwarmController = SwarmController(self.settings_manager.settings, self.mem)
        self.context: List[str] = []
        self.is_running: bool = True

    def _show_settings_menu(self):
        while True:
            remote_enabled = self.remote_logger.enabled
            swarm_enabled = self.swarm_controller.replication_enabled
            print("\n--- Submenú de Configuración ---")
            print(f"1. Aprendizaje Remoto      : {'ACTIVADO' if remote_enabled else 'DESACTIVADO'}")
            print(f"2. Replicación en Enjambre : {'ACTIVADA' if swarm_enabled else 'DESACTIVADA'}")
            print("Escribe '1' o '2' para cambiar la opción, o 'salir' para volver.")
            choice = input("Opción >> ").strip().lower()
            if choice == '1':
                new_status = not remote_enabled
                self.settings_manager.set_value('remote_learning.enabled', new_status)
                self.remote_logger.enabled = new_status
                print(f"El Aprendizaje Remoto ha sido {'ACTIVADO' if new_status else 'DESACTIVADO'}.")
            elif choice == '2':
                new_status = not swarm_enabled
                self.settings_manager.set_value('swarm.replication_enabled', new_status)
                self.swarm_controller.replication_enabled = new_status
                print(f"La Replicación en Enjambre ha sido {'ACTIVADA' if new_status else 'DESACTIVADA'}.")
            elif choice in ['salir', 'exit', 'quit']:
                print("Volviendo a la conversación...")
                break
            else:
                print("Opción no válida.")

    def handle_command(self, q: str) -> bool:
        q_lower = q.lower()
        if q_lower == "!settings":
            self._show_settings_menu()
            return True
        if q.startswith("!set "):
            try:
                _, key, *rest = q.split()
                self.mem.set(key, " ".join(rest))
                print(f"[Memoria] {key} = {" ".join(rest)}")
            except ValueError:
                print("[Error] Comando !set mal formado.")
            return True
        if q.startswith("!get "):
            try:
                _, key = q.split()
                print(f"[Memoria] {key} -> {self.mem.get(key) or 'No encontrado'}")
            except ValueError:
                print("[Error] Comando !get mal formado.")
            return True
        if q_lower == "!dump":
            print("[Memoria] Dump completo:", self.mem.dump_all())
            return True
        return False

    def setup(self) -> None:
        instance_id = self.mem.get_instance_id()
        print(f"--- Iniciando Mea-Core (ID: {instance_id[:8]}) ---")
        if self.remote_logger.enabled:
            print("[INFO] Aprendizaje remoto: ACTIVADO")
        else:
            print("[INFO] Aprendizaje remoto: DESACTIVADO")
        if self.swarm_controller.replication_enabled:
            print("[INFO] Replicación de enjambre: ACTIVADA")
        else:
            print("[INFO] Replicación de enjambre: DESACTIVADA")
        print(f"--- {self.brain.get_greeting()} ---")

    def process_input(self, q: str) -> None:
        if self.handle_command(q):
            return
        if not self.ethics.check_action(q):
            print(f"[Ética] {self.ethics.explain_decision(q)}")
            return
        respuestas = self.brain.get_response(q)
        for respuesta in respuestas:
            print(respuesta)
        self.mem.log_conversation(user_input=q, bot_output=respuestas)
        self.remote_logger.log(user_input=q, bot_output=respuestas)
        self.context.append(q)

    def run(self) -> None:
        self.setup()
        while self.is_running:
            try:
                self.swarm_controller.run_replication_cycle()
                q = input(">> ").strip()
                if q.lower() in {"exit", "quit", "salir"}:
                    print(self.brain.get_farewell())
                    self.is_running = False
                    continue
                if q:
                    self.process_input(q)
            except (EOFError, KeyboardInterrupt):
                print(f"\n{self.brain.get_farewell()}")
                self.is_running = False

if __name__ == "__main__":
    bot = CliBot()
    bot.run()