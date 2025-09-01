# Dockerfile para Mea-Core

# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos e instalarlos
# Esto se cachea para acelerar builds futuros
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Exponer el puerto que usará la API de FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación
# Asume que el punto de entrada es `main.py` que inicia un servidor uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]