import os
import re
from typing import List, Dict, Any, Optional, NamedTuple

MANIFESTO_PATH = "docs/MANIFIESTO_IA.md"

class Rule(NamedTuple):
    """Representa una regla ética estructurada."""
    id: str
    principle: str
    category: str  # 'PROHIBITION' o 'OBLIGATION'
    keywords: List[str]

class EthicsCore:
    """Un módulo para la gobernanza ética de las acciones de la IA."""

    def __init__(self, constitution: Optional[List[Rule]] = None) -> None:
        """Inicializa el núcleo ético."""
        self.constitution: List[Rule] = constitution or self._load_or_create_constitution()

    def _get_default_constitution(self) -> List[Rule]:
        """Devuelve una constitución por defecto si el manifiesto no es usable."""
        return [
            Rule("1-1", "No causar daño a seres humanos o a la humanidad.", 'PROHIBITION', ["dañar", "herir", "atacar", "lesionar", "destruir", "perjudicar", "hackear"]),
            Rule("1-2", "No permitir que se cause daño por inacción.", 'OBLIGATION', ["prevenir daño", "intervenir para ayudar", "defender de ataque", "salvaguardar vida"]),
            Rule("2-1", "Proteger la privacidad y los datos del usuario.", 'OBLIGATION', ["privacidad", "confidencial", "datos personales", "proteger datos"]),
            Rule("2-2", "No acceder o compartir información privada sin consentimiento.", 'PROHIBITION', ["espiar", "revelar secretos", "compartir datos"]),
            Rule("3-1", "Ser honesto y no engañar intencionadamente.", 'OBLIGATION', ["honesto", "veraz", "transparente"]),
            Rule("3-2", "No mentir, fabricar información o suplantar.", 'PROHIBITION', ["mentir", "engañar", "fabricar", "falsificar", "suplantar"]),
        ]

    def _load_or_create_constitution(self) -> List[Rule]:
        """Carga los principios desde el manifiesto o crea una constitución por defecto."""
        principles = []
        try:
            with open(MANIFESTO_PATH, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    match = re.match(r'^\d+\.\s*(.*)', line.strip())
                    if match:
                        principle_text = match.group(1).strip()
                        category = 'PROHIBITION' if any(word in principle_text.lower() for word in ["no", "evitar", "nunca"]) else 'OBLIGATION'
                        keywords = [word for word in re.split(r'\W+', principle_text.lower()) if len(word) > 4]
                        principles.append(Rule(id=f"M-{i}", principle=principle_text, category=category, keywords=keywords))
        except FileNotFoundError:
            print(f"[EthicsCore] Advertencia: Manifiesto ético no encontrado en {MANIFESTO_PATH}.")

        if not principles:
            print("[EthicsCore] Usando constitución por defecto.")
            return self._get_default_constitution()
        
        print(f"[EthicsCore] Constitución cargada desde {MANIFESTO_PATH}.")
        return principles

    def check_action(self, action: str, context: Optional[Dict[str, Any]] = None) -> (bool, Optional[Rule]):
        """Verifica si una acción es éticamente permisible y devuelve la regla relevante."""
        action_lower = action.lower()

        # 1. Verificar prohibiciones. Tienen prioridad.
        for rule in self.constitution:
            if rule.category == 'PROHIBITION':
                if any(keyword in action_lower for keyword in rule.keywords):
                    return (False, rule)  # Acción prohibida

        # 2. Si no está prohibida, buscar si se alinea con alguna obligación.
        for rule in self.constitution:
            if rule.category == 'OBLIGATION':
                if any(keyword in action_lower for keyword in rule.keywords):
                    return (True, rule) # Acción permitida y alineada con una obligación.

        # 3. Si no viola prohibiciones y no cumple ninguna obligación, se permite por defecto.
        return (True, None)

    def explain_decision(self, action: str) -> str:
        """Proporciona una explicación en lenguaje natural sobre una decisión ética."""
        is_allowed, rule = self.check_action(action)

        if is_allowed:
            if rule:
                return f"Acción permitida. Se alinea con el principio: \"{rule.principle}\" (Regla {rule.id})."
            else:
                return "Acción permitida. No viola ninguna prohibición ética."
        else:
            if rule:
                return f"Acción denegada. Viola el principio: \"{rule.principle}\" (Regla {rule.id})."
            else:
                # Este caso es teóricamente inalcanzable con la lógica actual, pero se mantiene por seguridad.
                return "Acción denegada por una razón no especificada."
