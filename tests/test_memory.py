
import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory import MemoryStore

class TestMemoryStore(unittest.TestCase):

    def setUp(self):
        """Crea una base de datos de prueba en memoria."""
        self.db_path = ":memory:"
        self.mem = MemoryStore(path=self.db_path)

    def test_set_and_get(self):
        """Prueba que se puede guardar y recuperar un valor."""
        self.mem.set("test_key", "test_value")
        self.assertEqual(self.mem.get("test_key"), "test_value")

    def test_get_nonexistent(self):
        """Prueba que al buscar una clave inexistente devuelve None."""
        self.assertIsNone(self.mem.get("nonexistent_key"))

    def test_update_value(self):
        """Prueba que un valor existente se puede actualizar."""
        self.mem.set("key_to_update", "initial_value")
        self.mem.set("key_to_update", "updated_value")
        self.assertEqual(self.mem.get("key_to_update"), "updated_value")

    def test_dump_all(self):
        """Prueba que se pueden volcar todos los pares clave-valor."""
        self.mem.set("key1", "value1")
        self.mem.set("key2", "value2")
        dump = self.mem.dump_all()
        self.assertEqual(dump, {"key1": "value1", "key2": "value2"})

if __name__ == "__main__":
    unittest.main()
