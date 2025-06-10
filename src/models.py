# blog/models.py

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .sql_alchemy_db import Base
import markdown

# Inherit from the Base class to get SQLAlchemy to automatically create tables and constraints for these classes

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    posts = relationship('Post', back_populates='author', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    author = relationship('User', back_populates='posts')

class MarkdownPost:
    def __init__(self, p: Post):
        self.id = p.id
        self.title = p.title
        self.body = markdown.markdown(str(p.body))
        self.created_at = p.created_at
        self.author_id = p.author_id
        self.author = p.author

def parsePost(post: Post) -> MarkdownPost:
    return MarkdownPost(post) # type: ignore