# Guía de Instalación de Mea-Core-Enterprise en Windows

Esta guía detalla los pasos para instalar y ejecutar Mea-Core-Enterprise en un entorno Windows utilizando Docker Desktop.

---

## Prerrequisitos

1.  **Docker Desktop**: Debes tener Docker Desktop para Windows instalado y en ejecución. Docker Desktop gestiona tanto Docker como Docker Compose.
    -   Puedes descargarlo desde el [sitio oficial de Docker](https://www.docker.com/products/docker-desktop/).
2.  **Git**: Necesitas Git para clonar el repositorio.
    -   Puedes descargarlo desde [git-scm.com](https://git-scm.com/download/win).

---

## Pasos de Instalación

### 1. Abrir una Terminal

Abre tu terminal preferida en Windows (PowerShell, Windows Terminal o Git Bash).

### 2. Clonar el Repositorio

Navega al directorio donde quieras instalar Mea-Core y clona el proyecto:

```sh
git clone https://github.com/KronoxYT/Mea-Core.git
cd Mea-Core
```

### 3. Configurar el Entorno

El proyecto utiliza un archivo `.env` para gestionar las contraseñas y claves secretas. Debes crearlo a partir del ejemplo proporcionado.

1.  Copia el archivo de ejemplo:
    ```sh
    copy .env.example .env
    ```
2.  Abre el nuevo archivo `.env` con un editor de texto (como Notepad o VS Code):
    ```sh
    notepad .env
    ```
3.  **Edita los valores**, especialmente `DB_PASSWORD` y `SECRET_KEY`, con valores seguros y complejos.
4.  Guarda y cierra el archivo.

### 4. Construir y Levantar los Servicios

Una vez que Docker Desktop esté en ejecución y hayas configurado tu archivo `.env`, puedes levantar toda la aplicación con un solo comando. Este comando utiliza el archivo de configuración de Docker Compose que hemos preparado.

```sh
docker-compose -f deploy/compose.yml up --build -d
```

-   `--build`: Fuerza la reconstrucción de las imágenes si ha habido cambios.
-   `-d`: Ejecuta los contenedores en segundo plano (detached mode).

El primer inicio puede tardar varios minutos mientras Docker descarga las imágenes base y construye los contenedores.

---

## Verificación

Una vez que el comando anterior haya terminado, la aplicación estará en ejecución.

-   **Interfaz Web**: Abre tu navegador y ve a `http://localhost:3000`.
-   **Documentación de la API**: Puedes acceder a la documentación interactiva en `http://localhost:8000/docs`.

## Gestión de los Servicios

-   **Para detener la aplicación**:
    ```sh
    docker-compose -f deploy/compose.yml down
    ```
-   **Para ver los logs en tiempo real**:
    ```sh
    docker-compose -f deploy/compose.yml logs -f
    ```
