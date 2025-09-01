# Checklist de Verificación de Despliegue

Este checklist debe ser usado para verificar que todos los componentes de Mea-Core-Enterprise están listos y funcionando correctamente antes y después de un despliegue en producción.

--- 

### Pre-Despliegue (Local)

- [ ] **Frontend**: ¿El comando `npm run build` se ejecuta sin errores dentro de la carpeta `webapp/`?
- [ ] **Backend**: ¿La imagen de Docker se construye correctamente usando `docker build -f Dockerfile.backend .`?
- [ ] **Pruebas**: ¿Todos los tests (`pytest`) pasan correctamente?
- [ ] **Linting**: ¿El código pasa el linter (`flake8`) sin errores críticos?
- [ ] **Variables de Entorno**: ¿Se ha creado el archivo `.env` a partir de `.env.example` y se han configurado las claves para el desarrollo local?

--- 

### Post-Despliegue (Producción)

- [ ] **Backend (Render/Railway)**:
    - [ ] ¿El servicio se ha desplegado correctamente y muestra el estado "Live" o "Healthy"?
    - [ ] ¿Se puede acceder a la URL pública del backend (ej. `https://mea-core-backend.onrender.com`) y ver el mensaje `{"message":"Mea-Core Enterprise API corriendo 🚀"}`?
    - [ ] ¿Las variables de entorno (`SECRET_KEY`, etc.) están configuradas en el dashboard del proveedor?

- [ ] **Frontend (Vercel)**:
    - [ ] ¿El despliegue se ha completado sin errores de construcción?
    - [ ] ¿Se puede acceder a la URL pública del frontend?
    - [ ] ¿La variable de entorno `REACT_APP_API_URL` está apuntando a la URL del backend de producción?

- [ ] **Integración y Funcionalidad**:
    - [ ] ¿Se puede registrar un nuevo usuario desde la interfaz web?
    - [ ] ¿Se puede iniciar sesión con un usuario existente?
    - [ ] ¿Se pueden enviar mensajes al chat y recibir respuestas de la IA?
    - [ ] (Revisar la consola del navegador) ¿Hay algún error de CORS o de red (404, 500) al comunicarse con la API?

--- 

### Verificación de Seguridad

- [ ] ¿El sitio del frontend carga sobre HTTPS?
- [ ] ¿El endpoint de la API carga sobre HTTPS?
- [ ] ¿Las contraseñas de la base de datos y las claves secretas **NO** están hardcodeadas en el código, sino que se gestionan como variables de entorno?
