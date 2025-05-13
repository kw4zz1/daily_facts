from pydantic import BaseModel
from typing import Optional, List

# Схемы для фактов
class FactBase(BaseModel):
    text: str
    category: str

class FactCreate(FactBase):
    pass

class Fact(FactBase):
    id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

# Схемы для пользователей
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    facts: List[Fact] = []

    class Config:
        from_attributes = True
