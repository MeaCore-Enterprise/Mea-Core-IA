# Fase 1: Build - Construir la aplicación de React
FROM node:18-alpine as build

WORKDIR /app

# Copiar package.json y package-lock.json primero para mejor cache
COPY package*.json ./

# Instalar dependencias con cache optimizado
RUN npm ci --only=production --silent

# Copiar el resto del código de la aplicación
COPY . .

# Construir la aplicación para producción con optimizaciones
RUN npm run build

# Fase 2: Production - Servir los archivos estáticos con Nginx
FROM nginx:1.25-alpine

# Instalar curl para health checks
RUN apk add --no-cache curl

# Copiar los archivos estáticos construidos desde la fase anterior
COPY --from=build /app/build /usr/share/nginx/html

# Crear configuración optimizada de Nginx
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Compresión gzip \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json; \
    \
    # Cache para archivos estáticos \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
    \
    # SPA routing \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Health check endpoint \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Exponer el puerto 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# El comando por defecto de Nginx ya se encarga de iniciar el servidor
CMD ["nginx", "-g", "daemon off;"]
