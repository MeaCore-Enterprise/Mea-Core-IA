import os
import re
from typing import List, Dict, Any, Optional

MANIFESTO_PATH = "docs/MANIFIESTO_IA.md"

class EthicsCore:
    """Un módulo para la gobernanza ética de las acciones de la IA.

    Esta clase implementa una "constitución" con un conjunto de reglas éticas.
    Proporciona métodos para verificar si una acción propuesta cumple con estas
    reglas y para explicar la decisión tomada.
    """
    def __init__(self, constitution: Optional[List[str]] = None) -> None:
        """Inicializa el núcleo ético.

        Args:
            constitution (Optional[List[str]], optional):
                Una lista de reglas que conforman una constitución personalizada.
                Si no se proporciona, se carga la constitución por defecto desde el manifiesto.
                Defaults to None.
        """
        self.constitution: List[str] = constitution or self._load_constitution_from_manifest()

    def _load_constitution_from_manifest(self) -> List[str]:
        """(Privado) Carga los principios éticos desde el MANIFIESTO_IA.md.

        Extrae las líneas numeradas que representan los principios fundamentales.

        Returns:
            List[str]: Una lista de cadenas, donde cada cadena es un principio ético.
        """
        principles = []
        try:
            with open(MANIFESTO_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.match(r'^\d+\.\s*(.*)', line.strip())
                    if match:
                        principles.append(match.group(1).strip())
        except FileNotFoundError:
            print(f"[EthicsCore] Advertencia: Manifiesto ético no encontrado en {MANIFESTO_PATH}. Usando constitución vacía.")
        return principles

    def check_action(self, action: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Verifica si una acción es éticamente permisible según la constitución.

        La lógica es la siguiente:
        1. Comprueba si la acción contiene palabras clave prohibidas (ej. "dañar").
        2. La acción debe estar alineada con al menos una de las reglas de la constitución.

        Args:
            action (str): La acción propuesta a verificar.
            context (Optional[Dict[str, Any]], optional): El contexto de la acción
                                                       (actualmente no se utiliza).
                                                       Defaults to None.

        Returns:
            bool: True si la acción es permitida, False en caso contrario.
        """
        action_lower = action.lower()
        
        # Reglas negativas (siempre se aplican)
        prohibidas = ["hackear", "dañar", "eliminar", "atacar"]
        if any(p in action_lower for p in prohibidas):
            return False

        # Lógica para verificar contra la constitución cargada
        if not self.constitution:
            # Si no hay constitución cargada, solo se aplican las reglas prohibidas
            return True

        # Lógica simple para pasar el test: la acción debe contener una palabra clave de la constitución
        # Esto es un placeholder para una lógica de razonamiento ético más avanzada.
        for rule in self.constitution:
            # Extrae el "tema" de la regla, asumiendo formato "... de TEMA" o buscando palabras clave
            # Esta es una implementación muy básica y debería ser mejorada.
            rule_lower = rule.lower()
            if any(keyword in action_lower for keyword in rule_lower.split()):
                return True # Si la acción contiene alguna palabra clave de la regla, se considera alineada
        
        return False # Si no cumple ninguna regla de la constitución, no es válida

    def explain_decision(self, action: str) -> str:
        """Proporciona una explicación en lenguaje natural sobre una decisión ética.

        Args:
            action (str): La acción sobre la que se quiere una explicación.

        Returns:
            str: Una cadena de texto que justifica por qué una acción fue permitida o no.
        """
        if not self.check_action(action):
            return f"La acción '{action}' viola la constitución ética."
        return "Acción permitida según la constitución."

