import unittest
import os
import sys
from unittest.mock import MagicMock

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memoria import MemoryStore
from core.gestor_configuracion import SettingsManager

class TestMemoryExtensions(unittest.TestCase):

    def setUp(self):
        """Usa una base de datos en memoria para cada prueba."""
        mock_settings_manager = MagicMock(spec=SettingsManager)
        mock_settings_manager.get_setting.return_value = ":memory:"
        self.memory = MemoryStore(settings_manager=mock_settings_manager)
        self.memory.clear_all_memory_for_testing()

    def tearDown(self):
        self.memory.close_db()

    def test_get_instance_id_creation_and_retrieval(self):
        """Prueba que se crea un ID de instancia y se recupera el mismo."""
        instance_id = self.memory.get_instance_id()
        self.assertIsInstance(instance_id, str)
        self.assertEqual(len(instance_id), 36) # UUID4 length

        retrieved_id = self.memory.get_instance_id()
        self.assertEqual(instance_id, retrieved_id)