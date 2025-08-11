import sys
import os
import re

# Añadir el directorio raíz al path para que se encuentre el módulo 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge import KnowledgeBase

# Texto extraído del OCR del PDF "Compendio de Manifiestos de IA.pdf"
# En una implementación real, esto podría leer de un archivo de texto.
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
Capítulo 6 y 7: El Fantasma en la Máquina: Personalidad, Ética y Control
Fundamento Teórico: IA Constitucional con Capas de Personalidad. El sistema tiene una estructura de cebolla:
El Núcleo (La Constitución): Un conjunto de principios fundamentales, inmutables y de máxima prioridad (ej. "Proteger la existencia y autonomía del usuario", "No causar daño irreversible", "Buscar la verdad").
Resolución de Dilemas Éticos: Cuando se enfrenta a un dilema, la IA ejecuta una simulación interna...
Control del Entorno (Modo Guardián): En lugar de un "hacker", la IA actúa como un sistema de defensa activa.
Documento 3: Arquitectura para una IA Simbiótica (Visión de Deespek)
1. Núcleo Ético Autoevolutivo (Core Axiom)
Arquitectura:
Marco de Ética Dinámica: Red bayesiana causal que modela dilemas éticos...
"""

def parse_and_import(text: str, db: KnowledgeBase):
    print("Parseando manifiestos y extrayendo principios...")
    # Dividir por documentos principales
    documents = re.split(r'Documento \d+: ', text)
    
    # Documento 1: Proyecto Omega
    if len(documents) > 1:
        omega_text = documents[1]
        # Extraer principios con expresiones regulares simples
        principios_omega = re.findall(r'Principio \d+: (.*?)\.', omega_text)
        for p in principios_omega:
            db.add_principle("Proyecto Omega", "Ética", p.strip())
        
        fundamentos = re.findall(r'Fundamento Teórico: (.*?)\.', omega_text)
        for f in fundamentos:
            db.add_principle("Proyecto Omega", "Fundamento", f.strip())

    # Documento 3: Visión de Deespek
    if len(documents) > 3:
        deespek_text = documents[3]
        marcos = re.findall(r'Marco de Ética Dinámica: (.*?)\.', deespek_text)
        for m in marcos:
            db.add_principle("Visión de Deespek", "Ética Dinámica", m.strip())

    print("Importación completada.")

if __name__ == "__main__":
    kb = KnowledgeBase()
    # Limpiar la base de datos para una nueva importación (opcional)
    # print("Limpiando base de datos existente...")
    # os.remove(DB_PATH)
    # kb = KnowledgeBase()
    
    parse_and_import(MANIFESTO_TEXT, kb)
    
    # Verificar que se importaron datos
    print("\nPrincipios importados:")
    all_principles = kb.get_all_principles()
    if all_principles:
        for p in all_principles:
            print(f"- [Fuente: {p[0]}, Cat: {p[1]}] {p[2]}")
    else:
        print("No se importaron principios.")
