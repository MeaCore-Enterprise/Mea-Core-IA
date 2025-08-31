from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
import os

# --- Configuración de la Base de Datos ---

# Leer la configuración de la base de datos desde variables de entorno o un archivo .env
# Esto permite configurar una base de datos PostgreSQL en producción sin cambiar el código.
DB_USER = config('DB_USER', default=None)
DB_PASSWORD = config('DB_PASSWORD', default=None)
DB_HOST = config('DB_HOST', default=None)
DB_PORT = config('DB_PORT', default=None)
DB_NAME = config('DB_NAME', default=None)

# Si se proporcionan credenciales de PostgreSQL, se usan. Si no, se usa SQLite como fallback.
if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print("[Database] Usando PostgreSQL como base de datos.")
else:
    # Crear el directorio de datos si no existe para SQLite
    os.makedirs('data', exist_ok=True)
    SQLALCHEMY_DATABASE_URL = "sqlite:///data/mea_core_main.db"
    print("[Database] Usando SQLite como base de datos de fallback.")

# Crear el motor de SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # connect_args es específico para SQLite para permitir el uso en múltiples hilos (FastAPI)
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# Crear una clase SessionLocal, que será la fábrica de sesiones de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una clase Base que nuestras clases de modelo de ORM heredarán
Base = declarative_base()

# --- Dependencia para FastAPI ---

def get_db():
    """
    Dependencia de FastAPI que crea y gestiona una sesión de base de datos por cada request.
    Asegura que la sesión se cierre siempre, incluso si hay errores.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Función de Inicialización ---

def init_db():
    """
    Crea todas las tablas en la base de datos que heredan de la clase Base.
    Debe ser llamado una vez al iniciar la aplicación.
    """
    print("[Database] Inicializando la base de datos y creando tablas si no existen...")
    Base.metadata.create_all(bind=engine)
    print("[Database] Inicialización completada.")
