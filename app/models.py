from sqlalchemy import Table, Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import registry, relationship
from .database import metadata

mapper_registry = registry()

class User:
    def __init__(self, username=None, hashed_password=None):
        self.username = username
        self.hashed_password = hashed_password
        self.id = None

class Fact:
    def __init__(self, category=None, text=None):
        self.category = category
        self.text = text
        self.id = None

class UserFact:
    def __init__(self, user_id=None, fact_id=None, created_at=None):
        self.user_id = user_id
        self.fact_id = fact_id
        self.created_at = created_at
        self.id = None

users_table = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String, unique=True, index=True, nullable=False),
    Column("hashed_password", String, nullable=False),
)

facts_table = Table(
    "facts", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("category", String, index=True, nullable=False),
    Column("text", String, nullable=False),
)

user_facts_table = Table(
    "user_facts", metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", ForeignKey("users.id")),
    Column("fact_id", ForeignKey("facts.id")),
    Column("created_at", TIMESTAMP),
)

mapper_registry.map_imperatively(User, users_table, properties={
    "facts": relationship("Fact", secondary=user_facts_table, back_populates="users")
})
mapper_registry.map_imperatively(Fact, facts_table, properties={
    "users": relationship("User", secondary=user_facts_table, back_populates="facts")
})
mapper_registry.map_imperatively(UserFact, user_facts_table)