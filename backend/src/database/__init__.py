"""Database setup using SQLAlchemy.
Provides `engine`, `SessionLocal`, `Base`, and a `get_db` dependency generator.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

from src.core.config import settings


# Create the SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Declarative base for models
Base = declarative_base()


def get_db() -> Generator:
    """Yield a database session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
