#!/bin/bash

# Installer for Mea-Core-Enterprise on Linux

set -e

# --- Functions ---

check_command() {
    if ! command -v $1 &> /dev/null;
    then
        echo -e "\e[31mError: El comando '$1' no fue encontrado. Por favor, instálalo y vuelve a intentarlo.\e[0m"
        exit 1
    fi
}

# --- Main Script ---

echo -e "\e[32m--- Instalador de Mea-Core-Enterprise ---\e[0m"

# 1. Verificar dependencias
echo "[1/4] Verificando dependencias (docker, docker-compose)..."
check_command docker
check_command docker-compose
echo "Dependencias encontradas."

# 2. Configuración del entorno
echo -e "\n[2/4] Configurando el entorno..."
if [ -f ".env" ]; then
    echo "El archivo '.env' ya existe. Omitiendo creación."
else
    echo "No se encontró el archivo '.env'. Creándolo desde '.env.example'..."
    if [ ! -f ".env.example" ]; then
        echo -e "\e[31mError: No se encontró el archivo '.env.example'. Asegúrate de que estás en el directorio raíz del proyecto.\e[0m"
        exit 1
    fi
    cp .env.example .env
    echo -e "\e[33m¡ACCIÓN REQUERIDA! Se ha creado el archivo '.env'. Por favor, edítalo ahora para establecer tus contraseñas y claves secretas.\e[0m"
    read -p "Presiona [Enter] cuando hayas terminado de editar el archivo .env..."
fi

# 3. Construir los contenedores
echo -e "\n[3/4] Construyendo las imágenes de Docker... Esto puede tardar varios minutos."
docker-compose -f deploy/compose.yml build
echo "Imágenes construidas con éxito."

# 4. Levantar los servicios
echo -e "\n[4/4] Iniciando los servicios de Mea-Core en segundo plano..."
docker-compose -f deploy/compose.yml up -d

echo -e "\n\e[32m--- ¡Instalación Completada!---\e[0m"
echo "Mea-Core-Enterprise se está ejecutando en segundo plano."
echo "- Puedes acceder a la interfaz web en: http://localhost:3000"
echo "- La documentación de la API está en: http://localhost:8000/docs"

echo -e "\nPara detener los servicios, ejecuta: docker-compose -f deploy/compose.yml down"
echo "Para ver los logs, ejecuta: docker-compose -f deploy/compose.yml logs -f"
