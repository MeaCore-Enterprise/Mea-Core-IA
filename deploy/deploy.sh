#!/bin/bash

# Script para desplegar el servidor de Mea-Core-Enterprise

# Navegar al directorio de la aplicación si es necesario
# (En Docker, el WORKDIR ya está configurado, pero es buena práctica para ejecuciones manuales)
# cd /app

# Activar el entorno virtual si existe y no se está en Docker
# if [ -f ".venv/bin/activate" ]; then
#   source .venv/bin/activate
# fi

# Iniciar el servidor FastAPI con Uvicorn
# - host 0.0.0.0: Permite conexiones desde fuera del contenedor/máquina
# - port 8000: El puerto estándar para la API
# - server.main:app: La ubicación del objeto FastAPI (archivo server/main.py, objeto app)
echo "🚀 Iniciando servidor de Mea-Core-Enterprise en el puerto 8000..."
uvicorn server.main:app --host 0.0.0.0 --port 8000
