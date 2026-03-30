# Guía de Despliegue para Clientes de Mea-Core-Enterprise

**Versión:** 1.0 (Fase 3)

---

## 1. Introducción

Este documento proporciona las instrucciones técnicas para el despliegue y la configuración inicial de la plataforma Mea-Core-Enterprise en un servidor Linux. Está destinado a administradores de sistemas y personal de TI.

## 2. Requisitos del Servidor

-   **Sistema Operativo**: Distribución de Linux moderna (Ubuntu 20.04+, CentOS 7+, etc.).
-   **Hardware Mínimo**: 2 CPU, 4 GB RAM, 20 GB de almacenamiento.
-   **Software**: 
    -   `docker`: Versión 19.03 o superior.
    -   `docker-compose`: Versión 1.25 o superior.
    -   `git`: Para clonar el repositorio.

## 3. Proceso de Instalación Automatizada

Hemos proporcionado un script de instalación para simplificar el proceso. Este script verificará las dependencias, le guiará en la configuración inicial y levantará la aplicación.

1.  **Clonar el Repositorio**:
    ```bash
    git clone https://github.com/KronoxYT/Mea-Core.git
    cd Mea-Core
    ```

2.  **Ejecutar el Instalador**:
    Conceda permisos de ejecución al script y láncelo.
    ```bash
    chmod +x installer/install.sh
    ./installer/install.sh
    ```

3.  **Configuración del Entorno (`.env`)**:
    El script le pedirá que edite el archivo `.env` que se creará automáticamente. Es **crítico** que configure contraseñas seguras para la base de datos y una `SECRET_KEY` compleja para la API.

Una vez finalizado el script, la aplicación estará en ejecución y accesible en los puertos `3000` (frontend) y `8000` (backend).

## 4. Configuración de HTTPS para Producción

Por defecto, la aplicación se ejecuta sobre HTTP. Para un entorno de producción, es **obligatorio** configurar HTTPS. La forma recomendada de hacerlo es utilizando un **reverse proxy** como Nginx o Caddy, que gestionará los certificados SSL/TLS y redirigirá el tráfico de forma segura a nuestros contenedores.

### Ejemplo con Nginx y Let's Encrypt

1.  **Instalar Nginx y Certbot**:
    ```bash
    sudo apt update
    sudo apt install nginx python3-certbot-nginx
    ```

2.  **Obtener Certificado SSL**:
    Reemplace `sudominio.com` con su dominio real.
    ```bash
    sudo certbot --nginx -d sudominio.com
    ```
    Certbot configurará automáticamente Nginx y la renovación del certificado.

3.  **Configurar el Reverse Proxy**:
    Edite el archivo de configuración de su sitio en Nginx (ej: `/etc/nginx/sites-available/sudominio.com`):

    ```nginx
    server {
        server_name sudominio.com;

        location / {
            proxy_pass http://127.0.0.1:3000; # Apuntar al frontend
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api {
            proxy_pass http://127.0.0.1:8000/api; # Apuntar a la API
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        listen 443 ssl; # managed by Certbot
        ssl_certificate /etc/letsencrypt/live/sudominio.com/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/sudominio.com/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    ```

4.  **Reiniciar Nginx**:
    ```bash
    sudo systemctl restart nginx
    ```

## 5. Mantenimiento

-   **Actualizar la Aplicación**: Para obtener la última versión, navegue al directorio del proyecto y ejecute:
    ```bash
    git pull
    docker-compose -f deploy/compose.yml build
    docker-compose -f deploy/compose.yml up -d
    ```
-   **Backup de la Base de Datos**: El volumen de Docker `postgres_data` contiene todos los datos. Realice copias de seguridad de este volumen según las políticas de su organización.
