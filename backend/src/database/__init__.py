"""
Database Connection and Session Management

This module handles all database setup:
1. PostgreSQL connection pooling via SQLAlchemy
2. Session factory for creating request-scoped database sessions
3. SQLAlchemy declarative base for ORM models
4. FastAPI dependency injection for database access

Every HTTP request gets its own database session that automatically closes.
This prevents connection leaks and ensures proper resource cleanup.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from src.core.config import settings

# ============================================================================
# DATABASE ENGINE - Core connection to PostgreSQL
# ============================================================================
# create_engine() creates a connection pool that:
# - Manages multiple connections to PostgreSQL efficiently
# - Reuses connections instead of creating new ones each time
# - Automatically closes idle connections
#
# Parameters:
#   settings.DATABASE_URL: postgresql://user:password@host:port/database
#   echo=False: Don't log all SQL (set to True for debugging)
#   future=True: Use SQLAlchemy 2.0 style behavior

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

# ============================================================================
# SESSION FACTORY - Creates database sessions for each request
# ============================================================================
# SessionLocal() creates a new session each time it's called.
# 
# Session lifecycle:
#   sessionmaker creates factory → SessionLocal() → Session object → 
#   endpoint uses session → get_db() closes session in finally block
#
# Parameters:
#   bind=engine: Use the engine created above
#   autocommit=False: Changes require explicit .commit() call
#   autoflush=False: Objects don't auto-flush to DB before queries

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# ============================================================================
# DECLARATIVE BASE - Parent class for all ORM models
# ============================================================================
# All database model classes inherit from Base:
#   class Worker(Base):
#       __tablename__ = "workers"
#   class Shift(Base):
#       __tablename__ = "shifts"
#
# Base.metadata contains all table definitions and is used to:
# - Create all tables: Base.metadata.create_all(bind=engine)
# - Generate SQL DDL (CREATE TABLE, etc.)

Base = declarative_base()


def get_db() -> Generator:
    """
    FastAPI Dependency Injection for Database Sessions
    
    This function provides a database session to any endpoint that requests it.
    FastAPI automatically detects `Depends(get_db)` and calls this function.
    
    How it works:
    1. Client makes HTTP request to endpoint
    2. FastAPI sees Depends(get_db) in endpoint signature
    3. FastAPI calls get_db() → creates SessionLocal() → database session
    4. Yields the session to the endpoint function
    5. Endpoint function executes and uses the session
    6. After endpoint returns, finally block closes the session
    7. Database connection returns to pool for reuse
    
    Example usage in an endpoint:
        @router.get(\"/workers/\")
        def list_workers(db: Session = Depends(get_db)):
            # db is automatically provided by FastAPI
            return db.query(Worker).all()
    
    Benefits:
    - Request-scoped sessions (one per HTTP request, not shared)
    - Automatic cleanup prevents connection leaks
    - Type-safe database access (Session type)
    - Database connection automatically closed after each request
    
    Yields:
        Session: SQLAlchemy database session for use in endpoint
    \"\"\"
    db = SessionLocal()  # Create new database session
    try:
        yield db  # Provide session to endpoint function
    finally:
        # Always execute, even if endpoint raises exception
        db.close()  # Close session and return connection to pool
