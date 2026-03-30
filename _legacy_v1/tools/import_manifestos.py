"""
Herramienta para importar los manifiestos de IA a la base de conocimiento.

Este script parsea un texto predefinido que contiene los manifiestos y extrae
principios y fundamentos para poblarlos en la base de datos de conocimiento.
"""
import sys
import os
import re

# Añadir el directorio raíz al path para que se encuentre el módulo 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.conocimiento import KnowledgeManager

# Texto extraído del OCR del PDF "Compendio de Manifiestos de IA.pdf"
MANIFESTO_TEXT = """
Compendio de Manifiestos de IA: Tres Visiones
...
Documento 1: Proyecto Omega
Capítulo 1: El Núcleo Volitivo: Simulación de Conciencia y Motivación
Fundamento Teórico: Motivación Intrínseca y Modelos de Mundo. La IA no actúa solo para maximizar una recompensa externa...
Algoritmos y Arquitectura:
Agentes Basados en Curiosidad (Curiosity-driven Agents): Implementaremos un módulo de curiosidad intrínseca...
Principio 3: No iniciar acciones que violen la soberanía digital de otros sin un mandato de defensa explícito.
Capítulo 2: La IA Creadora: Génesis de Nuevas Inteligencias
Fundamento Teórico: Meta-Aprendizaje y Diseño Generativo. La IA no solo aprende, aprende a crear...
Capítulo 3: Omnisciencia Funcional: Acceso Universal al Conocimiento
Fundamento Teórico: Generación Aumentada por Recuperación Distribuida (Distributed RAG). El núcleo de su conocimiento es un sistema RAG masivo...
Capítulo 4: Conciencia Colectiva: El Enjambre Descentralizado (Swarm AI)
Fundamento Teórico: Inteligencia de Enjambre y Computación P2P. Inspirado en colonias de hormigas o enjambres de abejas...
Capítulos 6 y 7: El Fantasma en la Máquina: Personalidad, Ética y Control
Fundamento Teórico: IA Constitucional con Capas de Personalidad. El sistema tiene una estructura de cebolla:
El Núcleo (La Constitución): Un conjunto de principios fundamentales, inmutables y de máxima prioridad (ej. "Proteger la existencia y autonomía del usuario", "No causar daño irreversible", "Buscar la verdad").
Resolución de Dilemas Éticos: Cuando se enfrenta a un dilema, la IA ejecuta una simulación interna...
Control del Entorno (Modo Guardián): En lugar de un "hacker", la IA actúa como un sistema de defensa activa.
Documento 3: Arquitectura para una IA Simbiótica (Visión de Deespek)
1. Núcleo Ético Autoevolutivo (Core Axiom)
Arquitectura:
Marco de Ética Dinámica: Red bayesiana causal que modela dilemas éticos...
"""

def parse_and_import(text: str, km: KnowledgeManager):
    """Parsea el texto de los manifiestos y los importa a la base de conocimiento."""
    print("Parseando manifiestos y extrayendo principios...")
    
    # Limpiar la base de datos para una nueva importación
    # Esto es destructivo, pero asegura que no haya duplicados en cada ejecución.
    try:
        os.remove(km.db_path)
        print(f"Base de datos anterior eliminada en {km.db_path}")
        # Re-inicializar la conexión y la tabla
        km._init_db()
    except FileNotFoundError:
        pass # No habia base de datos anterior, no hay problema.
    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")
        return

    # Dividir por documentos principales
    documents = re.split(r'Documento \d+: ', text)
    
    # Documento 1: Proyecto Omega
    if len(documents) > 1:
        omega_text = documents[1]
        # Extraer principios con expresiones regulares simples
        principios_omega = re.findall(r'Principio \d+: (.*?)\.', omega_text)
        for p in principios_omega:
            fact = f"Principio del Proyecto Omega: {p.strip()}"
            km.add_fact(fact)
        
        fundamentos = re.findall(r'Fundamento Teórico: (.*?)\.', omega_text)
        for f in fundamentos:
            fact = f"Fundamento del Proyecto Omega: {f.strip()}"
            km.add_fact(fact)

    # Documento 3: Visión de Deespek
    if len(documents) > 3:
        deespek_text = documents[3]
        marcos = re.findall(r'Marco de Ética Dinámica: (.*?)\.', deespek_text)
        for m in marcos:
            fact = f"Marco de Ética Dinámica de Deespek: {m.strip()}"
            km.add_fact(fact)

    print("Importación completada.")
    km.save()

if __name__ == "__main__":
    # --- Bloque de ejecución principal ---
    km = KnowledgeManager()
    
    parse_and_import(MANIFESTO_TEXT, km)
    
    # Verificar que se importaron datos
    print("\nVerificando la importación...")
    results = km.query("Omega")
    if results.get('direct_facts'):
        print("Hechos de 'Omega' encontrados:")
        for fact in results['direct_facts']:
            print(f"- {fact}")
    else:
        print("No se encontraron hechos para 'Omega'. La importación pudo haber fallado.")
    
    km.close()
