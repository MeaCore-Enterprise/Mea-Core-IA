# Despliegue de la Demo Pública Lite

Este documento contiene las instrucciones para desplegar una versión ligera y limitada de Mea-Core en plataformas de hosting modernas como Vercel, Railway o Replit.

## Requisitos

- Una cuenta en la plataforma de despliegue elegida (Vercel, Railway, etc.).
- El código fuente de Mea-Core en un repositorio de GitHub.

## Archivo Clave: `Dockerfile.lite`

Se ha creado un `Dockerfile.lite` específico para esta demo. Este Dockerfile se diferencia del principal en varios aspectos:

- **Instala menos dependencias**: Solo instala `fastapi`, `uvicorn` y lo esencial, omitiendo librerías pesadas de Machine Learning como `torch` o `transformers`.
- **Copia menos código**: Solo incluye los módulos necesarios para una API de consulta simple, excluyendo el enjambre, la evolución, el aprendizaje federado, etc.
- **Resultado**: Una imagen de Docker mucho más pequeña y rápida, ideal para un entorno de servidor sin GPU y con recursos limitados.

## Instrucciones de Despliegue (Ejemplo con Railway)

1.  **Inicia sesión en Railway:** Ve a [railway.app](https://railway.app/) y crea un nuevo proyecto.
2.  **Conecta tu Repositorio:** Autoriza a Railway para que acceda a tu repositorio de GitHub donde se encuentra Mea-Core.
3.  **Configura el Servicio:**
    - Railway detectará el `Dockerfile` principal. Debes cambiar la configuración para que use el `Dockerfile.lite`.
    - En la configuración del servicio, ve a la pestaña "Settings" y en la sección "Build", especifica la ruta al Dockerfile: `./Dockerfile.lite`.
4.  **Variables de Entorno:**
    - Añade las variables de entorno necesarias para la configuración de Mea-Core, como `SECRET_KEY`.
    - Es posible que necesites una variable como `MEA_MODE=LITE` para que la aplicación sepa que debe arrancar en modo limitado.
5.  **Desplegar:**
    - Guarda la configuración. Railway automáticamente construirá la imagen a partir de `Dockerfile.lite` y desplegará el servicio.
    - Una vez desplegado, Railway te proporcionará una URL pública (ej: `mea-core-demo.up.railway.app`) donde la API estará disponible.

## Limitaciones de la Demo

Esta versión Lite está diseñada para mostrar la capacidad de respuesta de la API y la interacción con una base de conocimiento estática. **No incluye**:

- Inteligencia de enjambre.
- Aprendizaje federado o local.
- Objetivos autónomos o curiosidad.
- Evolución supervisada.
- Paneles de control empresariales.

Es una herramienta de marketing para que los potenciales clientes puedan interactuar con la velocidad y la interfaz básica del sistema.
