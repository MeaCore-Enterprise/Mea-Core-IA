# core/curiosity.py

from typing import List, Dict, Set
from sqlalchemy.orm import Session

# Asumiendo que los gaps se guardarán en una tabla para persistencia
from . import models 

class CuriositySystem:
    """
    Gestiona la identificación de lagunas de conocimiento (gaps).
    """
    def __init__(self):
        # Usamos un set para evitar duplicados de gaps en la sesión actual
        self.identified_gaps: Set[str] = set()

    def identify_knowledge_gap(self, db: Session, search_query: str, search_results: List[Dict]) -> None:
        """
        Analiza los resultados de una búsqueda para identificar un posible gap.
        Si una búsqueda no arroja resultados, se considera un gap.
        
        Args:
            db (Session): La sesión de la base de datos para registrar el gap.
            search_query (str): El término de búsqueda que se utilizó.
            search_results (List[Dict]): La lista de resultados obtenidos.
        """
        if not search_results:
            normalized_query = search_query.lower().strip()
            if normalized_query and normalized_query not in self.identified_gaps:
                self.identified_gaps.add(normalized_query)
                print(f"[Curiosidad] Detectado gap de conocimiento: '{normalized_query}'")
                # Opcional: Guardar el gap en la base de datos para análisis futuro
                # self._save_gap_to_db(db, normalized_query)

    def get_identified_gaps(self) -> List[str]:
        """
        Devuelve la lista de gaps de conocimiento identificados en la sesión actual.
        """
        return list(self.identified_gaps)

    def _save_gap_to_db(self, db: Session, gap_query: str):
        """
        (Función futura) Guarda un gap de conocimiento en una tabla de la base de datos
        para que el sistema de objetivos pueda usarlo.
        """
        # Aquí se implementaría la lógica para guardar el gap en una tabla `knowledge_gaps`
        # Por ejemplo:
        # new_gap = models.KnowledgeGap(query=gap_query, status='new')
        # db.add(new_gap)
        # db.commit()
        pass

# Ejemplo de cómo se integraría en el flujo principal:

def example_usage_flow():
    from .memoria import MemoryStore
    from .database import SessionLocal

    db = SessionLocal()
    memory = MemoryStore()
    curiosity = CuriositySystem()

    # 1. El usuario hace una pregunta que la IA no conoce
    query = "¿Qué es la computación cuántica adiabática?"
    results = memory.get_memory(db, query)

    # 2. El sistema de curiosidad analiza el resultado
    curiosity.identify_knowledge_gap(db, query, results)

    # 3. El sistema de objetivos podría usar estos gaps para crear nuevas metas
    gaps = curiosity.get_identified_gaps()
    if gaps:
        print(f"Gaps de conocimiento para el sistema de objetivos: {gaps}")
    
    db.close()

if __name__ == '__main__':
    # Este es un ejemplo y no se ejecutará directamente en producción.
    # Muestra cómo las partes se conectarían.
    print("Ejecutando ejemplo de uso del sistema de curiosidad...")
    # Para ejecutar este ejemplo, necesitaríamos configurar la DB y modelos.
    # example_usage_flow()
    print("Ejemplo finalizado. Se necesitaría una base de datos activa para una prueba completa.")
