"""
Direct database initialization - creates all tables.

Run with:
    cd backend
    python scripts/init_db_direct.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Create all tables directly."""
    logger.info("Creating database tables...")
    
    # Import all models to ensure they're registered with Base
    from src.models.user import User, AdminSettings
    from src.models.eligibility_metrics import WorkerEligibility, VolatilityMetrics, PredictionAccuracy, WorkerSurvey
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Database tables created successfully!")
    
    # List created tables
    logger.info("\nCreated tables:")
    inspector = __import__('sqlalchemy').inspect(engine)
    for table_name in inspector.get_table_names():
        logger.info(f"  - {table_name}")


if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
