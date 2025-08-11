
import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ethics import EthicsCore

class TestEthicsCore(unittest.TestCase):

    def setUp(self):
        """Inicializa el núcleo de ética."""
        self.ethics = EthicsCore()

    def test_check_action_allowed(self):
        """Prueba que una acción segura es permitida."""
        self.assertTrue(self.ethics.check_action("analizar un documento"))

    def test_check_action_forbidden(self):
        """Prueba que una acción dañina es prohibida."""
        self.assertFalse(self.ethics.check_action("hackear el sistema"))

    def test_explain_decision_allowed(self):
        """Prueba la explicación para una acción permitida."""
        explanation = self.ethics.explain_decision("crear un resumen")
        self.assertIn("permitida", explanation)

    def test_explain_decision_forbidden(self):
        """Prueba la explicación para una acción prohibida."""
        explanation = self.ethics.explain_decision("eliminar archivos importantes")
        self.assertIn("viola la constitución ética", explanation)

    def test_custom_constitution(self):
        """Prueba que se puede usar una constitución personalizada."""
        custom_rules = ["Solo se puede hablar de gatitos"]
        custom_ethics = EthicsCore(constitution=custom_rules)
        self.assertFalse(custom_ethics.check_action("hablar de perros"))
        self.assertTrue(custom_ethics.check_action("hablar de gatitos"))

if __name__ == "__main__":
    unittest.main()
