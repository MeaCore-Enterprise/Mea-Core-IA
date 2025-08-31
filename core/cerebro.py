import json
import os
import random
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

# --- Importaciones de Módulos del Núcleo ---
from .memoria import MemoryStore
from .conocimiento import KnowledgeManager
from .etica import EthicsCore
from .motor_reglas import RulesEngine
from engine import MeaEngine

# --- Dependencias Opcionales ---
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from experta import KnowledgeEngine, Fact, Rule, MATCH, NOT, W
    EXPERTA_AVAILABLE = True
except ImportError:
    EXPERTA_AVAILABLE = False

# --- Clase Principal del Cerebro (Refactorizada para Inyección de Dependencias) ---

class Brain:
    """
    Módulo de cerebro para MEA-Core-IA. Orquesta la lógica de respuesta
    utilizando los módulos de memoria, conocimiento y ética.
    """
    def __init__(self, settings: Dict[str, Any], responses: Dict[str, Any],
                 memory: MemoryStore, knowledge: KnowledgeManager, ethics: EthicsCore):
        """
        Inicializa el cerebro con sus dependencias ya instanciadas.
        """
        self.settings = settings
        self.mode = self.settings.get("brain", {}).get("mode", "rule_engine")
        self.responses = responses
        self.memory = memory
        self.knowledge = knowledge
        self.ethics = ethics
        self.model = None
        self.engine = None

        # Cargar motor de embeddings si existe
        try:
            self.engine = MeaEngine.load_model("mea_engine.pth")
        except FileNotFoundError:
            print("[Cerebro] Modelo de motor de embeddings (mea_engine.pth) no encontrado.")
        except Exception as e:
            print(f"[ERROR] No se pudo cargar MeaEngine: {e}")

        # Inicializar modos de operación
        if self.mode == "ml" and SKLEARN_AVAILABLE:
            self._train_model()
        elif self.mode == "ml":
            print("[Advertencia] scikit-learn no disponible. Cambiando a modo 'rule'.")
            self.mode = "rule"

    def _train_model(self):
        """Entrena un modelo de clasificación simple."""
        intents = list(self.responses.get("respuestas_especificas", {}).keys())
        if not intents:
            self.mode = "rule"
            return
        self.model = make_pipeline(TfidfVectorizer(), LogisticRegression())
        self.model.fit(intents, intents)
        print("[Cerebro] Modelo ML entrenado.")

    def learn_fact(self, db: Session, fact_text: str):
        """Aprende un nuevo hecho y lo añade a la base de conocimiento."""
        self.knowledge.add_fact(db, fact_text)
        print(f"[Cerebro] Hecho aprendido: {fact_text}")

    def get_response(self, db: Session, user_input: str, context: Optional[List[str]] = None) -> List[str]:
        """
        Obtiene una respuesta coordinando los diferentes modos y módulos.
        Ahora requiere una sesión de DB para operar.
        """
        if not self.ethics.check_action(user_input):
            return [self.ethics.explain_decision(user_input)]

        user_input_lower = user_input.lower()
        response: Optional[List[str]] = None

        # La lógica de fallback permanece, pero ahora pasa la sesión de DB
        # 1. Memoria
        try:
            memory_results = self.memory.get_memory(db, query=user_input_lower, context=context, top_n=1)
            if memory_results:
                response = ["[Recuerdo Relevante]"] + [res['data'] for res in memory_results]
        except Exception as e:
            print(f"[Advertencia] Fallo en la consulta a memoria: {e}")

        # 2. Base de Conocimiento
        if response is None:
            try:
                kb_response = self.knowledge.query(db, user_input_lower)
                if kb_response.get('ranked_facts'):
                    response = ["[Hechos Relevantes]"] + [f"{fact} (Confianza: {conf:.2f})" for fact, conf in kb_response['ranked_facts']]
            except Exception as e:
                print(f"[Advertencia] Fallo en la consulta a conocimiento: {e}")

        # 3. Modo ML
        if response is None and self.mode == "ml" and self.model:
            try:
                predicted_intent = self.model.predict([user_input_lower])[0]
                if predicted_intent in self.responses.get("respuestas_especificas", {}):
                    response = self.responses["respuestas_especificas"][predicted_intent]
            except Exception as e:
                print(f"[Advertencia] Fallo en modo ML: {e}")

        # 4. Modo Regla Simple
        if response is None:
            if user_input_lower in self.responses.get("respuestas_especificas", {}):
                response = self.responses["respuestas_especificas"][user_input_lower]
        
        # 5. Fallback General
        if response is None:
            plantilla = random.choice(self.responses.get("plantillas_generales", []))
            response = [plantilla.format(input=user_input)]

        # Log del episodio conversacional
        self.memory.log_episode(db, type="conversation", source="brain", data={
            "user_input": user_input,
            "bot_output": response
        })

        return response if isinstance(response, list) else [response]