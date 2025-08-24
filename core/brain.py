import json
import os
import random
from typing import Any, Dict, List, Optional
from core.memory_consolidator import MemoryConsolidator
from core.rules_engine import RulesEngine

from core.knowledge_base import KnowledgeBase
from core.evolution import ActiveLearningModule
from core.goals import GoalManager
from core.memory_store import MemoryStore
from core.swarm_controller import SwarmController

# Intentar importar scikit-learn y manejar el fallo si no está instalado
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# --- Integración del Motor de Reglas ---
try:
    from experta import *
    EXPERTA_AVAILABLE = True
except ImportError:
    EXPERTA_AVAILABLE = False

# Definición de Hechos para el motor de reglas
class UserInput(Fact):
    """Hecho que representa la entrada del usuario."""
    pass

class BotAction(Fact):
    """Hecho que representa una acción que el bot debe tomar."""
    pass

class NeedsLearning(Fact):
    """Hecho que indica que la entrada actual es una oportunidad de aprendizaje."""
    pass

class ReviewGoals(Fact):
    """Hecho que dispara la revisión de metas activas."""
    pass

class ReasoningEngine(KnowledgeEngine):
    """Motor de razonamiento basado en reglas para MEA-Core."""
    def __init__(self, responses, brain_instance):
        super().__init__()
        self.responses = responses
        self.brain = brain_instance # Referencia al cerebro para acceder a otros módulos
        self.response_generated = False
        self.interaction_counter = 0

    @DefFacts()
    def _initial_facts(self):
        yield Fact(action="greet")

    @Rule(UserInput(text=MATCH.text))
    def handle_input(self, text):
        print(f"[Motor de Reglas] Hecho recibido: UserInput(text='{text}')")
        self.interaction_counter += 1
        if self.interaction_counter % 5 == 0: # Revisar metas cada 5 interacciones
            self.declare(ReviewGoals())

    @Rule(AND(UserInput(text=L('hola') | L('buenos días') | L('buenas tardes'))))
    def handle_greeting(self):
        self.declare(BotAction(type='greet'))

    @Rule(AND(UserInput(text=MATCH.text)), salience=-1)
    def handle_specific_questions(self, text):
        specific_responses = self.responses.get("respuestas_especificas", {})
        if text in specific_responses:
            self.declare(BotAction(type='respond_specific', key=text))

    @Rule(salience=-10)
    def handle_unknown_input(self):
        if not self.response_generated:
            self.declare(NeedsLearning())

    @Rule(NeedsLearning())
    def handle_learning_opportunity(self):
        self.declare(BotAction(type='request_teaching'))

    @Rule(ReviewGoals())
    def review_goals(self):
        active_goals = self.brain.goal_manager.list_goals(status='active')
        if active_goals:
            goal = active_goals[0]
            self.declare(BotAction(type='report_goal_status', goal=goal))

    @Rule(BotAction(type='greet'))
    def action_greet(self):
        self.response = [random.choice(self.responses.get("saludos", ["Hola."]))]
        self.response_generated = True

    @Rule(BotAction(type='respond_specific', key=MATCH.key))
    def action_respond_specific(self, key):
        self.response = self.responses["respuestas_especificas"][key]
        self.response_generated = True

    @Rule(BotAction(type='request_teaching'))
    def action_request_teaching(self):
        self.response = ["No estoy seguro de cómo responder a eso. ¿Puedes enseñarme? Para hacerlo, usa el comando !teach."]
        self.response_generated = True

    @Rule(BotAction(type='report_goal_status', goal=MATCH.goal))
    def action_report_goal_status(self, goal):
        self.response = [
            f"[Recordatorio de Meta] Estoy trabajando en: '{goal['name']}'",
            f"Progreso: {goal['progress']:.0f}%"
        ]
        self.response_generated = True

    def get_response(self) -> Optional[List[str]]:
        if self.response_generated:
            return self.response
        return None

    def get_rules(self):
        return self.rules

# --- Fin de la Integración del Motor de Reglas ---




# --- Clase principal del cerebro ---
class Brain:
    def process_message(self, message: str):
        """
        Procesa un mensaje del usuario y devuelve una respuesta.
        """
        # Modo rule_engine (Experta)
        if hasattr(self, 'reasoning_engine') and self.reasoning_engine:
            self.reasoning_engine.reset()
            self.reasoning_engine.declare(UserInput(text=message))
            self.reasoning_engine.run()
            response = self.reasoning_engine.get_response()
            if response:
                return '\n'.join(response)
        # Modo ML
        if self.mode == "ml" and self.model:
            intent = self.model.predict([message])[0]
            return '\n'.join(self.responses.get("respuestas_especificas", {}).get(intent, ["No entiendo."]))
        # Modo rule (básico)
        specific = self.responses.get("respuestas_especificas", {})
        if message.lower() in specific:
            return '\n'.join(specific[message.lower()])
        # Plantilla general
        plantilla = self.responses.get("plantillas_generales", ["No entiendo."])
        return plantilla[0].replace('{input}', message)
    """
    Módulo de cerebro para MEA-Core-IA. Gestiona la selección de respuestas y la integración de memoria, conocimiento y enjambre.
    """
    def __init__(self, settings: Dict[str, Any], responses: Dict[str, Any],
                 memory: Optional[MemoryStore] = None,
                 knowledge_base: Optional[KnowledgeBase] = None,
                 swarm_controller: Optional[SwarmController] = None):
        self.settings = settings
        self.mode = self.settings.get("brain", {}).get("mode", "rule_engine")
        self.responses = responses
        self.model = None
        self.memory = memory or MemoryStore()
        self.knowledge_base = knowledge_base or KnowledgeBase([])
        self.swarm_controller = swarm_controller or SwarmController(node_id="default")
        self.learning_module = ActiveLearningModule()
        self.goal_manager = GoalManager(self.memory)

        # Módulos de consolidación de memoria y motor de reglas dinámicas
        self.memory_consolidator = MemoryConsolidator()
        self.rules_engine = RulesEngine()
    # --- Consolidación de Memoria ---
    def resumir_conversacion(self, texto: str) -> str:
        return self.memory_consolidator.summarize_conversation(texto)

    def extraer_entidades(self, texto: str):
        self.memory_consolidator.extract_entities(texto)
        return self.memory_consolidator.get_entities()

    # --- Motor de Reglas Dinámicas ---
    def aplicar_reglas(self, texto: str) -> str:
        return self.rules_engine.apply(texto)

    def agregar_regla(self, condicion: str, accion: str):
        self.rules_engine.add_rule(condicion, accion)

    def listar_reglas(self):
        return self.rules_engine.list_rules()

        if self.mode == "rule_engine" and EXPERTA_AVAILABLE:
            self.reasoning_engine = ReasoningEngine(self.responses, self)
            print("[Cerebro] Modo 'rule_engine' activado con Experta.")
        else:
            # Fallback a modo 'rule' si experta no está disponible
            self.reasoning_engine = None
            self.mode = "rule"
            if EXPERTA_AVAILABLE:
                print("[Advertencia] Experta no está instalado. Cambiando a modo 'rule'.")
                print("Para usar el modo 'rule_engine', ejecuta: pip install experta")

        if self.mode == "ml" and SKLEARN_AVAILABLE:
            self._train_model()
        elif self.mode == "ml" and not SKLEARN_AVAILABLE:
            print("[Advertencia] scikit-learn no está instalado. Cambiando a modo 'rule'.")
            self.mode = "rule"

    def _train_model(self):
        """Entrena un modelo de clasificación simple con las respuestas específicas."""
        intents = list(self.responses.get("respuestas_especificas", {}).keys())
        if not intents:
            self.mode = "rule"
            return

        X_train, y_train = intents, intents
        self.model = make_pipeline(TfidfVectorizer(), LogisticRegression())
        self.model.fit(X_train, y_train)
        print("[Cerebro] Modelo ML entrenado y listo.")

    def _get_response_from_kb(self, user_input: str) -> Optional[List[str]]:
        """Consulta la base de conocimiento usando BM25F y búsqueda semántica."""
        bm25_results = self.knowledge_base.bm25_search(user_input, top_n=3)
        sem_results = self.knowledge_base.semantic_search(user_input, top_n=2)
        response = []
        if bm25_results:
            response.append("[BM25] Resultados relevantes:")
            response.extend([f"- {r}" for r in bm25_results])
        if sem_results:
            response.append("[Semántica] Resultados similares:")
            response.extend([f"- {r}" for r in sem_results])
        return response if response else None

    def get_response(self, user_input: str, context: Optional[List[str]] = None) -> List[str]:
        """
        Obtiene una respuesta de la fuente más apropiada: Motor de Reglas, KB, ML, o General.
        """
        user_input_lower = user_input.lower()

        # 1. Prioridad: Usar el motor de reglas si está activado
        if self.mode == "rule_engine" and self.reasoning_engine:
            self.reasoning_engine.reset()
            self.reasoning_engine.declare(UserInput(text=user_input_lower))
            self.reasoning_engine.run()
            rule_response = self.reasoning_engine.get_response()
            if rule_response:
                return rule_response

        # 2. Consultar la base de conocimiento (si no es un saludo/despedida)
        common_phrases = list(self.responses.get("saludos", [])) + list(self.responses.get("despedidas", []))
        if user_input_lower not in common_phrases:
            kb_response = self._get_response_from_kb(user_input_lower)
            if kb_response:
                return kb_response

        # 3. Usar el modelo ML si está activado
        if self.mode == "ml" and self.model:
            predicted_intent = self.model.predict([user_input_lower])[0]
            if predicted_intent in self.responses["respuestas_especificas"]:
                return self.responses["respuestas_especificas"][predicted_intent]

        # 4. Usar el modo 'rule' simple o como fallback
        if user_input_lower in self.responses.get("respuestas_especificas", {}):
            return self.responses["respuestas_especificas"][user_input_lower]
        
        # 5. Si no hay respuesta, devolver una plantilla general
        plantilla = random.choice(self.responses.get("plantillas_generales", []))
        return [plantilla.format(input=user_input)]

    def get_greeting(self) -> str:
        return random.choice(self.responses.get("saludos", ["Hola."]))

    def get_farewell(self) -> str:
        return random.choice(self.responses.get("despedidas", ["Adiós."]))