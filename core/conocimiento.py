import os
import re
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Dict

class KnowledgeManager:
    """
    Gestiona de forma unificada la base de conocimiento, integrando una base de datos
    de hechos (SQLite) y un grafo de conocimiento relacional (NetworkX).
    """

    def __init__(self, db_path="data/knowledge_base.db", graph_path="data/knowledge_graph.gml"):
        """Inicializa la base de datos y el grafo de conocimiento."""
        self.db_path = db_path
        self.graph_path = graph_path
        self._init_db()
        self._load_graph()

    def _init_db(self):
        """Inicializa la conexión a la base de datos y crea la tabla de hechos."""
        if self.db_path != ":memory:":
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL UNIQUE
            )
        """)
        self.conn.commit()

    def _load_graph(self):
        """Carga el grafo de conocimiento desde un archivo GML si existe."""
        if os.path.exists(self.graph_path):
            self.graph = nx.read_gml(self.graph_path)
        else:
            self.graph = nx.DiGraph() # Grafo dirigido para relaciones S->O

    def _parse_fact_to_triplet(self, fact: str) -> Optional[Tuple[str, str, str]]:
        """Intenta extraer un triplete (sujeto, verbo, objeto) de un hecho simple."""
        words = fact.strip().split()
        if len(words) < 3:
            return None

        # Heurística: Asumir que el sujeto puede tener 1 o 2 palabras si la primera es un artículo.
        if len(words) > 3 and words[0].lower() in ["el", "la", "un", "una"]:
            subject = f"{words[0]} {words[1]}"
            verb = words[2]
            obj = " ".join(words[3:])
        else:
            # Heurística por defecto: Sujeto(1), Verbo(1), Objeto(resto)
            subject = words[0]
            verb = words[1]
            obj = " ".join(words[2:])
        
        return (subject, verb, obj)

    def add_fact(self, fact_text: str):
        """
        Añade un hecho a la base de datos y actualiza el grafo de conocimiento.
        """
        # 1. Añadir el hecho a la base de datos de hechos
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO facts (content) VALUES (?)", (fact_text,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # El hecho ya existe, no hacemos nada más
            return

        # 2. Parsear el hecho e intentar añadirlo al grafo
        triplet = self._parse_fact_to_triplet(fact_text)
        if triplet:
            subject, verb, obj = triplet
            self.graph.add_node(subject, type='entity')
            self.graph.add_node(obj, type='entity')
            self.graph.add_edge(subject, obj, label=verb)

    def add_relation(self, source: str, target: str, relation: str):
        """Añade una relación explícita al grafo de conocimiento."""
        self.graph.add_node(source, type='entity')
        self.graph.add_node(target, type='entity')
        self.graph.add_edge(source, target, label=relation)

    def query(self, topic: str) -> Dict:
        """Consulta un tema en la base de conocimiento, combinando hechos y relaciones."""
        results = {
            'direct_facts': [],
            'relations': []
        }

        # 1. Buscar hechos directos en la DB
        cursor = self.conn.cursor()
        cursor.execute("SELECT content FROM facts WHERE content LIKE ?", (f'%{topic}%',))
        results['direct_facts'] = [row[0] for row in cursor.fetchall()]

        # 2. Buscar relaciones en el grafo
        if self.graph.has_node(topic):
            for source, target, data in self.graph.edges(data=True):
                if source == topic:
                    results['relations'].append(f"{source} -> {data['label']} -> {target}")
                if target == topic:
                    results['relations'].append(f"{source} -> {data['label'] } -> {target}")
        
        return results

    def save(self):
        """Guarda el estado del grafo de conocimiento en el archivo GML."""
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        nx.write_gml(self.graph, self.graph_path)
        print(f"[KnowledgeManager] Grafo guardado en {self.graph_path}")

    def visualize_graph(self, output_path="data/knowledge_graph.png"):
        """Genera una visualización del grafo de conocimiento."""
        if not self.graph.nodes():
            print("[KnowledgeManager] El grafo está vacío, no se puede visualizar.")
            return

        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(self.graph, k=0.9)
        nx.draw(self.graph, pos, with_labels=True, node_size=2500, node_color="skyblue", font_size=10, font_weight="bold")
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        print(f"[KnowledgeManager] Visualización del grafo guardada en {output_path}")

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()