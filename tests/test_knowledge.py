
import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):

    def setUp(self):
        """Crea una base de datos de conocimiento de prueba en memoria."""
        self.db_path = ":memory:"
        self.kb = KnowledgeBase(path=self.db_path)

    def test_add_and_get_principle(self):
        """Prueba que se puede añadir y recuperar un principio."""
        self.kb.add_principle("TestDoc", "TestCat", "Este es un principio de prueba.")
        principles = self.kb.get_principles_by_category("TestCat")
        self.assertEqual(len(principles), 1)
        self.assertEqual(principles[0][2], "Este es un principio de prueba.")

    def test_add_duplicate_principle(self):
        """Prueba que no se añaden principios duplicados."""
        content = "Un principio único."
        self.kb.add_principle("Doc1", "Cat1", content)
        self.kb.add_principle("Doc2", "Cat2", content) # Intentar añadir de nuevo
        
        all_principles = self.kb.get_all_principles()
        self.assertEqual(len(all_principles), 1)

    def test_get_by_category_like(self):
        """Prueba la búsqueda de categorías con LIKE."""
        self.kb.add_principle("DocA", "Ética Fundamental", "Principio A")
        self.kb.add_principle("DocB", "Ética Aplicada", "Principio B")
        self.kb.add_principle("DocC", "Arquitectura", "Principio C")

        ethical_principles = self.kb.get_principles_by_category("Ética")
        self.assertEqual(len(ethical_principles), 2)

        arch_principles = self.kb.get_principles_by_category("Arquitectura")
        self.assertEqual(len(arch_principles), 1)

if __name__ == "__main__":
    unittest.main()
