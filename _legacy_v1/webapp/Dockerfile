# Fase 1: Build - Construir la aplicación de React
FROM node:18-alpine as build

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código de la aplicación
COPY . .

# Construir la aplicación para producción
RUN npm run build

# Fase 2: Production - Servir los archivos estáticos con Nginx
FROM nginx:1.25-alpine

# Copiar los archivos estáticos construidos desde la fase anterior
COPY --from=build /app/build /usr/share/nginx/html

# Copiar una configuración personalizada de Nginx si es necesario (opcional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer el puerto 80
EXPOSE 80

# El comando por defecto de Nginx ya se encarga de iniciar el servidor
CMD ["nginx", "-g", "daemon off;"]
