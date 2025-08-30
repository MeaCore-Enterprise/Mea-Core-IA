
import unittest
from unittest.mock import MagicMock
import os
import time

# Añadir el directorio raíz al path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memoria import MemoryStore
from core.gestor_configuracion import SettingsManager

class TestMemoryStore(unittest.TestCase):

    def setUp(self):
        """Configura una base de datos en memoria para cada prueba."""
        mock_settings_manager = MagicMock(spec=SettingsManager)
        mock_settings_manager.get_setting.return_value = ":memory:"
        self.mem = MemoryStore(settings_manager=mock_settings_manager)
        self.mem.clear_all_memory_for_testing()

    def tearDown(self):
        """Cierra la conexión a la DB después de cada prueba."""
        self.mem.close_db()

    def test_log_and_get_episode(self):
        """Prueba que se puede registrar y recuperar un episodio."""
        test_data = {"info": "test_value"}
        self.mem.log_episode(type="test_event", source="test_suite", data=test_data)
        
        retrieved_memories = self.mem.get_memory(query="test_value")
        self.assertEqual(len(retrieved_memories), 1)
        self.assertEqual(retrieved_memories[0]['data'], test_data)

    def test_short_term_memory_limit(self):
        """Prueba que la memoria a corto plazo respeta su límite."""
        for i in range(150): # El límite por defecto es 100
            self.mem.log_episode(type="short_term_test", source="test", data={"i": i}, long_term=False)
        
        self.assertEqual(len(self.mem.short_term), 100)
        self.assertEqual(self.mem.short_term[0]['data']['i'], 50)

    def test_forget_least_relevant(self):
        """Prueba que se olvida el recuerdo menos accedido."""
        self.mem.log_episode(type="forget_test", source="test", data={"id": 1, "content": "olvidable"})
        self.mem.log_episode(type="forget_test", source="test", data={"id": 2, "content": "importante"})
        
        self.mem.get_memory(query="importante")

        self.mem.forget_least_relevant(n_items=1)

        all_memories = self.mem._load_from_db()
        contents = [m['data']['content'] for m in all_memories]
        self.assertNotIn("olvidable", contents)
        self.assertIn("importante", contents)

    def test_delete_episode(self):
        """Prueba que se puede eliminar un episodio específico por su ID."""
        episode = self.mem.log_episode(type="delete_test", source="test", data={"content": "borrame"})
        episode_id = episode['id']

        self.assertEqual(len(self.mem.get_memory(query="borrame")), 1)

        deleted = self.mem.delete_episode(episode_id)
        self.assertTrue(deleted)

        self.assertEqual(len(self.mem.get_memory(query="borrame")), 0)

    def test_get_instance_id_is_persistent(self):
        """Prueba que el instance_id es único y persistente."""
        instance_id_1 = self.mem.get_instance_id()
        instance_id_2 = self.mem.get_instance_id()
        self.assertIsNotNone(instance_id_1)
        self.assertEqual(instance_id_1, instance_id_2)
