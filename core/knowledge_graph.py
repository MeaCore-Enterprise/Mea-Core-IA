"""
Módulo para la gestión de un Grafo de Conocimiento (Knowledge Graph).

Este módulo proporciona la estructura para almacenar y consultar conocimiento en
forma de nodos (conceptos) y aristas (relaciones), con persistencia en una
base de datos SQLite.
"""
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

class KnowledgeGraph:
    """Gestiona un grafo de conocimiento con nodos y aristas."""

    def __init__(self, db_path: str = "data/knowledge_graph.db"):
        """Inicializa el Grafo de Conocimiento y la conexión a la base de datos.

        Args:
            db_path (str): Ruta al archivo de la base de datos SQLite.
        """
        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """(Privado) Inicializa la DB y crea las tablas de nodos y aristas."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            # Tabla para los nodos (conceptos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    attributes TEXT
                )
            """)
            # Tabla para las aristas (relaciones)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    attributes TEXT,
                    PRIMARY KEY (source_id, target_id, relation)
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[KnowledgeGraph] Error en la base de datos: {e}")
            self.conn = None

    def add_node(self, node_id: str, attributes: Optional[Dict] = None) -> bool:
        """Añade un nodo (concepto) al grafo.

        Args:
            node_id (str): El identificador único del nodo.
            attributes (Optional[Dict], optional): Atributos adicionales en formato JSON. Defaults to None.

        Returns:
            bool: True si el nodo se añadió, False si ya existía o hubo un error.
        """
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO nodes (id, attributes) VALUES (?, ?)",
                         (node_id, json.dumps(attributes or {})))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # El nodo ya existe, no es un error fatal.
            return False
        except sqlite3.Error as e:
            print(f"[KnowledgeGraph] Error al añadir nodo: {e}")
            return False

    def add_edge(self, source_id: str, target_id: str, relation: str, attributes: Optional[Dict] = None) -> bool:
        """Añade una arista (relación) dirigida entre dos nodos.

        Args:
            source_id (str): El ID del nodo de origen.
            target_id (str): El ID del nodo de destino.
            relation (str): La descripción de la relación (ej. 'es_un', 'tiene_parte').
            attributes (Optional[Dict], optional): Atributos adicionales para la relación. Defaults to None.

        Returns:
            bool: True si la arista se añadió, False si ya existía o hubo un error.
        """
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO edges (source_id, target_id, relation, attributes) VALUES (?, ?, ?, ?)",
                         (source_id, target_id, relation, json.dumps(attributes or {})))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # La arista ya existe
        except sqlite3.Error as e:
            print(f"[KnowledgeGraph] Error al añadir arista: {e}")
            return False

    def get_node(self, node_id: str) -> Optional[Dict]:
        """Recupera un nodo por su ID.

        Args:
            node_id (str): El ID del nodo a buscar.

        Returns:
            Optional[Dict]: Un diccionario con los datos del nodo, o None si no se encuentra.
        """
        if not self.conn:
            return None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, attributes FROM nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()
            if row:
                return {'id': row[0], 'attributes': json.loads(row[1])}
            return None
        except sqlite3.Error as e:
            print(f"[KnowledgeGraph] Error al obtener nodo: {e}")
            return None

    def find_related_nodes(self, node_id: str, relation: Optional[str] = None) -> List[Dict]:
        """Encuentra nodos conectados a un nodo dado, opcionalmente por un tipo de relación.

        Args:
            node_id (str): El ID del nodo de origen.
            relation (Optional[str], optional): El tipo de relación a filtrar. Defaults to None.

        Returns:
            List[Dict]: Una lista de diccionarios, cada uno representando un nodo relacionado.
        """
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            if relation:
                cursor.execute("SELECT target_id FROM edges WHERE source_id = ? AND relation = ?", (node_id, relation))
            else:
                cursor.execute("SELECT target_id FROM edges WHERE source_id = ?", (node_id,))
            rows = cursor.fetchall()
            return [self.get_node(row[0]) for row in rows if self.get_node(row[0]) is not None]
        except sqlite3.Error as e:
            print(f"[KnowledgeGraph] Error al buscar nodos relacionados: {e}")
            return []

    def close_db(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            self.conn = None
