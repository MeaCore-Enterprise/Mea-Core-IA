#!/usr/bin/env python3
"""
Script de optimización de rendimiento para Mea-Core
"""

import os
import sys
import sqlite3
import psutil
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def optimize_database():
    """Optimiza las bases de datos SQLite"""
    logger.info("Optimizando bases de datos...")
    
    db_files = [
        "data/central_memory.db",
        "data/knowledge_base.db", 
        "data/mea_core_main.db",
        "data/mea_memory.db",
        "data/swarm_sync.db"
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Analizar y optimizar
                cursor.execute("ANALYZE")
                cursor.execute("VACUUM")
                
                # Configurar WAL mode para mejor concurrencia
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                
                conn.close()
                logger.info(f"Optimizada: {db_file}")
                
            except Exception as e:
                logger.error(f"Error optimizando {db_file}: {e}")

def clean_logs():
    """Limpia logs antiguos"""
    logger.info("Limpiando logs antiguos...")
    
    log_dirs = ["logs", "logs/security"]
    
    for log_dir in log_dirs:
        if os.path.exists(log_dir):
            for log_file in Path(log_dir).glob("*.log"):
                try:
                    # Eliminar logs más antiguos de 7 días
                    if log_file.stat().st_mtime < (psutil.boot_time() - 7*24*3600):
                        log_file.unlink()
                        logger.info(f"Eliminado: {log_file}")
                except Exception as e:
                    logger.error(f"Error eliminando {log_file}: {e}")

def optimize_memory():
    """Optimiza el uso de memoria"""
    logger.info("Optimizando configuración de memoria...")
    
    # Crear archivo de configuración de memoria
    memory_config = {
        "max_memory_usage": "2GB",
        "cache_size": "512MB",
        "garbage_collection_threshold": 0.7,
        "model_cache_size": 1000
    }
    
    config_path = Path("config/memory.json")
    config_path.parent.mkdir(exist_ok=True)
    
    import json
    with open(config_path, 'w') as f:
        json.dump(memory_config, f, indent=2)
    
    logger.info("Configuración de memoria actualizada")

def check_system_resources():
    """Verifica recursos del sistema"""
    logger.info("Verificando recursos del sistema...")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    logger.info(f"Uso de CPU: {cpu_percent}%")
    
    # Memoria
    memory = psutil.virtual_memory()
    logger.info(f"Memoria total: {memory.total / (1024**3):.1f} GB")
    logger.info(f"Memoria disponible: {memory.available / (1024**3):.1f} GB")
    logger.info(f"Uso de memoria: {memory.percent}%")
    
    # Disco
    disk = psutil.disk_usage('/')
    logger.info(f"Espacio en disco: {disk.free / (1024**3):.1f} GB libres de {disk.total / (1024**3):.1f} GB")
    
    # Recomendaciones
    if cpu_percent > 80:
        logger.warning("⚠️  Alto uso de CPU detectado")
    
    if memory.percent > 80:
        logger.warning("⚠️  Alto uso de memoria detectado")
    
    if disk.free / disk.total < 0.1:
        logger.warning("⚠️  Poco espacio en disco disponible")

def optimize_imports():
    """Optimiza imports en archivos Python"""
    logger.info("Optimizando imports...")
    
    python_files = list(Path(".").rglob("*.py"))
    
    for py_file in python_files:
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar imports duplicados o no utilizados
            lines = content.split('\n')
            imports = [line for line in lines if line.strip().startswith(('import ', 'from '))]
            
            if len(imports) != len(set(imports)):
                logger.info(f"Imports duplicados encontrados en: {py_file}")
                
        except Exception as e:
            logger.error(f"Error procesando {py_file}: {e}")

def main():
    """Función principal"""
    logger.info("🚀 Iniciando optimización de rendimiento de Mea-Core")
    
    try:
        check_system_resources()
        optimize_database()
        clean_logs()
        optimize_memory()
        optimize_imports()
        
        logger.info("✅ Optimización completada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante la optimización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()