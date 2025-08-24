# Arquitectura de MEA-Core

Este documento describe la arquitectura de alto nivel del proyecto MEA-Core, sus componentes principales y el flujo de datos entre ellos.

## 1. Filosofía de Diseño

MEA-Core está diseñado bajo los siguientes principios:

- **Modularidad:** Cada componente tiene una responsabilidad única y clara. Esto permite que las partes del sistema (memoria, conocimiento, ética) puedan ser modificadas o reemplazadas con un impacto mínimo en el resto del sistema.
- **Extensibilidad:** El sistema está preparado para crecer a través de plugins y la adición de nuevos módulos o interfaces (bots, APIs).
- **Independencia Local:** El núcleo de la IA está diseñado para funcionar de manera local, sin depender de servicios en la nube para sus operaciones principales.

## 2. Estructura de Directorios Principales

La organización del proyecto refleja su arquitectura modular:

- **/core:** Contiene la lógica central y los componentes que conforman el "cerebro" de la IA.
- **/bots:** Interfaces para interactuar con la IA (CLI, Discord, Telegram).
- **/server:** Una API basada en FastAPI para la interacción remota y el aprendizaje.
- **/webapp:** Una interfaz de usuario web moderna (React) para la interacción.
- **/data:** Almacenamiento persistente, principalmente bases de datos SQLite para la memoria, el conocimiento y otros estados.
- **/config:** Archivos de configuración (JSON) que definen el comportamiento del sistema.
- **/docs:** Documentación del proyecto (como este mismo archivo).
- **/tests:** Pruebas automatizadas (unitarias y de integración) para garantizar la estabilidad.
- **/tools:** Scripts de utilidad para la gestión y mantenimiento del proyecto.

## 3. Componentes del Núcleo (`core/`)

El directorio `core` es el corazón de la aplicación. Sus componentes clave son:

- **`brain.py` (Cerebro):** Es el orquestador central. Recibe la entrada del usuario y decide cómo generar una respuesta. No contiene la lógica de respuesta en sí misma, sino que delega en otros componentes según su modo de operación.

- **Modos de Operación del Cerebro:**
    1.  **`rule_engine` (Motor de Reglas):** Utiliza la librería `Experta` para un razonamiento basado en reglas complejas. Es el modo por defecto y más sofisticado.
    2.  **`ml` (Machine Learning):** Utiliza un modelo de `scikit-learn` para clasificar la intención del usuario y seleccionar una respuesta predefinida.
    3.  **`rule` (Reglas Simples):** Un sistema básico de mapeo directo de entrada a respuesta, usado como fallback.

- **Módulos de Soporte del Cerebro:**
    - **`knowledge_base.py`:** Gestiona el acceso a la base de conocimiento (`knowledge_base.db`). Proporciona métodos para la búsqueda de información, utilizando tanto técnicas de búsqueda de texto (BM25) como de búsqueda semántica (vectores).
    - **`memory_store.py`:** Administra la memoria de la IA (`mea_memory.db`, `central_memory.db`), permitiendo guardar y recuperar experiencias pasadas.
    - **`memory_consolidator.py`:** Módulo para procesar y consolidar recuerdos, resumiendo conversaciones y extrayendo entidades clave.
    - **`goal_manager.py`:** Permite a la IA tener y seguir objetivos a largo plazo, revisando su progreso periódicamente.
    - **`ethics.py`:** Un componente diseñado para evaluar las acciones de la IA contra un conjunto de principios éticos.
    - **`curiosity.py`, `evolution.py`, `swarm.py`:** Módulos esqueleto preparados para futuras capacidades avanzadas como el aprendizaje proactivo, la auto-mejora y la operación en enjambre.

## 4. Flujo de Datos: Ciclo de una Interacción

El flujo de información para una interacción típica es el siguiente:

1.  **Entrada:** Un usuario envía un mensaje a través de una de las interfaces (ej. el CLI en `bots/cli_bot.py`).
2.  **Delegación:** La interfaz recibe el mensaje y lo pasa al `Brain` para su procesamiento.
3.  **Procesamiento en el Cerebro:**
    a. El `Brain` determina el modo de operación (ej. `rule_engine`).
    b. El motor correspondiente se activa. Puede consultar la `KnowledgeBase` en busca de información relevante o la `MemoryStore` para recordar interacciones pasadas.
    c. El `GoalManager` puede ser consultado si es el momento de revisar metas.
    d. El `Ethics` module podría, en un futuro, vetar o modificar una respuesta.
4.  **Generación de Respuesta:** El motor seleccionado genera una respuesta y la devuelve al `Brain`.
5.  **Salida:** El `Brain` entrega la respuesta final a la interfaz, que se la muestra al usuario.

## 5. Persistencia de Datos (`data/`)

El estado y el aprendizaje de la IA se guardan en varias bases de datos SQLite, lo que garantiza la persistencia entre sesiones:

- **`knowledge_base.db`:** Almacena documentos y textos para que la IA aprenda.
- **`mea_memory.db` / `central_memory.db`:** Guardan recuerdos de interacciones y hechos aprendidos.
- **`swarm_sync.db`:** Base de datos para la futura sincronización de agentes en enjambre.
