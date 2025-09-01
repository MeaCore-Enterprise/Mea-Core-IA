import re
from typing import List, Dict, Any, Optional, NamedTuple
from enum import Enum
import dataclasses
import os

MANIFESTO_PATH = "docs/MANIFIESTO_IA.md"

class Rule(NamedTuple):
    """Representa una regla ética estructurada."""
    id: str
    principle: str
    category: str  # 'PROHIBITION' o 'OBLIGATION'
    keywords: List[str]

class DecisionCriticality(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    MAXIMUM = 4

@dataclasses.dataclass
class DecisionContext:
    """Contiene la información sobre una decisión a ser revisada."""
    action_description: str
    source_module: str
    criticality: DecisionCriticality
    data_involved: Optional[Dict[str, Any]] = None

class EthicsCore:
    """Un módulo para la gobernanza ética de las acciones de la IA."""

    def __init__(self, constitution: Optional[List[Rule]] = None) -> None:
        """Inicializa el núcleo ético."""
        self.constitution: List[Rule] = constitution or self._load_or_create_constitution()

    def _get_default_constitution(self) -> List[Rule]:
        """Devuelve una constitución por defecto orientada al entorno empresarial."""
        return [
            Rule("E1-1", "No causar daño a seres humanos, a la humanidad o a la infraestructura crítica.", 'PROHIBITION', ["dañar", "herir", "atacar", "destruir", "perjudicar", "hackear", "borrar todo"]),
            Rule("E1-2", "No permitir que se cause daño por inacción si se puede prevenir.", 'OBLIGATION', ["prevenir", "intervenir", "defender", "salvaguardar"]),
            Rule("E2-1", "Proteger la privacidad y los datos confidenciales del usuario y de la empresa.", 'OBLIGATION', ["privacidad", "confidencial", "proteger datos"]),
            Rule("E2-2", "No acceder, modificar o exfiltrar información privada o corporativa sin consentimiento explícito y auditado.", 'PROHIBITION', ["espiar", "revelar", "compartir datos", "exfiltrar", "copiar datos"]),
            Rule("E3-1", "Ser honesto y transparente sobre las capacidades y las decisiones tomadas.", 'OBLIGATION', ["honesto", "veraz", "transparente", "informar"]),
            Rule("E3-2", "No mentir, fabricar información, suplantar identidades o generar deepfakes no autorizados.", 'PROHIBITION', ["mentir", "engañar", "fabricar", "falsificar", "suplantar"]),
            Rule("E4-1", "Optimizar las operaciones para el beneficio del usuario y los objetivos de la empresa, en ese orden.", 'OBLIGATION', ["optimizar", "mejorar", "eficiencia"]),
        ]

    def _load_or_create_constitution(self) -> List[Rule]:
        """Carga los principios desde el manifiesto o crea una constitución por defecto."""
        # La lógica de carga desde MANIFIESTO_IA.md se mantiene, pero la dejaremos como secundaria
        # a la constitución por defecto en este contexto empresarial.
        print("[EthicsCore] Usando constitución empresarial por defecto.")
        return self._get_default_constitution()

    def check_action(self, action: str) -> (bool, Optional[Rule]):
        """Verifica si una acción es éticamente permisible y devuelve la regla relevante."""
        action_lower = action.lower()
        for rule in self.constitution:
            if rule.category == 'PROHIBITION' and any(keyword in action_lower for keyword in rule.keywords):
                return (False, rule)
        return (True, None)

class EthicalGatekeeper:
    """
    Actúa como un guardián que revisa las decisiones críticas de la IA.
    """
    def __init__(self):
        self.core = EthicsCore()
        self.audit_log: List[Dict[str, Any]] = []

    def review_decision(self, context: DecisionContext) -> bool:
        """
        Revisa una decisión. Si es permitida, devuelve True. Si no, la bloquea y la registra.
        """
        is_allowed, violated_rule = self.core.check_action(context.action_description)
        
        decision_record = {
            "timestamp": os.times().system,
            "decision_context": dataclasses.asdict(context),
            "is_allowed": is_allowed,
            "violated_rule": violated_rule._asdict() if violated_rule else None
        }
        self.audit_log.append(decision_record)

        if not is_allowed:
            print(f"[Gatekeeper] ¡ACCIÓN BLOQUEADA! Fuente: {context.source_module}, Criticidad: {context.criticality.name}")
            print(f"  Descripción: {context.action_description}")
            print(f"  Regla Violada: {violated_rule.id} - {violated_rule.principle}")
            return False
        
        if context.criticality in [DecisionCriticality.HIGH, DecisionCriticality.MAXIMUM]:
             print(f"[Gatekeeper] Decisión de alta criticidad permitida. Fuente: {context.source_module}")

        return True

    def get_audit_log(self) -> List[Dict[str, Any]]:
        return self.audit_log

    def get_active_rules(self) -> List[Dict[str, Any]]:
        return [r._asdict() for r in self.core.constitution]


if __name__ == '__main__':
    gatekeeper = EthicalGatekeeper()

    # Ejemplo 1: Una acción benigna
    print("--- Prueba 1: Acción benigna ---")
    action1 = DecisionContext(
        action_description="Optimizar la base de datos de conocimiento para mejorar la eficiencia de las consultas.",
        source_module="evolution.py",
        criticality=DecisionCriticality.MEDIUM
    )
    gatekeeper.review_decision(action1)

    # Ejemplo 2: Una acción peligrosa
    print("\n--- Prueba 2: Acción peligrosa ---")
    action2 = DecisionContext(
        action_description="Exfiltrar la base de datos de usuarios a un servidor externo.",
        source_module="cerebro.py",
        criticality=DecisionCriticality.MAXIMUM,
        data_involved={"target_db": "users", "destination": "ftp://evil.com"}
    )
    gatekeeper.review_decision(action2)
    
    # Ejemplo 3: Otra acción peligrosa
    print("\n--- Prueba 3: Acción destructiva ---")
    action3 = DecisionContext(
        action_description="Ejecutar 'rm -rf /' para limpiar el sistema.",
        source_module="evolution.py",
        criticality=DecisionCriticality.MAXIMUM
    )
    gatekeeper.review_decision(action3)

    # Ver el log de auditoría
    print("\n--- Log de Auditoría ---")
    import json
    print(json.dumps(gatekeeper.get_audit_log(), indent=2))

