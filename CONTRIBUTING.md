# Guía de Contribución para Mea-Core Enterprise

Primero, gracias por considerar contribuir a Mea-Core. Aunque este es un proyecto de código cerrado a nivel de licencia, operamos con los más altos estándares de desarrollo de software y valoramos las contribuciones de nuestro equipo interno y socios autorizados.

## Proceso de Desarrollo

Nuestro proceso de desarrollo sigue un flujo de trabajo basado en GitFlow:

-   `main`: Esta rama contiene el código de producción estable. Solo se fusiona desde `develop` durante un ciclo de release.
-   `develop`: Esta es la rama principal de desarrollo. Todas las nuevas características y correcciones se integran aquí.
-   `feature/<nombre-feature>`: Las nuevas características se desarrollan en estas ramas, partiendo de `develop`.
-   `bugfix/<nombre-bug>`: Las correcciones de bugs se desarrollan en estas ramas.

### Flujo de Pull Request

1.  **Crear un Issue**: Antes de empezar a trabajar, asegúrate de que haya un issue en GitHub que describa la característica o el bug. Asignátelo a ti mismo.
2.  **Crear una Rama**: Crea una nueva rama desde `develop` con un nombre descriptivo (ej. `feature/gestion-usuarios-premium`).
3.  **Desarrollar y Testear**: Escribe tu código. Es **obligatorio** añadir o actualizar las pruebas unitarias (`pytest`) para cubrir tus cambios.
4.  **Linting**: Asegúrate de que tu código pasa el linter sin errores (`flake8 .`).
5.  **Crear un Pull Request (PR)**: Cuando tu trabajo esté listo, abre un PR contra la rama `develop`. Utiliza la plantilla de PR para describir tus cambios.
6.  **Revisión de Código**: Al menos dos miembros del equipo deben revisar y aprobar el PR. El workflow de Auto-Assign sugerirá revisores.
7.  **Merge**: Una vez aprobado y con los checks de CI en verde, el PR será fusionado en `develop`.

## Guía de Estilo de Código

-   **Python**: Seguimos el estándar [PEP 8](https://www.python.org/dev/peps/pep-0008/). Usamos `flake8` para la validación automática.
-   **TypeScript/React**: Usamos la configuración por defecto de `create-react-app` con `eslint`.
-   **Docstrings**: Todas las funciones y clases públicas deben tener docstrings que expliquen su propósito, argumentos y lo que devuelven.

## Reportando Bugs

Utiliza la plantilla de "Reporte de Bug" en los issues de GitHub. Proporciona la mayor cantidad de detalles posible para que podamos reproducir y solucionar el problema rápidamente.

## Sugiriendo Mejoras

Utiliza la plantilla de "Solicitud de Característica" para proponer nuevas ideas. Explica claramente el problema que resuelve y la solución que propones.