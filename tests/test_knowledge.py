import unittest
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.conocimiento import KnowledgeManager
from core import models

class TestKnowledgeManager(unittest.TestCase):

    def setUp(self):
        """Crea una base de datos y un grafo de prueba en memoria/temporales."""
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db_session = Session()
        self.graph_path = "data/test_knowledge_graph.gml"
        self.km = KnowledgeManager(db_session=self.db_session, graph_path=self.graph_path)

    def tearDown(self):
        """Cierra la sesión de la DB y elimina el grafo de prueba."""
        self.db_session.close()
        if os.path.exists(self.graph_path):
            os.remove(self.graph_path)

    def test_add_fact_and_query(self):
        """Prueba que se puede añadir un hecho y luego consultarlo."""
        fact_text = "La IA es una herramienta poderosa."
        self.km.add_fact(self.db_session, fact_text)
        
        # Verificar que el hecho está en la base de datos
        db_fact = self.db_session.query(models.Fact).filter_by(content=fact_text).first()
        self.assertIsNotNone(db_fact)

        # Consultar el hecho
        results = self.km.query(self.db_session, "herramienta")
        self.assertIn(fact_text, [fact for fact, score in results['ranked_facts']])

    def test_duplicate_fact(self):
        """Prueba que no se añaden hechos duplicados."""
        fact_text = "Los datos son el nuevo petróleo."
        self.km.add_fact(self.db_session, fact_text)
        self.km.add_fact(self.db_session, fact_text)

        count = self.db_session.query(models.Fact).filter_by(content=fact_text).count()
        self.assertEqual(count, 1)

    def test_save_and_load_graph(self):
        """Prueba que el grafo se guarda y se carga correctamente."""
        # La funcionalidad de añadir relaciones no está implementada en el mock,
        # pero podemos probar que el archivo se crea.
        self.km.save_graph()
        self.assertTrue(os.path.exists(self.graph_path))

        # Crear un nuevo gestor para probar la carga
        km2 = KnowledgeManager(db_session=self.db_session, graph_path=self.graph_path)
        self.assertIsNotNone(km2.graph)

if __name__ == '__main__':
    unittest.main()
