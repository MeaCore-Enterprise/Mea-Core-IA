# Roadmap de Producto - Mea-Core Enterprise

Este documento describe la dirección futura del producto, los hitos clave y las características planificadas.

## Q4 2025: Lanzamiento Beta y Validación de Mercado (Fase 9)

-   **Objetivo**: Validar los casos de uso principales con clientes reales y obtener feedback para el producto v1.1.
-   **Hitos Clave**:
    -   [ ] **Onboarding de Clientes Beta**: Integrar con éxito a 5-10 clientes beta en la plataforma (On-Premise o SaaS gestionado).
    -   [ ] **Recopilación de Feedback**: Establecer canales directos de comunicación con los testers para identificar puntos de fricción y características deseadas.
    -   [ ] **Análisis de Métricas de Uso**: Implementar telemetría básica (anónima y con consentimiento) para entender cómo se utiliza el producto.
    -   [ ] **Preparación para Inversión**: Refinar el `PITCH_DECK.md` con datos y testimonios reales del programa beta.

## Q1 2026: Versión 1.1 - Enfoque en la Experiencia de Cliente

-   **Objetivo**: Incorporar el feedback de los clientes beta y mejorar drásticamente la experiencia de usuario y de administrador.
-   **Características Planeadas**:
    -   [ ] **Dashboard de Cliente Mejorado**: Añadir gráficos de uso, gestión de facturación y un sistema de tickets de soporte integrado.
    -   [ ] **Marketplace de Plugins (UI)**: Desarrollar la interfaz de usuario para que los administradores puedan descubrir, instalar y configurar plugins con un solo clic.
    -   [ ] **Mejoras en la WebApp de Chat**: Añadir historial de conversaciones, capacidad de calificar respuestas y subida de documentos directamente desde el chat.
    -   [ ] **Documentación Pública**: Lanzar un sitio de documentación (`docs.meacore.ai`) con guías completas, tutoriales y referencias de API.

## Q2 2026: Versión 1.2 - Madurez del Enjambre y la IA

-   **Objetivo**: Mejorar la inteligencia y las capacidades de colaboración del enjambre.
-   **Características Planeadas**:
    -   [ ] **Votación y Consenso**: Implementar algoritmos de consenso (ej. Raft simplificado) para que el enjambre pueda tomar decisiones distribuidas.
    -   [ ] **Asignación Dinámica de Tareas**: Permitir que el enjambre asigne tareas complejas a los nodos más adecuados (ej. un nodo con GPU para tareas de visión artificial).
    -   [ ] **Aprendizaje Federado v2**: Mover el prototipo de `scikit-learn` a una implementación más robusta con `PyTorch` o `TensorFlow Federated`.
    -   [ ] **Motor de Curiosidad Activa**: La IA no solo identificará gaps de conocimiento, sino que podrá solicitar permiso para buscar activamente esa información en fuentes externas pre-aprobadas.

## H2 2026: Versión 2.0 - Expansión y Ecosistema

-   **Objetivo**: Expandir Mea-Core más allá de una plataforma a un verdadero ecosistema.
-   **Características Planeadas**:
    -   [ ] **SDK de Plugins Público**: Lanzar un kit de desarrollo de software (SDK) para que terceros puedan crear y monetizar sus propios plugins en nuestro marketplace.
    -   **Integraciones Nativas**: Ofrecer integraciones con plataformas clave como Salesforce, SAP, Slack y Microsoft Teams.
    -   **Multimodalidad Avanzada**: Añadir capacidades de entrada y salida de audio y video, permitiendo casos de uso como resúmenes de reuniones o análisis de videovigilancia.
    -   **Despliegue Multi-Nube**: Ofrecer soporte oficial y scripts para despliegues híbridos y multi-nube (AWS, Azure, GCP).
