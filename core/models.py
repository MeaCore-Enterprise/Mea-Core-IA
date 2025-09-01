from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .database import Base

# --- Modelos de Seguridad ---

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    role = relationship("Role")

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    usage_limit = Column(Integer, nullable=True) # Límite de peticiones (ej. por día)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")

# --- Modelos de Memoria ---

class EpisodicMemory(Base):
    __tablename__ = "episodic_memory"
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(Float, index=True)
    type = Column(String, index=True)
    source = Column(String)
    data = Column(JSON)
    access_count = Column(Integer, default=0)
    priority = Column(Integer, default=0, index=True)  # 0: normal, >0: mayor prioridad

class KeyValueStore(Base):
    __tablename__ = "kv_store"
    key = Column(String, primary_key=True, index=True)
    value = Column(Text)
    updated_at = Column(Float)

# --- Modelos de Conocimiento ---

class Fact(Base):
    __tablename__ = "facts"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False, unique=True)
