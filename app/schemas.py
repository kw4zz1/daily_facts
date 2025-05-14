from pydantic import BaseModel
from typing import Optional, List

# Схемы для фактов
class FactBase(BaseModel):
    title: str       # Заголовок факта
    text: str        # Текст факта
    category: str    # Категория

class FactCreate(FactBase):
    pass

class FactOut(FactBase):
    id: int
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

class UserOut(UserBase):
    id: int
    facts: List[FactOut] = []
    class Config:
        from_attributes = True
