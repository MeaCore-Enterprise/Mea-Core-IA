import unittest
from unittest.mock import MagicMock
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memoria import MemoryStore
from core import models

class TestMemoryStore(unittest.TestCase):

    def setUp(self):
        """Configura una base de datos en memoria para cada prueba."""
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db_session = Session()
        self.mem = MemoryStore()

    def tearDown(self):
        """Cierra la conexión a la DB después de cada prueba."""
        self.db_session.close()

    def test_log_and_get_episode(self):
        """Prueba que se puede registrar y recuperar un episodio."""
        test_data = {"info": "test_value"}
        self.mem.log_episode(self.db_session, type="test_event", source="test_suite", data=test_data)
        
        retrieved_memories = self.mem.get_memory(self.db_session, query="test_value")
        self.assertEqual(len(retrieved_memories), 1)
        self.assertEqual(retrieved_memories[0]['data'], test_data)

    def test_short_term_memory_limit(self):
        """Prueba que la memoria a corto plazo respeta su límite."""
        for i in range(150): # El límite por defecto es 100
            self.mem.log_episode(self.db_session, type="short_term_test", source="test", data={"i": i}, long_term=False)
        
        self.assertEqual(len(self.mem.short_term), 100)
        self.assertEqual(self.mem.short_term[0]['data']['i'], 50)

    def test_reset_memory(self):
        """Prueba que reset_memory limpia la base de datos."""
        self.mem.log_episode(self.db_session, type="reset_test", source="test", data={"content": "borrame"})
        self.db_session.commit() # Asegurarse que se escribe en la DB

        # Verificar que la memoria no está vacía
        memories = self.db_session.query(models.EpisodicMemory).all()
        self.assertGreater(len(memories), 0)

        # Resetear
        self.mem.reset_memory(self.db_session)

        # Verificar que la memoria está vacía
        memories_after_reset = self.db_session.query(models.EpisodicMemory).all()
        self.assertEqual(len(memories_after_reset), 0)

if __name__ == '__main__':
    unittest.main()