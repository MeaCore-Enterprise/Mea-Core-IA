# Web Corporativa de Mea-Core

Este directorio contiene el código fuente de la web corporativa de Mea-Core, construida con **Next.js** y **Tailwind CSS** para un rendimiento óptimo y un diseño moderno.

## Cómo Empezar

Para levantar el entorno de desarrollo local:

```bash
npm install
npm run dev
```

## Estructura de Directorios (Next.js)

- **/pages**: Contiene las rutas principales del sitio.
  - `index.tsx`: La landing page.
  - `use-cases.tsx`: La página que describe los casos de uso.
  - `pricing.tsx`: La página con los modelos de licenciamiento.
  - `contact.tsx`: El formulario de contacto para clientes.
  - `blog/`: Un blog para anuncios y artículos de marketing de contenidos.

- **/components**: Componentes de React reutilizables.
  - `Navbar.tsx`: La barra de navegación.
  - `Footer.tsx`: El pie de página.
  - `HeroSection.tsx`: La sección principal de la landing page.
  - `FeatureCard.tsx`: Tarjetas para mostrar las características del producto.

- **/public**: Archivos estáticos como imágenes, logos y fuentes.

- **/styles**: Estilos globales y configuración de Tailwind CSS.

## Despliegue

El sitio está diseñado para ser desplegado fácilmente en plataformas como **Vercel** o **Netlify** con integración continua desde el repositorio de GitHub.
