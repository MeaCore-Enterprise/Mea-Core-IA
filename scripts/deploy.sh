#!/bin/bash

# Script de despliegue para Mea-Core
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose no está instalado"
        exit 1
    fi
    
    success "Dependencias verificadas"
}

# Optimizar rendimiento
optimize_performance() {
    log "Ejecutando optimizaciones de rendimiento..."
    
    if [ -f "scripts/optimize_performance.py" ]; then
        python3 scripts/optimize_performance.py
        success "Optimizaciones completadas"
    else
        warning "Script de optimización no encontrado"
    fi
}

# Construir imágenes Docker
build_images() {
    log "Construyendo imágenes Docker..."
    
    # Construir backend
    log "Construyendo imagen del backend..."
    docker build -t mea-core-backend:latest .
    
    # Construir frontend
    log "Construyendo imagen del frontend..."
    docker build -t mea-core-frontend:latest ./webapp
    
    success "Imágenes construidas exitosamente"
}

# Ejecutar tests
run_tests() {
    log "Ejecutando tests..."
    
    # Tests del backend
    if [ -f "requirements.txt" ]; then
        log "Ejecutando tests del backend..."
        python3 -m pytest tests/ -v --tb=short
    fi
    
    # Tests del frontend
    if [ -d "webapp" ]; then
        log "Ejecutando tests del frontend..."
        cd webapp
        npm test -- --coverage --watchAll=false
        cd ..
    fi
    
    success "Tests completados"
}

# Desplegar con Docker Compose
deploy() {
    log "Desplegando aplicación..."
    
    # Detener contenedores existentes
    log "Deteniendo contenedores existentes..."
    docker-compose down --remove-orphans
    
    # Construir y levantar servicios
    log "Levantando servicios..."
    docker-compose up -d --build
    
    # Esperar a que los servicios estén listos
    log "Esperando a que los servicios estén listos..."
    sleep 30
    
    # Verificar salud de los servicios
    check_health
}

# Verificar salud de los servicios
check_health() {
    log "Verificando salud de los servicios..."
    
    # Backend
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        success "Backend está funcionando"
    else
        error "Backend no está respondiendo"
        return 1
    fi
    
    # Frontend
    if curl -f http://localhost:3000/ > /dev/null 2>&1; then
        success "Frontend está funcionando"
    else
        error "Frontend no está respondiendo"
        return 1
    fi
    
    # Base de datos
    if docker-compose exec -T db pg_isready -U mea_user -d mea_core > /dev/null 2>&1; then
        success "Base de datos está funcionando"
    else
        error "Base de datos no está respondiendo"
        return 1
    fi
}

# Mostrar logs
show_logs() {
    log "Mostrando logs de los servicios..."
    docker-compose logs --tail=50
}

# Limpiar recursos
cleanup() {
    log "Limpiando recursos..."
    
    # Detener y eliminar contenedores
    docker-compose down --remove-orphans
    
    # Eliminar imágenes no utilizadas
    docker image prune -f
    
    # Eliminar volúmenes no utilizados
    docker volume prune -f
    
    success "Limpieza completada"
}

# Función principal
main() {
    log "🚀 Iniciando despliegue de Mea-Core"
    
    case "${1:-deploy}" in
        "check")
            check_dependencies
            ;;
        "optimize")
            optimize_performance
            ;;
        "build")
            check_dependencies
            build_images
            ;;
        "test")
            run_tests
            ;;
        "deploy")
            check_dependencies
            optimize_performance
            build_images
            run_tests
            deploy
            ;;
        "health")
            check_health
            ;;
        "logs")
            show_logs
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "Uso: $0 {check|optimize|build|test|deploy|health|logs|cleanup}"
            echo ""
            echo "Comandos:"
            echo "  check     - Verificar dependencias"
            echo "  optimize  - Optimizar rendimiento"
            echo "  build     - Construir imágenes Docker"
            echo "  test      - Ejecutar tests"
            echo "  deploy    - Desplegar aplicación completa (por defecto)"
            echo "  health    - Verificar salud de los servicios"
            echo "  logs      - Mostrar logs"
            echo "  cleanup   - Limpiar recursos"
            exit 1
            ;;
    esac
    
    success "✅ Operación completada exitosamente"
}

# Ejecutar función principal
main "$@"