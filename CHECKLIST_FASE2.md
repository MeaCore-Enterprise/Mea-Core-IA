# Checklist Interno - Fase 2: Expansión Visible

Este documento rastrea el estado de avance de las tareas clave para la Fase 2.

## Tareas Principales

- [ ] **Branding:** Crear y aplicar la nueva identidad visual.
  - [ ] Crear logo en `branding/logo.svg`.
  - [ ] Aplicar logo al `README.md` principal.

- [ ] **Documentación:** Establecer la visión y el roadmap externo.
  - [ ] Crear `README_ENTERPRISE.md`.
  - [ ] Enlazar `README_ENTERPRISE.md` desde el `README.md` principal.

- [ ] **Infraestructura de Despliegue:** Preparar el proyecto para despliegue.
  - [ ] Crear `Dockerfile` funcional en la raíz.
  - [ ] Crear script `deploy/deploy.sh`.
  - [ ] Crear archivo de servicio `deploy/mea-core.service`.

- [ ] **Interfaz Web:** Desarrollar el frontend para interacción.
  - [ ] Conectar el chat de React al endpoint `/api/query` del backend.
  - [ ] Añadir sección "Estado del Sistema" (placeholder).
  - [ ] (Opcional) Integrar Tailwind CSS si es necesario para el diseño.

- [ ] **Verificación:** Probar la nueva infraestructura.
  - [ ] Construir la imagen de Docker y ejecutar un contenedor localmente.
  - [ ] Probar el script de despliegue en un entorno de pruebas Linux.
