import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):

    def setUp(self):
        """Crea una base de datos de conocimiento de prueba en memoria."""
        # Usamos una base de datos en memoria para cada prueba
        self.kb = KnowledgeBase(path=":memory:")
        # Añadimos datos de prueba comunes aquí para que estén disponibles en todos los tests
        self.kb.add_principle("Manifiesto A", "Ética", "Proteger siempre al usuario.")
        self.kb.add_principle("Manifiesto B", "Arquitectura", "El sistema debe ser modular y escalable.")
        self.kb.add_principle("Manifiesto C", "Ética", "La IA no debe causar daño a los humanos.")
        # Reconstruimos el índice después de añadir los principios de prueba
        self.kb.principles = self.kb.get_all_principles()
        corpus = [p[2] for p in self.kb.principles]
        tokenized_corpus = [doc.lower().split(" ") for doc in corpus]
        from rank_bm25 import BM25Okapi
        self.kb.bm25 = BM25Okapi(tokenized_corpus)


    def test_add_and_get_principle(self):
        """Prueba que se puede añadir y recuperar un principio."""
        # Este test ahora se beneficia de los datos del setUp
        principles = self.kb.get_principles_by_category("Ética")
        self.assertEqual(len(principles), 2)

    def test_add_duplicate_principle(self):
        """Prueba que no se añaden principios duplicados."""
        # Intentar añadir un principio que ya existe desde el setUp
        self.kb.add_principle("Doc1", "Cat1", "Proteger siempre al usuario.")
        all_principles = self.kb.get_all_principles()
        self.assertEqual(len(all_principles), 3) # Debería seguir siendo 3

    def test_get_by_category_like(self):
        """Prueba la búsqueda de categorías con LIKE."""
        ethical_principles = self.kb.get_principles_by_category("Ética")
        self.assertEqual(len(ethical_principles), 2)

        arch_principles = self.kb.get_principles_by_category("Arquitectura")
        self.assertEqual(len(arch_principles), 1)

    def test_search_with_bm25(self):
        """Prueba la nueva funcionalidad de búsqueda con BM25."""
        # 1. Búsqueda relevante
        query = "¿Cuál es la directriz sobre el daño?"
        results = self.kb.search(query, top_n=1)
        self.assertEqual(len(results), 1)
        # El resultado más relevante debería ser sobre "no causar daño"
        self.assertIn("daño", results[0][2])

        # 2. Búsqueda sobre arquitectura
        query_arch = "¿Cómo debe ser la arquitectura del sistema?"
        results_arch = self.kb.search(query_arch, top_n=1)
        self.assertEqual(len(results_arch), 1)
        self.assertIn("modular y escalable", results_arch[0][2])

        # 3. Búsqueda no relevante
        query_irrelevant = "¿De qué color es el cielo?"
        results_irrelevant = self.kb.search(query_irrelevant)
        self.assertEqual(len(results_irrelevant), 0)

if __name__ == "__main__":
    unittest.main()