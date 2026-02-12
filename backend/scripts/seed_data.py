"""Initialize database with sample data for development and testing.

This script:
1. Creates all database tables
2. Seeds sample workers
3. Seeds sample shifts
4. Seeds sample income guarantee records

Run with:
    cd backend
    python scripts/seed_data.py
"""
import logging
from datetime import datetime, timedelta
from src.database import engine, SessionLocal, Base
from src.models import Worker, Shift

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_workers(db):
    """Create sample workers."""
    workers_data = [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"},
        {"name": "Bob Johnson", "email": "bob@example.com"},
        {"name": "Alice Williams", "email": "alice@example.com"},
        {"name": "Charlie Brown", "email": "charlie@example.com"},
    ]
    
    for data in workers_data:
        existing = db.query(Worker).filter(Worker.email == data["email"]).first()
        if not existing:
            worker = Worker(**data)
            db.add(worker)
            logger.info(f"Created worker: {data['name']}")
    
    db.commit()


def seed_shifts(db):
    """Create sample shifts for testing income guarantee logic."""
    workers = db.query(Worker).all()
    if not workers:
        logger.warning("No workers found. Create workers first.")
        return
    
    now = datetime.utcnow()
    shifts_data = [
        # Worker 1: Good earnings (meets guarantee)
        {
            "worker_id": workers[0].id,
            "start_time": now - timedelta(days=5),
            "end_time": (now - timedelta(days=5)) + timedelta(hours=5),
            "earnings": 95.0,
            "predicted_earnings": 100.0,
        },
        # Worker 1: Poor earnings (below guarantee)
        {
            "worker_id": workers[0].id,
            "start_time": now - timedelta(days=3),
            "end_time": (now - timedelta(days=3)) + timedelta(hours=4),
            "earnings": 60.0,
            "predicted_earnings": 85.0,
        },
        # Worker 2: Mixed performance
        {
            "worker_id": workers[1].id,
            "start_time": now - timedelta(days=2),
            "end_time": (now - timedelta(days=2)) + timedelta(hours=6),
            "earnings": 110.0,
            "predicted_earnings": 120.0,
        },
        {
            "worker_id": workers[1].id,
            "start_time": now - timedelta(days=1),
            "end_time": (now - timedelta(days=1)) + timedelta(hours=5),
            "earnings": 75.0,
            "predicted_earnings": 100.0,
        },
    ]
    
    for data in shifts_data:
        shift = Shift(**data)
        db.add(shift)
        logger.info(f"Created shift for worker {data['worker_id']}: "
                   f"predicted=${data['predicted_earnings']}, actual=${data['earnings']}")
    
    db.commit()


def main():
    """Initialize database with tables and sample data."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created")
    
    db = SessionLocal()
    try:
        logger.info("Seeding sample workers...")
        seed_workers(db)
        logger.info("✓ Sample workers created")
        
        logger.info("Seeding sample shifts...")
        seed_shifts(db)
        logger.info("✓ Sample shifts created")
        
        logger.info("\n✅ Database initialized successfully!")
        logger.info("You can now run tests or start the API server.")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
