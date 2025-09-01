# Changelog de Mea-Core Enterprise

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere al [Versionado Semántico](https://semver.org/spec/v2.0.0.html).

## [Sin Publicar]

### Añadido
- Estructura completa de organización de GitHub (workflows, templates, etc.).
- Módulos de seguridad y monetización para la Fase 8.
- Borradores de posts de blog para marketing inicial.

### Cambiado
- `core/security.py` ahora cifra los logs de auditoría.
- `core/memoria.py` ahora cifra y descifra los recuerdos al interactuar con la base de datos.

## [1.0.0] - 2025-08-31

### Añadido
- **Fase 5**: Módulo de Evolución Supervisada (`core/evolution.py`).
- **Fase 5**: Guardián Ético (`core/etica.py`) con log de auditoría.
- **Fase 5**: Configuración base para despliegue en Kubernetes (`deploy/k8s/`).
- **Fase 5**: Paneles de Auditoría y Ética en la WebApp.
- **Fase 5**: Pruebas para evolución, ética y escalabilidad.
- **Fase 4**: Módulos de Enjambre (`core/swarm.py`), Aprendizaje Federado (`core/federated.py`), Curiosidad (`core/curiosity.py`) y Objetivos (`core/goals.py`).
- **Fase 4**: Paneles de Enjambre, Aprendizaje y Objetivos en la WebApp.
- **Fase 4**: `docker-compose.yml` para despliegue de enjambre.
- **Fase 3**: Sistema de autenticación con JWT y roles.
- **Fase 3**: Soporte para base de datos PostgreSQL.
- **Fase 2**: Interfaz de WebApp con React y Material-UI.
- **Fase 2**: `Dockerfile` para contenerización.
- **Fase 1**: Núcleo inicial de la IA con memoria, conocimiento y cerebro básico.
