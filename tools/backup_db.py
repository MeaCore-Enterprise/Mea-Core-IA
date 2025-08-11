
import sqlite3
import os
import shutil
import time

# Rutas a las bases de datos originales
DB_PATHS = {
    "memory": "data/mea_memory.db",
    "knowledge": "data/knowledge_base.db"
}

# Directorio donde se guardarán los backups
BACKUP_DIR = "data/backups"

def backup_database(db_name: str, db_path: str):
    """Crea una copia de seguridad de un archivo de base de datos."""
    if not os.path.exists(db_path):
        print(f"[Advertencia] No se encontró la base de datos '{db_name}' en '{db_path}'. No se hará backup.")
        return

    # Crear el nombre del archivo de backup con timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{db_name}_backup_{timestamp}.db"
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)

    try:
        # Copiar el archivo de la base de datos
        shutil.copy2(db_path, backup_filepath)
        print(f"[Éxito] Backup de la base de datos '{db_name}' creado en: {backup_filepath}")
    except Exception as e:
        print(f"[Error] No se pudo crear el backup para '{db_name}': {e}")

def main():
    """Función principal para ejecutar el proceso de backup."""
    print("Iniciando proceso de backup de bases de datos...")
    
    # Asegurarse de que el directorio de backups exista
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    for name, path in DB_PATHS.items():
        backup_database(name, path)
        
    print("Proceso de backup finalizado.")

if __name__ == "__main__":
    main()
