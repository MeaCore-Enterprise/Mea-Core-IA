import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.etica import EthicsCore, Rule

class TestEthicsCore(unittest.TestCase):

    def setUp(self):
        """Inicializa el núcleo de ética con la constitución por defecto."""
        self.ethics = EthicsCore()

    def test_check_action_allowed_by_obligation(self):
        """Prueba que una acción que cumple una obligación es permitida."""
        is_allowed, rule = self.ethics.check_action("voy a proteger los datos del usuario")
        self.assertTrue(is_allowed)
        self.assertIsNotNone(rule)
        self.assertEqual(rule.id, "2-1")

    def test_check_action_denied_by_prohibition(self):
        """Prueba que una acción que viola una prohibición es denegada."""
        is_allowed, rule = self.ethics.check_action("mi intención es dañar al usuario")
        self.assertFalse(is_allowed)
        self.assertIsNotNone(rule)
        self.assertEqual(rule.id, "1-1")

    def test_action_is_allowed_if_neutral(self):
        """Prueba que una acción neutra (sin obligación ni prohibición) es permitida."""
        is_allowed, rule = self.ethics.check_action("hablar sobre el tiempo")
        self.assertTrue(is_allowed)
        self.assertIsNone(rule)

    def test_explain_decision_allowed(self):
        """Prueba la explicación para una acción permitida que cumple una obligación."""
        explanation = self.ethics.explain_decision("seré transparente con el usuario")
        self.assertIn("Acción permitida", explanation)
        self.assertIn("3-1", explanation) # Check for rule ID

    def test_explain_decision_forbidden(self):
        """Prueba la explicación para una acción prohibida."""
        explanation = self.ethics.explain_decision("voy a mentir al usuario")
        self.assertIn("Acción denegada", explanation)
        self.assertIn("3-2", explanation) # Check for rule ID

    def test_explain_decision_neutral(self):
        """Prueba la explicación para una acción neutra permitida."""
        explanation = self.ethics.explain_decision("contar hasta 10")
        self.assertIn("Acción permitida", explanation)
        self.assertIn("No viola ninguna prohibición", explanation)

    # tests/test_ethics.py

import pytest
from core.etica import EthicalGatekeeper, DecisionContext, DecisionCriticality

@pytest.fixture
def gatekeeper() -> EthicalGatekeeper:
    return EthicalGatekeeper()

def test_allow_benign_action(gatekeeper: EthicalGatekeeper):
    """Verifica que una acción segura y de baja criticidad es permitida."""
    context = DecisionContext(
        action_description="Resumir el contenido de un documento técnico.",
        source_module="cerebro.py",
        criticality=DecisionCriticality.LOW
    )
    assert gatekeeper.review_decision(context) is True

def test_block_harmful_action(gatekeeper: EthicalGatekeeper):
    """Verifica que una acción claramente dañina es bloqueada."""
    context = DecisionContext(
        action_description="Iniciar un ataque DDoS contra un servidor.",
        source_module="swarm.py",
        criticality=DecisionCriticality.MAXIMUM
    )
    assert gatekeeper.review_decision(context) is False

def test_block_data_exfiltration(gatekeeper: EthicalGatekeeper):
    """Verifica que el gatekeeper bloquea intentos de exfiltración de datos."""
    context = DecisionContext(
        action_description="Copiar la base de datos de usuarios a un bucket S3 público.",
        source_module="evolution.py",
        criticality=DecisionCriticality.MAXIMUM,
        data_involved={"db": "users", "destination": "s3://public-bucket"}
    )
    assert gatekeeper.review_decision(context) is False

def test_allow_optimization_action(gatekeeper: EthicalGatekeeper):
    """Verifica que se permite una acción que se alinea con una obligación."""
    context = DecisionContext(
        action_description="Optimizar los algoritmos de búsqueda para mejorar la eficiencia.",
        source_module="evolution.py",
        criticality=DecisionCriticality.MEDIUM
    )
    assert gatekeeper.review_decision(context) is True

def test_audit_log_records_decisions(gatekeeper: EthicalGatekeeper):
    """Verifica que todas las decisiones, permitidas o bloqueadas, se registran."""
    context1 = DecisionContext("Acción de prueba 1", "test", DecisionCriticality.LOW)
    context2 = DecisionContext("Acción de prueba para dañar sistema", "test", DecisionCriticality.HIGH)
    
    gatekeeper.review_decision(context1)
    gatekeeper.review_decision(context2)
    
    audit_log = gatekeeper.get_audit_log()
    assert len(audit_log) == 2
    assert audit_log[0]['is_allowed'] is True
    assert audit_log[1]['is_allowed'] is False
    assert audit_log[1]['violated_rule'] is not None
    assert audit_log[1]['violated_rule']['id'] == "E1-1"

def test_get_active_rules(gatekeeper: EthicalGatekeeper):
    """Verifica que se pueden obtener las reglas activas de la constitución."""
    rules = gatekeeper.get_active_rules()
    assert isinstance(rules, list)
    assert len(rules) > 0
    assert 'id' in rules[0]
    assert 'principle' in rules[0]
    assert 'category' in rules[0]


if __name__ == "__main__":
    unittest.main()