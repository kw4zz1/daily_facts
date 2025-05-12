from sqlalchemy.orm import Session
from sqlalchemy.sql import func  # Добавлен импорт func
from . import models, schemas, auth
from datetime import datetime

def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).get(user_id)

def get_random_fact(db: Session, category: str = None):
    query = db.query(models.Fact)
    if category:
        query = query.filter(models.Fact.category == category)
    return query.order_by(func.random()).first()

def list_categories(db: Session):
    return [category[0] for category in db.query(models.Fact.category).distinct().all()]  # Исправлено для возврата строк

def save_user_fact(db: Session, user_id: int, fact_id: int):
    uf = models.UserFact(user_id=user_id, fact_id=fact_id, created_at=datetime.utcnow())
    db.add(uf)
    db.commit()
    return uf

def get_user_history(db: Session, user_id: int):
    return db.query(models.Fact).join(models.UserFact).filter(models.UserFact.user_id == user_id).all()