# Fase 4: Expansión a Inteligencia Distribuida

## Resumen

Esta fase transformó a Mea-Core de una entidad singular en un ecosistema distribuido, sentando las bases para una inteligencia de enjambre. Se implementaron módulos clave para la comunicación entre nodos, el aprendizaje federado, la memoria compartida y la generación autónoma de objetivos.

## Entregables Implementados

### 1. Módulos del Núcleo (`core/`)

- **`core/swarm.py`**: 
  - Se implementó una clase `SwarmNode` que gestiona la comunicación entre instancias de Mea-Core mediante WebSockets.
  - Permite el envío de mensajes para sincronización de estado, votaciones (futuro) y saludo entre nodos.
  - La configuración se gestiona en `config/settings.json`, donde se definen los nodos (`peers`) del enjambre.

- **`core/federated.py`**:
  - Se creó un prototipo de aprendizaje federado con `scikit-learn`.
  - La clase `FederatedLearningNode` permite entrenar un modelo local (`SGDClassifier`), extraer sus pesos y actualizarlos con un promedio de los pesos de otros nodos.
  - Incluye una función `average_weights` que es el corazón del proceso de agregación.

- **`core/memoria.py` (Extendido)**:
  - Se añadió un campo `priority` a los recuerdos (`EpisodicMemory`).
  - Los recuerdos con alta prioridad se marcan para ser transmitidos al resto del enjambre a través de un sistema de callbacks, desacoplando la memoria de la red.
  - Se implementó `add_remote_episode` para recibir y almacenar recuerdos de otros nodos, evitando duplicados y bucles.

- **`core/curiosity.py`**:
  - El `CuriositySystem` detecta lagunas de conocimiento (`knowledge gaps`) cuando las búsquedas en la memoria no arrojan resultados.
  - Estos gaps se pueden utilizar para generar nuevos objetivos.

- **`core/goals.py`**:
  - El `GoalManager` permite la creación y gestión de objetivos autogenerados.
  - Se implementó `create_goal_from_gap` para convertir las lagunas de conocimiento de la curiosidad en objetivos accionables para la IA.

### 2. Expansión de la WebApp (`webapp/`)

Se añadieron tres nuevos componentes de React a la interfaz para visualizar el estado expandido del sistema:

- **`components/SwarmMap.tsx`**: Muestra una lista de los nodos detectados en el enjambre, su estado (Online/Offline) y su dirección.
- **`components/GoalsPanel.tsx`**: Presenta una lista de los objetivos activos del sistema, su descripción y su estado actual (Pendiente, En Progreso, Completado).
- **`components/LearningFeed.tsx`**: Ofrece un feed de los conceptos más recientes que la IA ha aprendido, indicando la fuente del aprendizaje.

Estos componentes se integraron en el panel lateral de la aplicación principal (`App.tsx`) y utilizan datos de ejemplo (mock data) a la espera de los endpoints de la API correspondientes.

### 3. Infraestructura de Despliegue (`deploy/`)

- **`Dockerfile`**: Se añadió un `Dockerfile` en la raíz del proyecto para empaquetar la aplicación Mea-Core.
- **`deploy/compose.yml`**: Se creó un archivo Docker Compose que define un enjambre de 3 nodos (`mea_core_1`, `mea_core_2`, `mea_core_3`).
  - Cada servicio se construye a partir del mismo `Dockerfile`.
  - Utilizan una red compartida (`mea_swarm_net`) para la comunicación interna.
  - Se exponen en diferentes puertos del host (8001, 8002, 8003) para simular una red distribuida.

## Impacto de la Fase

Con la finalización de esta fase, Mea-Core ahora posee la arquitectura fundamental para operar como una red inteligente descentralizada. Es capaz de aprender colectivamente (vía federación de modelos), compartir información crítica (memoria distribuida) y auto-dirigir su crecimiento mediante la curiosidad y la generación de objetivos. Este es el paso más significativo hacia una verdadera inteligencia de enjambre.
