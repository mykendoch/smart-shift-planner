"""Debug script to test database connection and schema"""
import logging
import sys
import traceback
from sqlalchemy import text

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    print("=" * 70)
    print("DEBUGGING WORKER CREATION ISSUE")
    print("=" * 70)
    
    # Test imports
    print("\n1. Testing imports...")
    from src.database import engine, SessionLocal, Base
    print("   ✓ Database module imported")
    
    from src.models import Worker, Shift
    print("   ✓ Models imported")
    
    from src.schemas import WorkerCreate, WorkerRead
    print("   ✓ Schemas imported")
    
    # Test connections
    print("\n2. Testing database connection...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("   ✓ Connection successful")
    
    # Check tables
    print("\n3. Checking tables...")
    inspector = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    with engine.connect() as conn:
        result = conn.execute(inspector)
        tables = [row[0] for row in result]
        print(f"   Tables found: {tables}")
        if "workers" not in tables:
            print("   ⚠ 'workers' table not found!")
        if "shifts" not in tables:
            print("   ⚠ 'shifts' table not found!")
    
    # Try creating tables
    print("\n4. Creating schema...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ Schema created")
    
    # Verify tables exist now
    print("\n5. Verifying tables...")
    with engine.connect() as conn:
        result = conn.execute(inspector)
        tables = [row[0] for row in result]
        print(f"   Tables now: {tables}")
    
    # Try a test insert
    print("\n6. Testing insert...")
    db = SessionLocal()
    try:
        worker = Worker(name="Test User", email="test123@example.com")
        db.add(worker)
        db.commit()
        db.refresh(worker)
        print(f"   ✓ Worker created: ID={worker.id}, Name={worker.name}, Email={worker.email}")
        
        # Delete for cleanup
        db.delete(worker)
        db.commit()
        print("   ✓ Test worker deleted")
    finally:
        db.close()
    
    print("\n" + "=" * 70)
    print("DEBUG COMPLETE - All systems operational!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
