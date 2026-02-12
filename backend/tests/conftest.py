"""Pytest configuration and fixtures for database testing.

This module provides fixtures for:
- Creating temporary test database sessions
- Seeding test data (sample workers, shifts)
- FastAPI TestClient with test DB
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta

from src.core.config import settings
from src.database import Base, get_db
from src.main import app
from src.models import Worker, Shift
from fastapi.testclient import TestClient


# Create test engine (using same DB but could be separate)
TEST_DATABASE_URL = settings.DATABASE_URL
test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def db_session_factory():
    """Create test database tables once per test session."""
    Base.metadata.create_all(bind=test_engine)
    yield TestingSessionLocal
    # Keep tables for manual inspection or teardown as needed
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db(db_session_factory):
    """Provide a fresh DB session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """Provide FastAPI test client with test DB."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_worker(db):
    """Create a sample worker for testing."""
    worker = Worker(
        name="John Doe",
        email="john@example.com"
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@pytest.fixture
def sample_shift(db, sample_worker):
    """Create a sample shift for testing."""
    now = datetime.utcnow()
    shift = Shift(
        worker_id=sample_worker.id,
        start_time=now,
        end_time=now + timedelta(hours=4),
        earnings=50.0,
        predicted_earnings=60.0
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift
