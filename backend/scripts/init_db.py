"""Small helper to create database tables from SQLAlchemy models.

Run this to create tables (useful for tests and initial setup):

    python backend/scripts/init_db.py

It reads `DATABASE_URL` from environment or .env via settings.
"""
import logging
from src.database import engine, Base


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logging.info("Done.")


if __name__ == '__main__':
    main()
