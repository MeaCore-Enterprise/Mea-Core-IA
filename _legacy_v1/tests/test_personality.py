
import unittest
import os
import sys
import json

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.personalidad import load_personality, save_personality, DEFAULT

class TestPersonality(unittest.TestCase):

    def setUp(self):
        """Crea un archivo de personalidad temporal."""
        self.test_path = "test_personality.json"

    def tearDown(self):
        """Elimina el archivo de personalidad temporal si existe."""
        if os.path.exists(self.test_path):
            os.remove(self.test_path)

    def test_load_default_personality(self):
        """Prueba que se carga la personalidad por defecto si el archivo no existe."""
        # Asegurarse de que el archivo no existe
        if os.path.exists(self.test_path):
            os.remove(self.test_path)
        
        persona = load_personality(path=self.test_path)
        self.assertEqual(persona, DEFAULT)
        # Verificar que el archivo fue creado
        self.assertTrue(os.path.exists(self.test_path))

    def test_load_existing_personality(self):
        """Prueba que se carga una personalidad desde un archivo existente."""
        custom_persona = {"name": "TestBot", "greeting": "Hola test!"}
        with open(self.test_path, "w", encoding="utf-8") as f:
            json.dump(custom_persona, f)
        
        persona = load_personality(path=self.test_path)
        self.assertEqual(persona, custom_persona)

    def test_save_personality(self):
        """Prueba que se puede guardar una configuración de personalidad."""
        new_persona = {"name": "SavedBot", "tone": "direct"}
        save_personality(new_persona, path=self.test_path)
        
        with open(self.test_path, "r", encoding="utf-8") as f:
            loaded_persona = json.load(f)
        
        self.assertEqual(loaded_persona, new_persona)

if __name__ == "__main__":
    unittest.main()
