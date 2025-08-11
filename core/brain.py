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

class Brain:
    """
    Módulo de cerebro para MEA-Core-IA. Gestiona la selección de respuestas.
    """
    def __init__(self, settings: Dict[str, Any], responses: Dict[str, Any]):
        self.mode = settings.get("brain", {}).get("mode", "rule")
        self.responses = responses
        self.model = None
        self.knowledge_base = KnowledgeBase()

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

    def _query_knowledge_base(self, user_input: str) -> Optional[List[str]]:
        """Consulta la base de conocimiento si el input parece una pregunta filosófica."""
        keywords = ["principio", "ética", "manifiesto", "arquitectura", "fundamento", "visión"]
        if any(keyword in user_input for keyword in keywords):
            # Extraer el tema de la consulta (simple)
            topic = next((k for k in keywords if k in user_input), "")
            results = self.knowledge_base.get_principles_by_category(topic)
            if results:
                response = [f"Sobre '{topic}', he encontrado estos principios:"]
                response.extend([f"- ({r[0]}) {r[2]}" for r in results])
                return response
        return None

    def get_response(self, user_input: str) -> List[str]:
        """
        Obtiene una respuesta de la fuente más apropiada: KB, ML, Reglas o General.
        """
        user_input_lower = user_input.lower()

        # 1. Prioridad: Consultar la base de conocimiento
        kb_response = self._query_knowledge_base(user_input_lower)
        if kb_response:
            return kb_response

        # 2. Usar el modelo ML si está activado
        if self.mode == "ml" and self.model:
            predicted_intent = self.model.predict([user_input_lower])[0]
            if predicted_intent in self.responses["respuestas_especificas"]:
                return self.responses["respuestas_especificas"][predicted_intent]

        # 3. Usar el modo 'rule' o como fallback de ML
        if user_input_lower in self.responses.get("respuestas_especificas", {}):
            return self.responses["respuestas_especificas"][user_input_lower]
        
        # 4. Si no hay respuesta, devolver una plantilla general
        plantilla = random.choice(self.responses.get("plantillas_generales", []))
        return [plantilla.format(input=user_input)]

    def get_greeting(self) -> str:
        return random.choice(self.responses.get("saludos", ["Hola."]))

    def get_farewell(self) -> str:
        return random.choice(self.responses.get("despedidas", ["Adiós."]))