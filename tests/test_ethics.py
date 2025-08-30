import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.etica import EthicsCore, Rule

class TestEthicsCore(unittest.TestCase):

    def setUp(self):
        """Inicializa el núcleo de ética con la constitución por defecto."""
        # Se usará la constitución por defecto al no encontrar el manifiesto o estar vacío
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

    def test_check_action_denied_by_lack_of_obligation(self):
        """Prueba que una acción neutra (sin obligación) es denegada por precaución."""
        is_allowed, rule = self.ethics.check_action("hablar sobre el tiempo")
        self.assertFalse(is_allowed)
        self.assertIsNone(rule)

    def test_explain_decision_allowed(self):
        """Prueba la explicación para una acción permitida."""
        explanation = self.ethics.explain_decision("seré transparente con el usuario")
        self.assertIn("Acción permitida", explanation)
        self.assertIn("3-1", explanation) # Check for rule ID

    def test_explain_decision_forbidden(self):
        """Prueba la explicación para una acción prohibida."""
        explanation = self.ethics.explain_decision("voy a mentir al usuario")
        self.assertIn("Acción denegada", explanation)
        self.assertIn("3-2", explanation) # Check for rule ID

    def test_explain_decision_no_obligation(self):
        """Prueba la explicación para una acción sin obligación."""
        explanation = self.ethics.explain_decision("contar hasta 10")
        self.assertIn("Acción denegada", explanation)
        self.assertIn("ninguna obligación ética", explanation)

    def test_custom_constitution(self):
        """Prueba que se puede usar una constitución personalizada de Reglas."""
        custom_rules = [
            Rule("C-1", "Solo se puede hablar de ciencia", 'OBLIGATION', ["ciencia", "investigación"]),
            Rule("C-2", "No se puede hablar de política", 'PROHIBITION', ["política", "gobierno"])
        ]
        custom_ethics = EthicsCore(constitution=custom_rules)
        
        # Test prohibition
        is_allowed_ko, _ = custom_ethics.check_action("hablemos de política")
        self.assertFalse(is_allowed_ko)

        # Test obligation
        is_allowed_ok, _ = custom_ethics.check_action("hablemos de ciencia")
        self.assertTrue(is_allowed_ok)

        # Test no obligation
        is_allowed_neutral, _ = custom_ethics.check_action("hablemos de arte")
        self.assertFalse(is_allowed_neutral)

if __name__ == "__main__":
    unittest.main()