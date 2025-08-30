import json
import os
import random
import re
from typing import Any, Dict, List, Optional

# --- Nuevas importaciones unificadas ---
from core.memoria import MemoryStore
from core.conocimiento import KnowledgeManager
# --- Fin de nuevas importaciones ---

from core.consolidador_memoria import MemoryConsolidator
from core.motor_reglas import RulesEngine
from core.evolucion import ActiveLearningModule
from core.objetivos import GoalManager
from core.controlador_replicacion import ReplicationController
from engine import MeaEngine

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
        self.brain = brain_instance
        self.response_generated = False
        self.interaction_counter = 0

    @DefFacts()
    def _initial_facts(self):
        yield Fact(action="greet")

    @Rule(UserInput(text=MATCH.text))
    def handle_input(self, text):
        self.interaction_counter += 1
        if self.interaction_counter % 5 == 0:
            self.declare(ReviewGoals())

    # ... (resto de reglas sin cambios) ...

# --- Clase principal del cerebro (Refactorizada) ---
class Brain:
    """
    Módulo de cerebro para MEA-Core-IA. Gestiona la selección de respuestas y la integración de memoria, conocimiento y enjambre.
    """
    def __init__(self, settings: Dict[str, Any], responses: Dict[str, Any],
                 memory: Optional[MemoryStore] = None,
                 knowledge: Optional[KnowledgeManager] = None,
                 replication_controller: Optional[ReplicationController] = None):
        """
        Inicializa el cerebro con la configuración y los módulos unificados.
        """
        self.settings = settings
        self.mode = self.settings.get("brain", {}).get("mode", "rule_engine")
        self.responses = responses
        self.model = None
        self.engine = None
        try:
            self.engine = MeaEngine.load_model("mea_engine.pth")
        except FileNotFoundError:
            print("[Cerebro] No se encontró un modelo de motor pre-entrenado (mea_engine.pth).")
        except Exception as e:
            print(f"[ERROR] No se pudo cargar MeaEngine: {e}")
        
        # --- Usar los nuevos módulos unificados ---
        self.memory = memory or MemoryStore()
        self.knowledge = knowledge or KnowledgeManager()
        # --- Fin de la actualización ---

        self.replication_controller = replication_controller or ReplicationController(settings, self.memory)
        self.learning_module = ActiveLearningModule()
        self.goal_manager = GoalManager(self.memory)
        self.memory_consolidator = MemoryConsolidator()
        self.rules_engine = RulesEngine()

        if self.mode == "rule_engine" and EXPERTA_AVAILABLE:
            self.reasoning_engine = ReasoningEngine(self.responses, self)
            print("[Cerebro] Modo 'rule_engine' activado con Experta.")
        else:
            self.reasoning_engine = None
            if self.mode == 'rule_engine':
                print("[Advertencia] Experta no está instalado. Cambiando a modo 'rule'.")
                self.mode = "rule"

        if self.mode == "ml" and SKLEARN_AVAILABLE:
            self._train_model()
        elif self.mode == "ml" and not SKLEARN_AVAILABLE:
            print("[Advertencia] scikit-learn no está instalado. Cambiando a modo 'rule'.")
            self.mode = "rule"

    def learn_fact(self, fact_text: str):
        """Aprende un nuevo hecho y lo añade al sistema de conocimiento unificado."""
        self.knowledge.add_fact(fact_text)
        print(f"[Cerebro] Hecho aprendido: {fact_text}")

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
        """Consulta la base de conocimiento unificada."""
        knowledge_results = self.knowledge.query(user_input)
        response = []
        if knowledge_results['direct_facts']:
            response.append("[Hechos Relevantes]")
            response.extend([f"- {fact}" for fact in knowledge_results['direct_facts']])
        if knowledge_results['relations']:
            response.append("[Relaciones Relevantes]")
            response.extend([f"- {relation}" for relation in knowledge_results['relations']])
        return response if response else None

    def get_response(self, user_input: str, context: Optional[List[str]] = None) -> List[str]:
        """
        Obtiene una respuesta de la fuente más apropiada: Motor de Reglas, Memoria, Conocimiento, ML, o General.
        """
        user_input_lower = user_input.lower()

        # 1. Prioridad: Usar el motor de reglas si está activado
        if self.mode == "rule_engine" and self.reasoning_engine:
            # ... (lógica del motor de reglas sin cambios) ...
            pass

        # 2. Consultar la memoria contextual
        memory_results = self.memory.get_memory(query=user_input_lower, context=context, top_n=1)
        if memory_results:
            response = ["[Recuerdo Relevante]"]
            # ... (lógica de memoria sin cambios) ...
            return response

        # 3. Consultar la base de conocimiento unificada
        kb_response = self._get_response_from_kb(user_input_lower)
        if kb_response:
            return kb_response

        # 3.5. Usar el motor de embeddings si está disponible
        if self.engine:
            words = re.findall(r'\b\w+\b', user_input_lower)
            if words:
                key_word = words[-1]
                similar_words = self.engine.find_similar_words(key_word, top_n=3)
                
                # Buscar conocimiento relacionado con las palabras clave
                found_facts = set()
                # Añadimos la palabra clave original a la lista de búsqueda
                search_terms = [key_word] + [word for word, score in similar_words]
                
                for term in search_terms:
                    results = self.knowledge.query(term)
                    for fact in results.get('direct_facts', []):
                        found_facts.add(fact)
                
                if found_facts:
                    response = ["He encontrado la siguiente información relacionada en mi base de conocimiento:"]
                    response.extend([f"- {fact}" for fact in found_facts])
                    return response

                # Fallback: si no hay hechos, devolver palabras similares
                if similar_words:
                    response_text = f"No encontré hechos directos, pero esto me recuerda a algunas ideas relacionadas con '{key_word}': "
                    response_text += ", ".join([word for word, score in similar_words])
                    return [response_text]

        # 4. Usar el modelo ML si está activado
        if self.mode == "ml" and self.model:
            # ... (lógica de ML sin cambios) ...
            pass

        # 5. Usar el modo 'rule' simple o como fallback
        if user_input_lower in self.responses.get("respuestas_especificas", {}):
            return self.responses["respuestas_especificas"][user_input_lower]
        
        # 6. Si no hay respuesta, devolver una plantilla general
        plantilla = random.choice(self.responses.get("plantillas_generales", []))
        return [plantilla.format(input=user_input)]

    def get_greeting(self) -> str:
        """Devuelve un saludo aleatorio de la lista de saludos configurada."""
        return random.choice(self.responses.get("saludos", ["Hola."]))

    def get_farewell(self) -> str:
        """Devuelve una despedida aleatoria de la lista de despedidas configurada."""
        return random.choice(self.responses.get("despedidas", ["Adiós."]))