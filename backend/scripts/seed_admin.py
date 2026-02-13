"""
Seed admin user and demo data for Smart Shift Planner.

Run this script after running database initialization:

    cd backend
    python scripts/seed_admin.py

This will create:
- Admin user: mykendoche@gmail.com / admin123
- Demo driver: driver@example.com / driver123
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.user import User, UserRole
from src.core.config import settings
import bcrypt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# Create direct database connection
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()


def seed_admin_user(db):
    """Create the main admin user."""
    admin_email = "mykendoche@gmail.com"
    admin_password = "admin123"
    admin_name = "Admin User"
    
    # Check if admin already exists
    existing = db.query(User).filter(User.email == admin_email).first()
    if existing:
        logger.info(f"Admin user '{admin_email}' already exists")
        return existing
    
    # Create admin directly
    admin_user = User(
        email=admin_email,
        password_hash=hash_password(admin_password),
        full_name=admin_name,
        phone="+1234567890",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    logger.info(f"✅ Created admin user: {admin_email}")
    return admin_user


def seed_demo_driver(db):
    """Create a demo driver user for testing."""
    driver_email = "driver@example.com"
    driver_password = "driver123"
    driver_name = "Demo Driver"
    
    # Check if driver already exists
    existing = db.query(User).filter(User.email == driver_email).first()
    if existing:
        logger.info(f"Driver user '{driver_email}' already exists")
        return existing
    
    # Create driver directly
    driver_user = User(
        email=driver_email, 
        password_hash=hash_password(driver_password),
        full_name=driver_name,
        phone="+0987654321",
        role=UserRole.DRIVER,
        is_active=True,
        is_verified=True
    )
    
    db.add(driver_user)
    db.commit()
    db.refresh(driver_user)
    
    logger.info(f"✅ Created demo driver: {driver_email}")
    return driver_user


def main():
    """Run the seeding process."""
    logger.info("=" * 60)
    logger.info("SMART SHIFT PLANNER - SEED ADMIN USER")
    logger.info("=" * 60)
    
    try:
        # Seed admin user
        admin = seed_admin_user(db)
        
        # Seed demo driver
        driver = seed_demo_driver(db)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("SEEDING COMPLETE!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Login Credentials:")
        logger.info("-" * 60)
        logger.info("Admin:")
        logger.info("  Email:    mykendoche@gmail.com")
        logger.info("  Password: admin123")
        logger.info("")
        logger.info("Demo Driver:")
        logger.info("  Email:    driver@example.com")
        logger.info("  Password: driver123")
        logger.info("-" * 60)
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
