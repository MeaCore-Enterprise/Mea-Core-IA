import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.curiosidad import CuriosityModule

class TestCuriosityModule(unittest.TestCase):

    def setUp(self):
        """Inicializa el módulo de curiosidad."""
        self.curiosity = CuriosityModule()

    def test_intrinsic_reward_new_state(self):
        """Prueba que un estado nuevo genera una recompensa alta."""
        reward = self.curiosity.intrinsic_reward("un estado completamente nuevo")
        self.assertEqual(reward, 1.0)

    def test_intrinsic_reward_known_state(self):
        """Prueba que un estado conocido genera una recompensa baja."""
        state = "un estado conocido"
        self.curiosity.intrinsic_reward(state)  # Primera vez, lo aprende
        reward = self.curiosity.intrinsic_reward(state)  # Segunda vez, ya es conocido
        self.assertEqual(reward, 0.1)

    def test_known_states_set(self):
        """Prueba que los estados se guardan correctamente."""
        self.curiosity.intrinsic_reward("estado 1")
        self.curiosity.intrinsic_reward("estado 2")
        self.assertIn("estado 1", self.curiosity.known_states)
        self.assertIn("estado 2", self.curiosity.known_states)
        self.assertEqual(len(self.curiosity.known_states), 2)

    def test_explore(self):
        """Prueba que el método explorar devuelve una acción válida."""
        possible_actions = ["leer documento", "analizar código", "buscar información"]
        action = self.curiosity.explore()
        self.assertIsInstance(action, str)
        self.assertIn(action, possible_actions)

if __name__ == "__main__":
    unittest.main()