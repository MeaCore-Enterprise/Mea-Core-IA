from pydantic import BaseModel
from typing import List, Optional

# --- Esquemas para Tokens (JWT) ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Esquemas para Usuarios ---

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role_id: Optional[int] = None

    class Config:
        from_attributes = True # Nuevo en Pydantic v2, reemplaza orm_mode

# --- Esquemas para la API Principal ---

class QueryRequest(BaseModel):
    text: str

class QueryResponse(BaseModel):
    responses: List[str]
    status: Optional[str] = None
