import unittest
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memoria import MemoryStore
from core import models

class TestMemoryPersistence(unittest.TestCase):

    def setUp(self):
        """Configura una base de datos en un archivo temporal para las pruebas."""
        self.db_path = "data/test_persistence.db"
        # Asegurarse de que no haya una base de datos de una prueba anterior
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def tearDown(self):
        """Limpia el archivo de la base de datos después de cada prueba."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_persistence_across_instances(self):
        """Prueba que los recuerdos persisten en la DB entre diferentes instancias."""
        # --- Primera Instancia: Guardar un recuerdo ---
        session1 = self.Session()
        mem1 = MemoryStore()
        test_data = {"info": "datos persistentes"}
        mem1.log_episode(session1, type="persistence_test", source="test_suite", data=test_data)
        session1.commit()
        session1.close()

        # --- Segunda Instancia: Cargar y verificar ---
        session2 = self.Session()
        mem2 = MemoryStore()
        retrieved_memories = mem2.get_memory(session2, query="datos persistentes")
        self.assertEqual(len(retrieved_memories), 1)
        self.assertEqual(retrieved_memories[0]['data'], test_data)
        session2.close()

    def test_reset_memory_clears_db_file(self):
        """Prueba que reset_memory() limpia permanentemente el archivo de la DB."""
        # --- Primera Instancia: Guardar y resetear ---
        session1 = self.Session()
        mem1 = MemoryStore()
        mem1.log_episode(session1, type="reset_test", source="test_suite", data={"info": "datos a borrar"})
        session1.commit()

        # Verificar que el dato está ahí
        self.assertEqual(len(mem1.get_memory(session1, query="datos a borrar")), 1)

        # Resetear la memoria
        mem1.reset_memory(session1)
        self.assertEqual(len(mem1.get_memory(session1, query="datos a borrar")), 0)
        session1.close()

        # --- Segunda Instancia: Verificar que la DB está vacía ---
        session2 = self.Session()
        memories_after_reset = session2.query(models.EpisodicMemory).all()
        self.assertEqual(len(memories_after_reset), 0)
        session2.close()

if __name__ == '__main__':
    unittest.main()