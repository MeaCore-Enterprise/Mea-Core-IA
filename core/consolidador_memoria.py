# memory_consolidator.py
"""
Módulo para consolidación de memoria inteligente en MEA-Core-IA.
Incluye resumen automático de conversaciones y almacenamiento de entidades clave.
"""
import re
from collections import defaultdict

class MemoryConsolidator:
    def __init__(self):
        self.summaries = []  # Lista de resúmenes de conversaciones
        self.entities = defaultdict(set)  # Entidades clave: personas, temas, acciones

    def summarize_conversation(self, conversation: str) -> str:
        """
        Genera un resumen simple de la conversación extrayendo frases clave.
        """
        # Extrae frases largas y elimina repeticiones
        sentences = re.split(r'[.!?]', conversation)
        key_sentences = [s.strip() for s in sentences if len(s.split()) > 6]
        summary = ' '.join(key_sentences[:3])  # Toma hasta 3 frases clave
        self.summaries.append(summary)
        return summary

    def extract_entities(self, conversation: str):
        """
        Extrae entidades clave (personas, temas, acciones) de la conversación.
        """
        # Personas (palabras que empiezan en mayúscula y no al inicio de frase)
        people = re.findall(r'(?<![.!?]\s)([A-Z][a-z]+)', conversation)
        # Temas (palabras clave frecuentes)
        topics = re.findall(r'\b(IA|memoria|reglas|conocimiento|usuario|sistema|API|entidad|acción)\b', conversation, re.IGNORECASE)
        # Acciones (verbos en infinitivo)
        actions = re.findall(r'\b(analizar|aprender|resumir|guardar|buscar|responder|modificar|priorizar)\b', conversation, re.IGNORECASE)
        self.entities['personas'].update(people)
        self.entities['temas'].update([t.lower() for t in topics])
        self.entities['acciones'].update([a.lower() for a in actions])

    def get_summaries(self):
        return self.summaries

    def get_entities(self):
        return {k: list(v) for k, v in self.entities.items()}
