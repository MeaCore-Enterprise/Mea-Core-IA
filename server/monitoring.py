"""
Módulo de monitoreo de rendimiento para Mea-Core
"""

import time
import psutil
import logging
from functools import wraps
from typing import Dict, Any, Callable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor de rendimiento del sistema"""
    
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "total_response_time": 0,
            "avg_response_time": 0,
            "memory_usage": 0,
            "cpu_usage": 0,
            "active_connections": 0
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del sistema"""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            "memory_usage_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "cpu_usage_percent": cpu_percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "active_processes": len(psutil.pids())
        }
    
    def update_request_metrics(self, response_time: float):
        """Actualiza métricas de requests"""
        self.metrics["request_count"] += 1
        self.metrics["total_response_time"] += response_time
        self.metrics["avg_response_time"] = (
            self.metrics["total_response_time"] / self.metrics["request_count"]
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna todas las métricas"""
        system_metrics = self.get_system_metrics()
        return {**self.metrics, **system_metrics}

# Instancia global del monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(func: Callable) -> Callable:
    """Decorator para monitorear el rendimiento de funciones"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            execution_time = time.time() - start_time
            performance_monitor.update_request_metrics(execution_time)
            logger.info(f"Function {func.__name__} executed in {execution_time:.4f}s")
    return wrapper

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware para monitorear requests HTTP"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Procesar request
        response = await call_next(request)
        
        # Calcular tiempo de respuesta
        process_time = time.time() - start_time
        
        # Actualizar métricas
        performance_monitor.update_request_metrics(process_time)
        
        # Agregar headers de performance
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = str(int(time.time() * 1000))
        
        # Log de performance
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.4f}s"
        )
        
        return response

def get_performance_metrics() -> Dict[str, Any]:
    """Endpoint para obtener métricas de rendimiento"""
    return performance_monitor.get_metrics()

def check_system_health() -> Dict[str, Any]:
    """Verifica la salud del sistema"""
    metrics = performance_monitor.get_system_metrics()
    
    health_status = "healthy"
    warnings = []
    
    # Verificar memoria
    if metrics["memory_usage_percent"] > 80:
        health_status = "warning"
        warnings.append("High memory usage")
    
    # Verificar CPU
    if metrics["cpu_usage_percent"] > 80:
        health_status = "warning"
        warnings.append("High CPU usage")
    
    # Verificar disco
    if metrics["disk_usage_percent"] > 90:
        health_status = "critical"
        warnings.append("Low disk space")
    
    return {
        "status": health_status,
        "metrics": metrics,
        "warnings": warnings,
        "timestamp": time.time()
    }