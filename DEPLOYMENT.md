# 🚀 Guía de Despliegue - Mea-Core

Esta guía te ayudará a desplegar Mea-Core de manera optimizada y escalable.

## 📋 Prerrequisitos

- Docker y Docker Compose
- Python 3.10+
- Node.js 18+
- Git

## 🏗️ Opciones de Despliegue

### 1. Despliegue Local con Docker Compose

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd mea-core

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Desplegar
./scripts/deploy.sh deploy
```

### 2. Despliegue en Vercel (Frontend)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Desplegar desde la carpeta webapp
cd webapp
vercel --prod
```

### 3. Despliegue en Render/Railway (Backend)

```bash
# Conectar tu repositorio a Render/Railway
# Configurar las variables de entorno
# El despliegue se hará automáticamente
```

## 🔧 Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y configura:

```env
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/mea_core

# Seguridad
SECRET_KEY=tu-clave-secreta-muy-segura
JWT_SECRET_KEY=tu-clave-jwt-secreta

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Frontend
REACT_APP_API_URL=https://tu-api.com
```

### Configuración de Base de Datos

```sql
-- Crear base de datos
CREATE DATABASE mea_core;
CREATE USER mea_user WITH PASSWORD 'mea_password';
GRANT ALL PRIVILEGES ON DATABASE mea_core TO mea_user;
```

## 📊 Monitoreo

### Métricas Disponibles

- **Backend**: `http://localhost:8000/api/metrics`
- **Health Check**: `http://localhost:8000/api/health`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3001`

### Comandos de Monitoreo

```bash
# Ver logs en tiempo real
./scripts/deploy.sh logs

# Verificar salud del sistema
./scripts/deploy.sh health

# Optimizar rendimiento
./scripts/deploy.sh optimize
```

## 🚀 Optimizaciones Implementadas

### Backend
- ✅ Multi-stage Docker builds
- ✅ Usuario no-root para seguridad
- ✅ Health checks
- ✅ Monitoreo de rendimiento
- ✅ Cache de dependencias
- ✅ Workers múltiples

### Frontend
- ✅ Build optimizado con Nginx
- ✅ Compresión gzip
- ✅ Cache de archivos estáticos
- ✅ SPA routing
- ✅ Health checks

### Base de Datos
- ✅ Configuración WAL mode
- ✅ Optimización de cache
- ✅ Vacuum automático
- ✅ Índices optimizados

### CI/CD
- ✅ GitHub Actions optimizado
- ✅ Cache de dependencias
- ✅ Tests paralelos
- ✅ Build multi-plataforma
- ✅ Deploy automático

## 🔍 Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**
   ```bash
   # Verificar que PostgreSQL esté corriendo
   docker-compose ps
   ```

2. **Frontend no carga**
   ```bash
   # Verificar logs del frontend
   docker-compose logs frontend
   ```

3. **Alto uso de memoria**
   ```bash
   # Ejecutar optimización
   ./scripts/deploy.sh optimize
   ```

### Logs y Debugging

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Acceder al contenedor
docker-compose exec backend bash
```

## 📈 Escalabilidad

### Horizontal Scaling

```yaml
# docker-compose.override.yml
services:
  backend:
    deploy:
      replicas: 3
  frontend:
    deploy:
      replicas: 2
```

### Load Balancing

El nginx configurado actúa como load balancer automáticamente.

## 🔒 Seguridad

### Implementado
- ✅ HTTPS con certificados SSL
- ✅ Headers de seguridad
- ✅ Rate limiting
- ✅ Autenticación JWT
- ✅ Usuario no-root en contenedores
- ✅ Variables de entorno seguras

### Recomendaciones Adicionales
- Configurar firewall
- Usar secrets management
- Implementar WAF
- Monitoreo de seguridad

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `./scripts/deploy.sh logs`
2. Verifica la salud: `./scripts/deploy.sh health`
3. Consulta la documentación
4. Abre un issue en GitHub

## 🎯 Próximos Pasos

1. **Configurar dominio personalizado**
2. **Implementar SSL/TLS**
3. **Configurar backup automático**
4. **Implementar alertas**
5. **Optimizar para producción**

---

¡Tu aplicación Mea-Core está lista para producción! 🎉