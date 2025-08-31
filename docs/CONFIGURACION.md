# Guía de Configuración (`settings.json`)

Este documento detalla las opciones de configuración disponibles en el archivo `config/settings.json`.

---

## 1. `brain`

Esta sección controla el comportamiento del núcleo de razonamiento de la IA.

-   **`mode`**: Define el modo de operación principal del cerebro.
    -   **Valores posibles**:
        -   `"rule"`: (Modo simple por defecto) El cerebro solo responderá a coincidencias exactas definidas en `config/responses.json`. Es el modo más rápido y predecible.
        -   `"rule_engine"`: (Recomendado para MVP) Utiliza el motor de reglas `Experta` para un razonamiento más complejo basado en hechos y reglas lógicas. Permite un comportamiento más dinámico que el modo `rule`.
        -   `"ml"`: Utiliza un modelo de Machine Learning (clasificador simple) para predecir la intención del usuario. Requiere `scikit-learn`.
    -   **Fallback**: El cerebro está diseñado para ser robusto. Si un modo falla (p. ej., `ml` falla por falta de dependencias), intentará automáticamente usar el siguiente modo en la jerarquía: `ml` -> `rule_engine` -> `rule`.

---

## 2. `remote_learning`

Configura la capacidad de la instancia para enviar datos de aprendizaje a un servidor central.

-   **`enabled`**: Activa o desactiva el aprendizaje remoto.
    -   **Valores posibles**:
        -   `true`: La instancia intentará enviar resúmenes de conversaciones al servidor especificado.
        -   `false`: La instancia operará de forma completamente aislada.
-   **`server_url`**: La URL del endpoint del servidor central que recibe los datos de aprendizaje.

---

## 3. `swarm`

Controla el comportamiento relacionado con el enjambre de IAs y la replicación (Funcionalidad de Fase 3).

-   **`replication_enabled`**: Activa o desactiva la capacidad de la IA para crear réplicas de sí misma en la red.
    -   **Valores posibles**:
        -   `true`: Habilita el módulo de replicación. **(Experimental)**.
        -   `false`: Deshabilita la replicación.
-   **`scan_interval_seconds`**: Define la frecuencia (en segundos) con la que la instancia buscará otras instancias en la red para formar un enjambre.
    -   **Ejemplo**: `300` significa que escaneará la red cada 5 minutos.