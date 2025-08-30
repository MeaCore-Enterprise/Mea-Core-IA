import unittest
import os
import sys
import time

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cargador import CoreLoader

# Crear un plugin de prueba
PLUGIN_DIR = os.path.join(os.path.dirname(__file__), '..', 'plugins')
TEST_PLUGIN_PATH = os.path.join(PLUGIN_DIR, 'test_plugin.py')

def create_test_plugin():
    if not os.path.exists(PLUGIN_DIR):
        os.makedirs(PLUGIN_DIR)
    with open(TEST_PLUGIN_PATH, 'w') as f:
        f.write('def run(): print("Test plugin running!")\n')
        f.write('def stop(): print("Test plugin stopping!")\n')

def remove_test_plugin():
    if os.path.exists(TEST_PLUGIN_PATH):
        os.remove(TEST_PLUGIN_PATH)

class TestCoreLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_test_plugin()

    @classmethod
    def tearDownClass(cls):
        remove_test_plugin()

    def setUp(self):
        self.loader = CoreLoader()

    def test_discover(self):
        """Prueba que el loader descubre plugins existentes."""
        plugins = self.loader.discover()
        self.assertIn('logger', plugins)
        self.assertIn('test_plugin', plugins)

    def test_load(self):
        """Prueba que un plugin se puede cargar correctamente."""
        handle = self.loader.load('test_plugin')
        self.assertIsNotNone(handle)
        self.assertIn('test_plugin', self.loader.plugins)
        self.assertTrue(hasattr(handle.module, 'run'))

    def test_start_and_stop(self):
        """Prueba que un plugin puede ser iniciado y detenido."""
        # Nota: La prueba real de hilos es compleja, aquí solo probamos la ejecución
        self.assertTrue(self.loader.start('test_plugin'))
        handle = self.loader.plugins.get('test_plugin')
        self.assertIsNotNone(handle.thread)
        time.sleep(0.1) # Dar tiempo al hilo para que inicie
        self.assertTrue(handle.thread.is_alive())
        # Darle tiempo al hilo para que corra
        time.sleep(0.1)
        # La detención en este diseño es cooperativa, solo llamamos al método
        self.assertTrue(self.loader.stop('test_plugin'))

if __name__ == "__main__":
    unittest.main()
