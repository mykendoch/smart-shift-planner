"""
Worker Database Model

Represents a gig economy worker in the system.
Maps to the 'workers' table in PostgreSQL database.
One worker can have multiple shifts over time.

Schema mapping:
    Python Class: Worker
    Database Table: workers
    Inheritance: Inherits from Base (SQLAlchemy declarative base)
\"\"\"
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from src.database import Base


class Worker(Base):
    \"\"\"
    Worker ORM Model - Database representation of a gig economy worker.
    
    This class maps to the 'workers' table in PostgreSQL.
    When you create a Worker instance and add it to a session, SQLAlchemy
    automatically stores it in the database and generates SQL INSERT statements.
    
    Database Table: workers
    Example rows:
        id=1 | name=\"John Doe\" | email=\"john@example.com\" | created_at=2026-02-12...
        id=2 | name=\"Jane Smith\" | email=\"jane@example.com\" | created_at=2026-02-12...
    
    Relationships:
        Many Shifts can belong to one Worker (one-to-many)
        Access via: worker.shifts → returns list of all shifts for this worker
    \"\"\"
    __tablename__ = \"workers\"

    # ========================================================================
    # DATABASE COLUMNS
    # ========================================================================
    
    # PRIMARY KEY - Uniquely identifies each worker in database
    # Integer: Whole number (1, 2, 3, ...)
    # primary_key=True: This column uniquely identifies each row
    # index=True: Creates database index for fast lookups by ID
    # Auto-incremented: 1, 2, 3, ... assigned automatically
    id = Column(Integer, primary_key=True, index=True)
    
    # WORKER NAME - Display name or full name
    # String(128): Maximum 128 characters
    # nullable=False: Name is required (cannot be empty/null in database)
    # index=True: Create index for faster name searches
    name = Column(String(length=128), nullable=False, index=True)
    
    # EMAIL ADDRESS - Login identifier and unique key
    # String(256): Maximum 256 characters (email addresses can be long)
    # unique=True: No two workers can have the same email (database constraint)
    # nullable=False: Email is required for all workers
    # index=True: Create index for fast email lookups (user login)
    # Used for: Unique identification, login, communication
    email = Column(String(length=256), unique=True, nullable=False, index=True)
    
    # CREATION TIMESTAMP - When worker record was created
    # DateTime: Date and time with timezone
    # server_default=func.now(): PostgreSQL generates timestamp automatically
    # Automatically set to current time when record created (no manual input needed)
    # Used to track: When worker joined system, record age
    created_at = Column(DateTime, server_default=func.now())

    # ========================================================================
    # RELATIONSHIPS - Link to other tables
    # ========================================================================
    
    # One-to-Many: One Worker has many Shifts
    # relationship(\"Shift\"): Link to Shift model class
    # back_populates=\"worker\": Bidirectional - Shift.worker links back to Worker
    # Allows accessing all shifts: worker.shifts → [shift1, shift2, shift3...]
    shifts = relationship(\"Shift\", back_populates=\"worker\")


