import sys
import os
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Importaciones del Núcleo y de la App ---
from core import models, schemas, security
from core.database import SessionLocal, engine, get_db
from core.gestor_configuracion import SettingsManager
from core.memoria import MemoryStore
from core.conocimiento import KnowledgeManager
from core.etica import EthicsCore
from core.cerebro import Brain
from server.monitoring import PerformanceMiddleware, get_performance_metrics, check_system_health

# --- Inicialización de la Base de Datos y Componentes ---

# 1. Crear modelos en la DB
models.Base.metadata.create_all(bind=engine)

# 2. Instanciar componentes de la aplicación
settings_manager = SettingsManager()
memory_store = MemoryStore()
# El KnowledgeManager ahora necesita una sesión para construir su índice inicial
db_for_init = SessionLocal()
knowledge_manager = KnowledgeManager(db_session=db_for_init)
db_for_init.close()
ethics_core = EthicsCore()

brain = Brain(
    settings=settings_manager.settings,
    responses=settings_manager.get_responses(),
    memory=memory_store,
    knowledge=knowledge_manager,
    ethics=ethics_core
)

# --- App y Routers ---
app = FastAPI(title="Mea-Core Enterprise API")

# --- Configuración de CORS ---
origins = [
    "http://localhost:3000",  # Para desarrollo local de React
    "https://app.mea-core.com", # URL de producción del frontend (ejemplo)
    # Añadir aquí la URL que te de Vercel si es diferente
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Agregar middleware de monitoreo de rendimiento
app.add_middleware(PerformanceMiddleware)

api_router = APIRouter(prefix="/api")
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- Funciones de Ayuda y Dependencias ---

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate, role_name: str = 'cliente'):
    role = db.query(models.Role).filter(models.Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=500, detail=f"El rol '{role_name}' no existe.")
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password, role_id=role.id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def upsert_admin_user(db: Session, username: str, password: str, email: str) -> models.User:
    """Crea o actualiza el usuario admin con credenciales seguras."""
    admin_role = db.query(models.Role).filter(models.Role.name == 'admin').first()
    if not admin_role:
        # En caso extremo que aún no exista, lo creamos aquí
        admin_role = models.Role(name='admin')
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    user = db.query(models.User).filter(models.User.username == username).first()
    hashed_password = security.get_password_hash(password)
    if user:
        user.email = email
        user.hashed_password = hashed_password
        user.role_id = admin_role.id
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    new_user = models.User(username=username, email=email, hashed_password=hashed_password, role_id=admin_role.id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def ensure_admin_seed(db: Session):
    """Garantiza que exista un admin y permite reset controlado por variables de entorno."""
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD')
    auto_reset = os.getenv('ADMIN_AUTO_RESET', 'false').lower() == 'true'

    if not admin_password:
        # Evitar bloquear el arranque por falta de password; no tocar usuarios
        return

    admin_user = db.query(models.User).filter(models.User.username == admin_username).first()
    if admin_user is None or auto_reset:
        upsert_admin_user(db, admin_username, admin_password, admin_email)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_access_token(token)
    if payload is None or (username := payload.get("sub")) is None:
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# --- Endpoints ---

@auth_router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if get_user(db, username=user.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    return create_user(db=db, user=user)

@api_router.get("/users/me", response_model=schemas.User, tags=["Users"])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@api_router.post("/query", response_model=schemas.QueryResponse, tags=["Brain"])
def process_query(request: schemas.QueryRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    responses = brain.get_response(db, user_input=request.text)
    return {"responses": responses, "status": f"Consulta procesada para {current_user.username}"}

class ResetAdminRequest(BaseModel):
    new_password: str | None = None
    username: str | None = None
    email: str | None = None

@api_router.post("/admin/reset", tags=["Admin"])
def admin_reset(
    payload: ResetAdminRequest,
    db: Session = Depends(get_db),
    x_admin_reset_token: str | None = Header(default=None, convert_underscores=False)
):
    """Resetea o crea el usuario admin.

    Seguridad: requiere header 'X-Admin-Reset-Token' que coincida con ADMIN_RESET_TOKEN.
    """
    expected = os.getenv('ADMIN_RESET_TOKEN')
    if not expected or x_admin_reset_token != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token de reset inválido")

    username = payload.username or os.getenv('ADMIN_USERNAME', 'admin')
    email = payload.email or os.getenv('ADMIN_EMAIL', 'admin@example.com')
    password = payload.new_password or os.getenv('ADMIN_PASSWORD')
    if not password:
        raise HTTPException(status_code=400, detail="Se requiere 'new_password' o ADMIN_PASSWORD")

    user = upsert_admin_user(db, username=username, password=password, email=email)
    return {"status": "ok", "message": f"Usuario admin '{user.username}' reseteado"}

@api_router.get("/metrics", tags=["Monitoring"])
def get_metrics():
    """Endpoint para obtener métricas de rendimiento"""
    return get_performance_metrics()

@api_router.get("/health", tags=["Monitoring"])
def health_check():
    """Endpoint para verificar la salud del sistema"""
    return check_system_health()

# --- Eventos de Startup y Montaje ---

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        # Siembra de roles si no existen
        existing_roles = db.query(models.Role).count()
        if existing_roles == 0:
            print("[Startup] No se encontraron roles. Sembrando roles por defecto...")
            default_roles = [models.Role(name='admin'), models.Role(name='dev'), models.Role(name='cliente')]
            db.add_all(default_roles)
            db.commit()
            print("[Startup] Roles por defecto creados.")

        # Asegurar admin si falta o si se solicita auto reset via env
        ensure_admin_seed(db)
    finally:
        db.close()

app.include_router(auth_router)
app.include_router(api_router)

@app.get("/", tags=["General"])
def root():
    return {"message": "Mea-Core Enterprise API corriendo 🚀"}
