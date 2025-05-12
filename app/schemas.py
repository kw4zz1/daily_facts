from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class FactBase(BaseModel):
    category: str
    text: str

class FactOut(FactBase):
    id: int

    class Config:
        from_attributes = True
