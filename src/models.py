# blog/models.py

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship # Only needed if you have relationships
from .sql_alchemy_db import Base # <-- Import Base from your db setup

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(120), nullable=False)

    posts = relationship('Post', back_populates='author', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

# If you had other models like Post, they would go here too:
class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    author = relationship('User', back_populates='posts')