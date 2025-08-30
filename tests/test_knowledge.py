import unittest
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.conocimiento import KnowledgeManager

class TestKnowledgeManager(unittest.TestCase):

    def setUp(self):
        """Crea una base de datos y un grafo de prueba en memoria/temporales."""
        self.db_path = ":memory:"
        self.graph_path = "data/test_knowledge_graph.gml"
        self.km = KnowledgeManager(db_path=self.db_path, graph_path=self.graph_path)

    def tearDown(self):
        """Cierra la conexión a la DB y elimina el archivo de grafo temporal."""
        self.km.close()
        if os.path.exists(self.graph_path):
            os.remove(self.graph_path)

    def test_add_fact_and_db_storage(self):
        """Prueba que un hecho se añade correctamente a la base de datos."""
        fact = "La IA aprende de datos"
        self.km.add_fact(fact)
        
        cursor = self.km.conn.cursor()
        cursor.execute("SELECT content FROM facts WHERE content=?", (fact,))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], fact)

    def test_add_fact_and_graph_creation(self):
        """Prueba que un hecho añade nodos y relaciones al grafo."""
        fact = "MEA-Core usa Python"
        self.km.add_fact(fact)
        
        self.assertTrue(self.km.graph.has_node("MEA-Core"))
        self.assertTrue(self.km.graph.has_node("Python"))
        self.assertTrue(self.km.graph.has_edge("MEA-Core", "Python"))
        edge_data = self.km.graph.get_edge_data("MEA-Core", "Python")
        self.assertEqual(edge_data['label'], 'usa')

    def test_add_relation(self):
        """Prueba que se puede añadir una relación explícita."""
        self.km.add_relation("Gemini", "Google", "es de")
        self.assertTrue(self.km.graph.has_edge("Gemini", "Google"))
        self.assertEqual(self.km.graph.get_edge_data("Gemini", "Google")['label'], "es de")

    def test_query(self):
        """Prueba que una consulta devuelve tanto hechos como relaciones."""
        self.km.add_fact("La IA necesita ética")
        self.km.add_fact("La ética guía a la IA")

        results = self.km.query("La ética")
        
        # La búsqueda LIKE '%La ética%' solo debe encontrar el hecho que lo contiene literalmente
        self.assertEqual(len(results['direct_facts']), 1)
        self.assertIn("La ética guía a la IA", results['direct_facts'])
        self.assertNotIn("La IA necesita ética", results['direct_facts'])
        
        # La búsqueda de relaciones debe ser exacta con el nodo
        self.assertEqual(len(results['relations']), 1)
        self.assertIn("La ética -> guía -> a la IA", results['relations'])

    def test_save_and_load_graph(self):
        """Prueba que el grafo se guarda y se carga correctamente."""
        self.km.add_fact("El sol es una estrella")
        self.km.save()

        # Crear una nueva instancia para forzar la carga desde el archivo
        new_km = KnowledgeManager(db_path=self.db_path, graph_path=self.graph_path)
        self.assertTrue(new_km.graph.has_node("El sol"))
        self.assertTrue(new_km.graph.has_edge("El sol", "una estrella"))
        new_km.close()

    def test_duplicate_fact(self):
        """Prueba que añadir un hecho duplicado no causa errores ni duplicados."""
        fact = "El cielo es azul"
        self.km.add_fact(fact)
        self.km.add_fact(fact) # Añadir por segunda vez

        cursor = self.km.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM facts WHERE content=?", (fact,))
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
        self.assertEqual(len(self.km.graph.nodes()), 2)

if __name__ == "__main__":
    unittest.main()