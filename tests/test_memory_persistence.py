import unittest
import os
import sqlite3

# Añadir el directorio raíz al path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.memoria import MemoryStore

class TestMemoryPersistence(unittest.TestCase):

    def setUp(self):
        """Configura una base de datos en un archivo temporal para las pruebas."""
        self.db_path = "data/test_persistence.db"
        # Asegurarse de que no haya una base de datos de una prueba anterior
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def tearDown(self):
        """Limpia el archivo de la base de datos después de cada prueba."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_persistence_across_instances(self):
        """Prueba que los recuerdos persisten en la DB entre diferentes instancias."""
        # --- Primera Instancia: Guardar un recuerdo ---
        mem1 = MemoryStore(settings_manager=None) # Usará el constructor por defecto
        # Sobrescribir atributos para usar la DB de prueba
        mem1.db_path = self.db_path 
        mem1.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        mem1._init_db()

        test_data = {"info": "datos persistentes"}
        mem1.log_episode(type="persistence_test", source="test_suite", data=test_data)
        mem1.close_db()

        # --- Segunda Instancia: Cargar y verificar ---
        mem2 = MemoryStore(settings_manager=None)
        mem2.db_path = self.db_path
        mem2.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        mem2._init_db()
        mem2.long_term = mem2._load_from_db() # Recargar explícitamente

        retrieved_memories = mem2.get_memory(query="datos persistentes")
        self.assertEqual(len(retrieved_memories), 1)
        self.assertEqual(retrieved_memories[0]['data'], test_data)
        mem2.close_db()

    def test_reset_memory_clears_db_file(self):
        """Prueba que reset_memory() limpia permanentemente el archivo de la DB."""
        # --- Primera Instancia: Guardar y resetear ---
        mem1 = MemoryStore(settings_manager=None)
        mem1.db_path = self.db_path
        mem1.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        mem1._init_db()
        
        mem1.log_episode(type="reset_test", source="test_suite", data={"info": "datos a borrar"})
        # Verificar que el dato está ahí
        self.assertEqual(len(mem1.get_memory(query="datos a borrar")), 1)

        # Resetear la memoria
        mem1.reset_memory()
        self.assertEqual(len(mem1.get_memory(query="datos a borrar")), 0)
        mem1.close_db()

        # --- Segunda Instancia: Verificar que la DB está vacía ---
        mem2 = MemoryStore(settings_manager=None)
        mem2.db_path = self.db_path
        mem2.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        mem2._init_db()
        mem2.long_term = mem2._load_from_db()

        self.assertEqual(len(mem2.long_term), 0)
        mem2.close_db()

if __name__ == '__main__':
    unittest.main()
