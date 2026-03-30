# Guía de Despliegue: Mea-Core Enterprise

Esta guía detalla los pasos para desplegar el frontend en Vercel y el backend en Render.

## 1. Despliegue del Backend (Render)

El backend utiliza el archivo `deploy/render.yaml` para una configuración automática "Blueprint".

1.  **Crear Cuenta en Render:**
    *   Regístrate o inicia sesión en [render.com](https://render.com).

2.  **Crear un Nuevo Blueprint:**
    *   En el dashboard, haz clic en **New -> Blueprint**.
    *   Conecta tu repositorio de GitHub donde se encuentra Mea-Core.
    *   Render detectará automáticamente el archivo `render.yaml` en la raíz del proyecto. Dale un nombre al grupo de servicios (ej: `mea-core-backend`).

3.  **Configuración y Despliegue:**
    *   Render leerá `render.yaml` y configurará el servicio web usando `Dockerfile.backend`.
    *   Aprueba el plan. El primer despliegue comenzará automáticamente y puede tardar varios minutos.

4.  **Obtener la URL del Backend:**
    *   Una vez desplegado, Render asignará una URL pública a tu servicio (ej: `https://mea-core-backend.onrender.com`).
    *   Copia esta URL. La necesitarás para configurar el frontend.

## 2. Despliegue del Frontend (Vercel)

El frontend es una aplicación React que se despliega en Vercel.

1.  **Crear Cuenta en Vercel:**
    *   Regístrate o inicia sesión en [vercel.com](https://vercel.com).

2.  **Importar Proyecto:**
    *   Desde el dashboard, haz clic en **Add New -> Project**.
    *   Importa el repositorio de GitHub de Mea-Core.
    *   Vercel detectará la configuración en el archivo `vercel.json` que hemos creado.

3.  **Configurar Variables de Entorno:**
    *   En la configuración del proyecto, ve a **Settings -> Environment Variables**.
    *   Añade la siguiente variable:
        *   **Key:** `REACT_APP_API_URL`
        *   **Value:** La URL del backend que obtuviste de Render (ej: `https://mea-core-backend.onrender.com`).

4.  **Desplegar:**
    *   Haz clic en **Deploy**. Vercel construirá y desplegará la aplicación.
    *   La URL de acceso principal será del tipo `<project-name>.vercel.app`.

## 3. Optimización y Extras (Vercel)

Una vez desplegado el proyecto, puedes activar funcionalidades adicionales desde el dashboard de Vercel:

*   **Preview Deployments:**
    *   Esta función está activada por defecto. Cada `pull request` a tu repositorio generará una URL de previsualización aislada y automática.

*   **Speed Insights:**
    *   Ve a la pestaña **Analytics** o **Speed Insights** en tu proyecto de Vercel.
    *   Activa el servicio (puede tener un coste asociado o una capa gratuita).
    *   Desde aquí podrás monitorear el rendimiento de tu aplicación (Core Web Vitals) y obtener recomendaciones de mejora.

*   **Dominios Personalizados:**
    *   Sigue las instrucciones en `docs/DOMAIN_SETUP.md` para añadir y configurar tu propio dominio.