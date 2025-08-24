import sys
import os
import json
import numpy as np
from typing import Any, List, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory_store import MemoryStore
from core.ethics import EthicsCore
from core.brain import Brain
from core.remote_logger import RemoteLogger
from core.swarm_controller import SwarmController
from core.knowledge_base import KnowledgeBase
from core.settings_manager import SettingsManager

class CliBot:
    def __init__(self) -> None:
        self.settings_manager = SettingsManager()
        self.responses = self.settings_manager.get_responses()
        self.memory = MemoryStore()
        self.knowledge_base = KnowledgeBase([])
        self.swarm_controller = SwarmController(node_id="cli")
        self.ethics = EthicsCore()
        self.brain = Brain(self.settings_manager.settings, self.responses, memory=self.memory, knowledge_base=self.knowledge_base, swarm_controller=self.swarm_controller)
        self.remote_logger = RemoteLogger(self.settings_manager.settings)
        self.context: List[str] = []
        self.is_running: bool = True
        # Nuevas variables para el sistema de feedback
        self.last_user_input: Optional[str] = None
        self.last_ai_response: Optional[List[str]] = None
        self.feedback_file = os.path.join("data", "feedback_log.jsonl")


    def _save_feedback(self, feedback_type: str, correction: Optional[str] = None):
        """Guarda el feedback del usuario en un archivo JSONL."""
        if not self.last_user_input or not self.last_ai_response:
            print("[Feedback] No hay una conversación reciente para dar feedback.")
            return

        feedback_data = {
            "user_input": self.last_user_input,
            "ai_response": self.last_ai_response,
            "feedback": feedback_type,
            "correction": correction
        }

        try:
            with open(self.feedback_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_data, ensure_ascii=False) + '\n')
            print("[Feedback] ¡Gracias! Tu feedback ha sido guardado.")
        except IOError as e:
            print(f"[Error] No se pudo guardar el feedback: {e}")


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

    def _teach_mode(self):
        """Inicia un ciclo interactivo para enseñar al ActiveLearningModule."""
        learner = self.brain.learning_module
        if not learner or not learner.learner:
            print("[Error] El módulo de aprendizaje activo no está disponible.")
            return

        print("--- Modo de Enseñanza Activa ---")
        print("Se te presentarán muestras y se te pedirá que las etiquetes.")
        print("Escribe 'salir' en cualquier momento para terminar.")

        while True:
            # 1. Obtener la muestra más incierta del pool
            indices, samples = learner.get_uncertain_samples()
            if not samples.any():
                print("No hay más muestras en el pool de aprendizaje. ¡Gracias!")
                break
            
            sample_to_teach = samples[0]
            print(f"\nMuestra a etiquetar: {sample_to_teach}")
            label = input("¿Cuál es la etiqueta correcta para esta muestra? (ej: 0, 1, etc.) >> ").strip().lower()

            if label in ['salir', 'exit', 'quit']:
                print("Saliendo del modo de enseñanza...")
                break
            
            try:
                # 2. Enseñar al modelo con la nueva etiqueta
                learner.teach(indices=indices, labels=np.array([int(label)]))
                print(f"¡Gracias! Modelo actualizado con la nueva información.")
                print(f"Nueva precisión del modelo: {learner.get_model_accuracy():.2f}")
            except (ValueError, TypeError) as e:
                print(f"[Error] Etiqueta no válida. Por favor, introduce un número entero. ({e})")
            except Exception as e:
                print(f"[Error] Ocurrió un error durante la enseñanza: {e}")

    def handle_command(self, q: str) -> bool:
        q_lower = q.lower()

        # --- Nuevos comandos de Feedback ---
        if q_lower == "!buena":
            self._save_feedback("good")
            return True
        if q_lower.startswith("!mala "):
            correction_text = q[len("!mala "):].strip()
            if not correction_text:
                print("[Feedback] Por favor, proporciona una corrección después de !mala.")
            else:
                self._save_feedback("bad", correction=correction_text)
            return True
        # --- Fin de comandos de Feedback ---

        if q_lower == "!settings":
            self._show_settings_menu()
            return True
        if q.startswith("!set "):
            try:
                _, key, *rest = q.split()
                self.memory.set(key, " ".join(rest))
                print(f"[Memoria] {key} = {" ".join(rest)}")
            except ValueError:
                print("[Error] Comando !set mal formado.")
            return True
        if q.startswith("!get "):
            try:
                _, key = q.split()
                print(f"[Memoria] {key} -> {self.memory.get(key) or 'No encontrado'}")
            except ValueError:
                print("[Error] Comando !get mal formado.")
            return True
        if q_lower == "!dump":
            print("[Memoria] Dump completo:", self.memory.dump_all())
            return True
        if q_lower == "!stats":
            print("[Estadísticas]", self.memory.get_stats())
            return True
        if q_lower == "!rules":
            if self.brain.reasoning_engine:
                print("--- Reglas del Motor de Razonamiento ---")
                for name, rule in self.brain.reasoning_engine.get_rules().items():
                    print(f"- {name}: {rule.__doc__ or 'Sin descripción'}")
            else:
                print("[Error] El motor de reglas no está activado.")
            return True
        if q_lower == "!teach":
            self._teach_mode()
            return True
        if q.startswith("!addgoal "):
            try:
                parts = q[len("!addgoal "):].split(';')
                name = parts[0].strip()
                description = parts[1].strip()
                tasks = [t.strip() for t in parts[2].split(',')]
                if self.brain.goal_manager.add_goal(name, description, tasks):
                    print(f"[Metas] Nueva meta añadida: '{name}'")
                else:
                    print(f"[Error] No se pudo añadir la meta. ¿Quizás ya existe?")
            except IndexError:
                print("[Error] Comando !addgoal mal formado. Uso: !addgoal <nombre>; <descripción>; <tarea1>,<tarea2>,...")
            return True
        if q_lower == "!goals":
            active_goals = self.brain.goal_manager.list_goals('active')
            completed_goals = self.brain.goal_manager.list_goals('completed')
            print("--- Metas Activas ---")
            if not active_goals:
                print("Ninguna.")
            else:
                for goal in active_goals:
                    print(f"- {goal['name']} ({goal['progress']:.0f}%): {goal['description']}")
            print("\n--- Metas Completadas ---")
            if not completed_goals:
                print("Ninguna.")
            else:
                for goal in completed_goals:
                    print(f"- {goal['name']}")
            return True
        if q.startswith("!taskdone "):
            try:
                _, goal_name, task_name = q.split(maxsplit=2)
                if self.brain.goal_manager.complete_task(goal_name.strip(), task_name.strip()):
                    print(f"[Metas] Tarea '{task_name}' marcada como completada en la meta '{goal_name}'.")
                else:
                    print("[Error] No se pudo marcar la tarea como completada.")
            except ValueError:
                print("[Error] Comando !taskdone mal formado. Uso: !taskdone <nombre_meta> <nombre_tarea>")
            return True
        return False

    def setup(self) -> None:
        instance_id = self.memory.get_instance_id()
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
        
        # Guardar la interacción para el feedback
        self.last_user_input = q
        self.last_ai_response = respuestas

        for respuesta in respuestas:
            print(respuesta)
            
        self.memory.log_conversation(user_input=q, bot_output=respuestas)
        self.remote_logger.log(user_input=q, bot_output=respuestas)
        self.context.append(q)

    def run(self) -> None:
        self.setup()
        while self.is_running:
            try:
                if hasattr(self.swarm_controller, 'run_replication_cycle'):
                    self.swarm_controller.run_replication_cycle()
                q = input(">>").strip()
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
