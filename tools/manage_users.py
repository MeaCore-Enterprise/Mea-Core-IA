# tools/manage_api_keys.py

import argparse
import secrets
import sys
import os

# Añadir el directorio raíz al path para poder importar desde 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal, init_db
from core import models, schemas
from core.security import get_password_hash

# Inicializar la base de datos para asegurarse de que las tablas existen
init_db()

def create_api_key(db: Session, username: str, limit: int = None) -> str:
    """Crea una nueva clave de API para un usuario existente."""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise ValueError(f"El usuario '{username}' no existe.")

    new_key_str = f"mea_sk_{secrets.token_urlsafe(32)}" # Prefijo para identificar la clave
    
    new_api_key = models.APIKey(
        key=new_key_str,
        user_id=user.id,
        usage_limit=limit
    )
    db.add(new_api_key)
    db.commit()
    return new_key_str

def seed_roles_if_needed(db: Session):
    """Asegura que los roles por defecto existan en la base de datos."""
    if db.query(models.Role).count() == 0:
        print("[Seed] No se encontraron roles. Sembrando roles por defecto...")
        default_roles = [models.Role(name='admin'), models.Role(name='dev'), models.Role(name='cliente')]
        db.add_all(default_roles)
        db.commit()

def create_user(db: Session, username: str, email: str, password: str, role: str = 'cliente'):
    """Crea un nuevo usuario con un rol específico."""
    if db.query(models.User).filter(models.User.username == username).first():
        raise ValueError(f"El usuario '{username}' ya existe.")
    
    db_role = db.query(models.Role).filter(models.Role.name == role).first()
    if not db_role:
        raise ValueError(f"El rol '{role}' no es válido. Roles disponibles: admin, dev, cliente")

    hashed_password = get_password_hash(password)
    new_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role_id=db_role.id
    )
    db.add(new_user)
    db.commit()
    print(f"Usuario '{username}' creado exitosamente con el rol de '{role}'.")

def list_api_keys(db: Session, username: str = None):
    """Lista las claves de API, opcionalmente filtrando por usuario."""
    query = db.query(models.APIKey).join(models.User)
    if username:
        query = query.filter(models.User.username == username)
    
    keys = query.all()
    if not keys:
        print("No se encontraron claves de API.")
        return

    print(f"{'ID':<5} {'Usuario':<15} {'Clave (prefijo)':<15} {'Activa':<8} {'Uso':<15}")
    print("-" * 60)
    for key in keys:
        usage = f"{key.usage_count}/{key.usage_limit or '∞'}"
        print(f"{key.id:<5} {key.user.username:<15} {key.key[:12]+'...':<15} {str(key.is_active):<8} {usage:<15}")

def revoke_api_key(db: Session, key_prefix: str):
    """Revoca (desactiva) una clave de API por su prefijo."""
    key_to_revoke = db.query(models.APIKey).filter(models.APIKey.key.like(f"{key_prefix}%")).first()
    if not key_to_revoke:
        raise ValueError(f"No se encontró ninguna clave que empiece con '{key_prefix}'.")
    
    key_to_revoke.is_active = False
    db.commit()
    print(f"Clave {key_to_revoke.key[:12]}... revocada exitosamente.")

def main():
    parser = argparse.ArgumentParser(description="Herramienta de gestión de usuarios y claves de API para Mea-Core.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Comandos de Usuario ---
    user_parser = subparsers.add_parser("create_user", help="Crea un nuevo usuario.")
    user_parser.add_argument("-u", "--username", required=True, help="Nombre de usuario.")
    user_parser.add_argument("-e", "--email", required=True, help="Email del usuario.")
    user_parser.add_argument("-p", "--password", required=True, help="Contraseña del usuario.")
    user_parser.add_argument("-r", "--role", default='cliente', help="Rol del usuario (admin, dev, cliente). Por defecto: cliente.")

    # --- Comandos de Clave de API ---
    key_parser = subparsers.add_parser("create_key", help="Crea una nueva clave de API para un usuario.")
    key_parser.add_argument("-u", "--username", required=True, help="Nombre del usuario al que se le asignará la clave.")
    key_parser.add_argument("-l", "--limit", type=int, help="Límite de uso diario para la clave (opcional).")

    list_parser = subparsers.add_parser("list_keys", help="Lista las claves de API existentes.")
    list_parser.add_argument("-u", "--username", help="Filtra las claves por nombre de usuario (opcional).")

    revoke_parser = subparsers.add_parser("revoke_key", help="Revoca (desactiva) una clave de API.")
    revoke_parser.add_argument("--key", required=True, help="La clave de API completa o su prefijo (ej. mea_sk_...).")

    args = parser.parse_args()
    db = SessionLocal()

    try:
        # Asegurarse de que los roles existan antes de cualquier operación
        seed_roles_if_needed(db)

        if args.command == "create_user":
            create_user(db, args.username, args.email, args.password, args.role)
        elif args.command == "create_key":
            new_key = create_api_key(db, args.username, args.limit)
            print(f"Clave de API creada exitosamente para '{args.username}':")
            print(new_key)
        elif args.command == "list_keys":
            list_api_keys(db, args.username)
        elif args.command == "revoke_key":
            revoke_api_key(db, args.key)
    except ValueError as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
