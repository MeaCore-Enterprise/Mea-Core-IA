from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import os
import json

from jose import JWTError, jwt
from passlib.context import CryptContext
from decouple import config

# --- Configuración de Auditoría ---
LOG_DIR = "logs/security"
AUDIT_LOG_FILE = os.path.join(LOG_DIR, "security_audit.log")

# --- Configuración de Seguridad ---

SECRET_KEY = config('SECRET_KEY', default='a_very_secret_key_for_development')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int, default=30)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from cryptography.fernet import Fernet

# --- Configuración de Cifrado ---
# IMPORTANTE: En producción, esta clave DEBE ser cargada de forma segura (ej. Vault, AWS KMS)
# Generar una clave con: Fernet.generate_key()
ENCRYPTION_KEY = config('MEA_ENCRYPTION_KEY', default=Fernet.generate_key().decode())
fernet = Fernet(ENCRYPTION_KEY.encode())

# --- Clase de Auditoría de Seguridad ---

class SecurityAuditor:
    """Registra eventos de seguridad críticos en un log de auditoría cifrado."""
    def __init__(self):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        self.failed_logins = {}
        self.brute_force_threshold = 5 # Número de intentos fallidos para generar una alerta

    def log_event(self, event_type: str, subject: str, outcome: str, details: Optional[Dict[str, Any]] = None):
        """
        Registra y cifra un evento de seguridad.
        También detecta posibles ataques de fuerza bruta.
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "subject": subject,
            "outcome": outcome,
            "details": details or {}
        }
        
        # Cifrar el log antes de escribirlo
        encrypted_log = encrypt_data(json.dumps(log_entry))

        with open(AUDIT_LOG_FILE, 'ab') as f: # Escribir en modo binario
            f.write(encrypted_log + b'\n')

        # Detección de anomalías: fuerza bruta en logins
        if event_type == "LOGIN" and outcome == "FAILURE":
            self.check_brute_force(subject)

    def check_brute_force(self, username: str):
        """Comprueba si se está produciendo un ataque de fuerza bruta."""
        now = time.time()
        if username not in self.failed_logins:
            self.failed_logins[username] = []
        
        # Añadir el intento fallido actual y limpiar los antiguos (más de 5 min)
        self.failed_logins[username].append(now)
        self.failed_logins[username] = [t for t in self.failed_logins[username] if now - t < 300]

        if len(self.failed_logins[username]) >= self.brute_force_threshold:
            alert_details = {"message": f"Posible ataque de fuerza bruta detectado para el usuario '{username}'.", "count": len(self.failed_logins[username])}
            self.log_event("ANOMALY_DETECTED", subject=username, outcome="BRUTE_FORCE_ALERT", details=alert_details)
            # Limpiar los intentos para no generar alertas repetidas inmediatamente
            self.failed_logins[username] = []

# Instancia global para ser usada en toda la aplicación
auditor = SecurityAuditor()

# --- Utilidades de Contraseña ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña plana contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    # Evento de auditoría: se está generando un nuevo hash
    # No se guarda la contraseña en el log, solo el hecho.
    auditor.log_event("PASSWORD_HASH", subject="system", outcome="SUCCESS")
    return pwd_context.hash(password)

# --- Utilidades de JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un nuevo token de acceso JWT."""
    to_encode = data.copy()
    subject = to_encode.get('sub', 'unknown')
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
auditor.log_event("TOKEN_CREATION", subject=subject, outcome="SUCCESS")
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica un token de acceso. Devuelve el payload o None si es inválido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        auditor.log_event("TOKEN_VALIDATION", subject=token, outcome="FAILURE", details={"error": str(e)})
        return None

# --- Utilidades de Cifrado ---

def encrypt_data(data: str) -> bytes:
    """Cifra una cadena de texto."""
    return fernet.encrypt(data.encode('utf-8'))

def decrypt_data(encrypted_data: bytes) -> str:
    """Descifra datos y los devuelve como cadena de texto."""
    try:
        return fernet.decrypt(encrypted_data).decode('utf-8')
    except Exception:
        # Si la clave cambia o los datos están corruptos, la desencriptación fallará.
        return "[datos indescifrables]"
