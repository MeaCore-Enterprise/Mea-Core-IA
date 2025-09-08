#!/usr/bin/env python3
"""
Reset de admin offline: si la API no responde, este script conecta a la DB
y crea/actualiza el usuario admin usando variables de entorno.
"""

import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal  # type: ignore
from core import models, security  # type: ignore

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def upsert_admin_user(session, username: str, password: str, email: str):
    admin_role = session.query(models.Role).filter(models.Role.name == 'admin').first()
    if not admin_role:
        admin_role = models.Role(name='admin')
        session.add(admin_role)
        session.commit()
        session.refresh(admin_role)

    user = session.query(models.User).filter(models.User.username == username).first()
    hashed_password = security.get_password_hash(password)
    if user:
        user.email = email
        user.hashed_password = hashed_password
        user.role_id = admin_role.id
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info("Usuario admin actualizado: %s", user.username)
        return

    new_user = models.User(username=username, email=email, hashed_password=hashed_password, role_id=admin_role.id)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    logger.info("Usuario admin creado: %s", new_user.username)


def main():
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    password = os.getenv('ADMIN_PASSWORD')
    if not password:
        logger.error("ADMIN_PASSWORD no está definido")
        sys.exit(1)

    session = SessionLocal()
    try:
        upsert_admin_user(session, username=username, password=password, email=email)
    finally:
        session.close()


if __name__ == '__main__':
    main()

