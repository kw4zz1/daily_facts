from sqlalchemy.orm import Session
from sqlalchemy.sql import func
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

def get_random_fact(db: Session, category: str = None):
    query = db.query(models.Fact)
    if category:
        query = query.filter(models.Fact.category == category)
    return query.order_by(func.random()).first()

def list_categories(db: Session):
    return [row[0] for row in db.query(models.Fact.category).distinct().all()]

def save_user_fact(db: Session, user_id: int, fact_id: int):
    uf = models.UserFact(user_id=user_id, fact_id=fact_id, created_at=datetime.utcnow())
    db.add(uf)
    db.commit()
    return uf

def get_user_history(db: Session, user_id: int):
    return db.query(models.Fact).join(models.UserFact).filter(models.UserFact.user_id == user_id).all()

def create_fact(db: Session, fact: schemas.FactCreate):
    db_fact = models.Fact(
        title=fact.title,
        text=fact.text,
        category=fact.category
    )
    db.add(db_fact)
    db.commit()
    db.refresh(db_fact)
    return db_fact

def get_fact_by_content(db: Session, text: str):
    return db.query(models.Fact).filter(models.Fact.text == text).first()

def delete_user_fact(db: Session, user_id: int, fact_id: int):
    db.query(models.UserFact).filter_by(user_id=user_id, fact_id=fact_id).delete()
    db.commit()


def clear_user_history(db: Session, user_id: int):
    db.query(models.UserFact).filter(
        models.UserFact.user_id == user_id
    ).delete()
    db.commit()
