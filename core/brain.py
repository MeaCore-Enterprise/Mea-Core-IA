
import json
import os
import random
from typing import Any, Dict, List, Optional

from core.knowledge import KnowledgeBase

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

class ReasoningEngine(KnowledgeEngine):
    """Motor de razonamiento basado en reglas para MEA-Core."""
    def __init__(self, responses):
        super().__init__()
        self.responses = responses
        self.response_generated = False

    @DefFacts()
    def _initial_facts(self):
        yield Fact(action="greet")

    @Rule(UserInput(text=MATCH.text))
    def handle_input(self, text):
        # Esta regla se activa con cualquier entrada del usuario
        # y puede ser usada para análisis más complejos.
        # Por ahora, simplemente lo registramos.
        print(f"[Motor de Reglas] Hecho recibido: UserInput(text='{text}')")

    @Rule(AND(UserInput(text=L('hola') | L('buenos días') | L('buenas tardes'))))
    def handle_greeting(self):
        self.declare(BotAction(type='greet'))

    @Rule(AND(UserInput(text=MATCH.text), salience= -1))
    def handle_specific_questions(self, text):
        specific_responses = self.responses.get("respuestas_especificas", {})
        if text in specific_responses:
            self.declare(BotAction(type='respond_specific', key=text))

    @Rule(BotAction(type='greet'))
    def action_greet(self):
        self.response = [random.choice(self.responses.get("saludos", ["Hola."]))]
        self.response_generated = True

    @Rule(BotAction(type='respond_specific', key=MATCH.key))
    def action_respond_specific(self, key):
        self.response = self.responses["respuestas_especificas"][key]
        self.response_generated = True

    def get_response(self) -> Optional[List[str]]:
        if self.response_generated:
            return self.response
        return None

# --- Fin de la Integración del Motor de Reglas ---


class Brain:
    """
    Módulo de cerebro para MEA-Core-IA. Gestiona la selección de respuestas.
    """
    def __init__(self, settings: Dict[str, Any], responses: Dict[str, Any]):
        self.settings = settings.get("brain", {})
        self.mode = self.settings.get("mode", "rule_engine") # Cambiado a 'rule_engine' por defecto
        self.responses = responses
        self.model = None
        self.knowledge_base = KnowledgeBase()

        if self.mode == "rule_engine" and EXPERTA_AVAILABLE:
            self.reasoning_engine = ReasoningEngine(self.responses)
            print("[Cerebro] Modo 'rule_engine' activado con Experta.")
        elif self.mode == "rule_engine" and not EXPERTA_AVAILABLE:
            print("[Advertencia] Experta no está instalado. Cambiando a modo 'rule'.")
            print("Para usar el modo 'rule_engine', ejecuta: pip install experta")
            self.mode = "rule"
            self.reasoning_engine = None
        else:
            self.reasoning_engine = None

        if self.mode == "ml" and SKLEARN_AVAILABLE:
            self._train_model()
        elif self.mode == "ml" and not SKLEARN_AVAILABLE:
            print("[Advertencia] scikit-learn no está instalado. Cambiando a modo 'rule'.")
            print("Para usar el modo 'ml', ejecuta: pip install scikit-learn")
            self.mode = "rule"

    def _train_model(self):
        """Entrena un modelo de clasificación simple con las respuestas específicas."""
        intents = list(self.responses.get("respuestas_especificas", {}).keys())
        if not intents:
            print("[Advertencia] No hay 'respuestas_especificas' para entrenar el modelo ML.")
            self.mode = "rule"
            return

        X_train = intents
        y_train = intents
        self.model = make_pipeline(TfidfVectorizer(), LogisticRegression())
        self.model.fit(X_train, y_train)
        print("[Cerebro] Modelo ML entrenado y listo.")

    def _get_response_from_kb(self, user_input: str) -> Optional[List[str]]:
        """Consulta la base de conocimiento usando búsqueda semántica (BM25)."""
        search_threshold = self.settings.get("kb_search_threshold", 0.1)
        
        results = self.knowledge_base.search(user_input, top_n=3)
        
        if results:
            response = ["He encontrado estos principios que podrían ser relevantes:"]
            response.extend([f"- ({r[0]}) {r[2]}" for r in results])
            return response
        return None

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
