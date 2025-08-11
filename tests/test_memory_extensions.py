import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memory import MemoryStore

class TestMemoryExtensions(unittest.TestCase):

    def setUp(self):
        """Usa una base de datos en memoria para cada prueba."""
        self.memory = MemoryStore(path=":memory:")

    def test_get_instance_id_creation(self):
        """Prueba que se crea un ID de instancia si no existe."""
        instance_id = self.memory.get_instance_id()
        self.assertIsInstance(instance_id, str)
        self.assertTrue(len(instance_id) > 0)

    def test_get_instance_id_retrieval(self):
        """Prueba que el ID de instancia es persistente."""
        first_id = self.memory.get_instance_id()
        second_id = self.memory.get_instance_id()
        self.assertEqual(first_id, second_id)

    def test_log_replication(self):
        """Prueba que se puede registrar una replicación."""
        clone_id = "test-clone-id-123"
        clone_path = "E:\\Mea-Core_Clone"
        self.memory.log_replication(clone_id, clone_path)

        # Verificar que el dato se escribió correctamente
        cursor = self.memory.conn.execute("SELECT path FROM replications WHERE id = ?", (clone_id,))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], clone_path)

if __name__ == "__main__":
    unittest.main()
