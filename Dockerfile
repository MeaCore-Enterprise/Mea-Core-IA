# Fase 1: Build
# Usar una imagen de Python oficial
FROM python:3.10-slim as builder

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias de build si fueran necesarias en el futuro
# RUN pip install --upgrade pip

# Copiar el archivo de requerimientos e instalar dependencias
# Esto se hace en un paso separado para aprovechar el cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Fase 2: Producción
FROM python:3.10-slim

WORKDIR /app

# Copiar las dependencias instaladas desde la fase de build
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copiar todo el código de la aplicación
COPY . .

# Asegurarse de que los scripts de despliegue sean ejecutables
RUN chmod +x /app/deploy/deploy.sh

# Comando por defecto para ejecutar la aplicación (CLI)
# Para ejecutar el servidor, se puede sobreescribir con: docker run -p 8000:8000 <imagen> deploy/deploy.sh
CMD ["python3", "main.py"]
