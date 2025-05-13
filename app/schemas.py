from pydantic import BaseModel, EmailStr
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
        orm_mode = True


# Схемы для пользователей
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    facts: List[Fact] = []

    class Config:
        orm_mode = True