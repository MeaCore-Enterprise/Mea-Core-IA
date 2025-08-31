# Checklist Interno - Fase 3: Escalamiento y Distribución

Seguimiento de tareas para la conversión de Mea-Core en un producto empresarial escalable y distribuible.

## 1. Backend y Seguridad
- [ ] **Base de Datos:** Migrar de SQLite a PostgreSQL.
  - [ ] Abstraer la conexión a la base de datos para soportar tanto PostgreSQL como SQLite.
  - [ ] Actualizar `core/memoria.py` y `core/conocimiento.py` para usar la nueva capa de abstracción.
- [ ] **Autenticación:** Implementar sistema de usuarios y JWT.
  - [ ] Crear modelos de Usuario y Rol en la base de datos.
  - [ ] Implementar endpoints `/login` y `/register`.
  - [ ] Proteger endpoints de la API con dependencias de seguridad JWT.
  - [ ] Añadir pruebas unitarias para el sistema de autenticación.
- [ ] **HTTPS:** Configurar certificados para desarrollo seguro.
  - [ ] Generar certificados autofirmados.
  - [ ] Documentar el uso de certificados reales (Let's Encrypt).

## 2. DevOps e Infraestructura
- [ ] **Docker Compose:** Orquestar todos los servicios.
  - [ ] Crear `deploy/compose.yml`.
  - [ ] Configurar servicio `db` (PostgreSQL) con volumen persistente.
  - [ ] Configurar servicio `api` (FastAPI).
  - [ ] Configurar servicio `frontend` (React).
- [ ] **Verificación:** Probar el despliegue completo.
  - [ ] Levantar la pila completa con `docker-compose up`.
  - [ ] Validar la comunicación entre servicios (frontend -> api -> db).

## 3. Distribución y Documentación de Cliente
- [ ] **Instaladores:** Crear scripts para facilitar la instalación.
  - [ ] Crear `installer/install.sh` para Linux.
  - [ ] Crear guía o script `installer/install.bat` para Windows.
- [ ] **Documentación de Despliegue:** Crear guía para clientes.
  - [ ] Redactar `docs/DEPLOY_CLIENTE.md`.

## 4. Branding y Producto
- [ ] **Activos de Marca:** Actualizar la carpeta `branding/`.
  - [ ] Generar versión PNG del logo.
  - [ ] Crear plantilla de presentación corporativa en Markdown.
- [ ] **Marketing:** Crear mockups de documentos de producto.
  - [ ] Redactar `docs/LANDING_PAGE.md`.
  - [ ] Redactar `docs/PRICING_MODEL.md`.
