# Guía de Despliegue Profesional: Frontend y Backend

Este documento explica cómo desplegar el frontend y el backend de Mea-Core-Enterprise en servicios modernos como Vercel y Render.

---

## 1. Despliegue del Backend (FastAPI)

Recomendamos usar **Render** para el backend por su facilidad para desplegar servicios en Docker y gestionar bases de datos.

**Pasos en Render:**

1.  **Crear una Cuenta**: Regístrate en [Render.com](https://render.com/).
2.  **Nuevo Servicio Web**: En tu dashboard, haz clic en "New" > "Web Service".
3.  **Conectar Repositorio**: Conecta tu repositorio de GitHub (`Mea-Core-IA`).
4.  **Configuración del Servicio**:
    -   **Name**: `mea-core-backend` (o el que prefieras).
    -   **Environment**: `Docker`.
    -   **DockerfilePath**: `./Dockerfile.backend` (asegúrate de que apunte al Dockerfile que creamos).
    -   **Plan**: Elige un plan (el plan gratuito puede ser suficiente para empezar).
5.  **Variables de Entorno**: Render te permite añadir variables de entorno seguras. El archivo `render.yaml` que hemos creado le sugiere a Render que genere valores seguros automáticamente para `SECRET_KEY` y `MEA_ENCRYPTION_KEY`.
6.  **Desplegar**: Haz clic en "Create Web Service". Render construirá la imagen y desplegará tu API.
7.  **Obtener la URL**: Una vez desplegado, Render te dará una URL pública, como `https://mea-core-backend.onrender.com`. **Copia esta URL.**

---

## 2. Despliegue del Frontend (React)

Recomendamos **Vercel** para el frontend por su integración perfecta con frameworks de JavaScript como React.

**Pasos en Vercel:**

1.  **Crear una Cuenta**: Regístrate en [Vercel.com](https://vercel.com/).
2.  **Nuevo Proyecto**: En tu dashboard, haz clic en "Add New..." > "Project".
3.  **Importar Repositorio**: Importa tu repositorio de GitHub (`Mea-Core-IA`).
4.  **Configuración del Proyecto**:
    -   **Framework Preset**: Vercel debería detectar `Create React App`.
    -   **Root Directory**: **MUY IMPORTANTE**. Haz clic en "Edit" y selecciona la carpeta `webapp`.
5.  **Variables de Entorno**: Aquí es donde conectas el frontend con el backend.
    -   **KEY**: `REACT_APP_API_URL`
    -   **VALUE**: Pega la URL de tu backend que copiaste de Render (ej. `https://mea-core-backend.onrender.com`).
6.  **Desplegar**: Haz clic en "Deploy". Vercel construirá y desplegará tu aplicación de React.

---

## 3. Verificación Final

Una vez que ambos servicios estén desplegados, abre la URL de tu frontend (la de Vercel). La aplicación web debería cargar y ser capaz de comunicarse con la API en Render para iniciar sesión y realizar consultas a la IA.

¡Felicidades! Tienes un despliegue profesional, seguro y escalable de Mea-Core-Enterprise.
