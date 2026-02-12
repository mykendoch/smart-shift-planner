"""
QUICK START GUIDE - Smart Shift Planner Backend
================================================

This guide walks you through setting up and running the backend with all tests and ML endpoints.

Prerequisites Verified:
✅ PostgreSQL running at localhost:5432
✅ Database: gigeconomy (user: postgres, password: Ndoch)
✅ Python dependencies installed (see requirements.txt)
✅ .env file configured with DATABASE_URL
✅ All source files encoded as UTF-8

---

1. CREATE DATABASE SCHEMA (Alembic Migrations)
===============================================

Navigate to backend/ directory:
    cd backend

Create initial migration:
    alembic revision --autogenerate -m "Initial schema"

This will generate a new migration file in alembic/versions/ with Worker and Shift tables.

Apply the migration to PostgreSQL:
    alembic upgrade head

Expected output:
    INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
    INFO  [alembic.runtime.migration] Will assume transactional DDL.
    INFO  [alembic.runtime.migration] Running upgrade  -> <revision_id>
    (Creates workers and shifts tables)

Verify tables were created:
    psql -U postgres -d gigeconomy -c "\dt"

You should see:
    public | shifts  | table | postgres
    public | workers | table | postgres

---

2. SEED TEST DATA (Optional but Recommended)
=============================================

Populate the database with sample workers and shifts:
    python scripts/seed_data.py

Expected output:
    INFO     Seeding database with sample data...
    INFO     Created worker: Alice Johnson (alice@example.com)
    INFO     Created worker: Bob Smith (bob@example.com)
    ...
    INFO     Created shift for Alice: 2024-12-15 09:00:00 - 13:00:00 (earned $80)
    ...
    INFO     Database seeding complete!

This creates:
- 5 workers with different names/emails
- 4 shifts with varied earnings (to test income guarantee top-up logic)

---

3. RUN UNIT TESTS (No API Server Needed)
=========================================

Test basic endpoints that don't require database:
    python -m pytest tests/unit/test_basic.py -v

Expected output:
    tests/unit/test_basic.py::test_root PASSED                         [ 50%]
    tests/unit/test_basic.py::test_health PASSED                       [100%]

    ============================= 2 passed in 0.XX s =============================

---

4. RUN INTEGRATION TESTS (Requires DB)
======================================

Test worker/shift CRUD operations and income guarantee logic:
    python -m pytest tests/integration/test_workers_shifts.py -v

Expected output:
    tests/integration/test_workers_shifts.py::test_create_worker PASSED [ 12%]
    tests/integration/test_workers_shifts.py::test_create_worker_duplicate_email PASSED [ 25%]
    tests/integration/test_workers_shifts.py::test_list_workers PASSED [ 37%]
    tests/integration/test_workers_shifts.py::test_create_shift PASSED [ 50%]
    tests/integration/test_workers_shifts.py::test_create_shift_invalid_worker PASSED [ 62%]
    tests/integration/test_workers_shifts.py::test_list_shifts PASSED [ 75%]
    tests/integration/test_workers_shifts.py::test_compute_topup_below_threshold PASSED [ 87%]
    tests/integration/test_workers_shifts.py::test_compute_topup_meets_guarantee PASSED [100%]

    ============================= 8 passed in 0.XX s =============================

Test ML prediction endpoints:
    python -m pytest tests/integration/test_predictions.py -v

Expected output:
    tests/integration/test_predictions.py::test_predict_earnings PASSED [ 20%]
    tests/integration/test_predictions.py::test_predict_earnings_peak_vs_offpeak PASSED [ 40%]
    tests/integration/test_predictions.py::test_forecast_demand PASSED [ 60%]
    tests/integration/test_predictions.py::test_recommend_shifts PASSED [ 80%]
    tests/integration/test_predictions.py::test_recommend_shifts_weekend_higher_earnings PASSED [100%]

    ============================= 5 passed in 0.XX s =============================

Run all tests:
    python -m pytest tests/ -v

---

5. START THE API SERVER
=======================

Launch the FastAPI development server:
    python -m uvicorn src.main:app --reload

Expected output:
    INFO:     Uvicorn running on http://127.0.0.1:8000
    INFO:     Application startup complete
    
    (Server logs will show startup info with system details)

The --reload flag auto-restarts when you change code. Omit it for production.

---

6. EXPLORE THE API
==================

Open Swagger UI (Interactive API Docs):
    http://localhost:8000/docs

Open ReDoc (Alternative API Docs):
    http://localhost:8000/redoc

Root Info Endpoint (Project Details):
    http://localhost:8000/

Health Check:
    http://localhost:8000/health

---

7. TEST REST ENDPOINTS MANUALLY
================================

Using curl (or REST CLI of your choice):

A) WORKER ENDPOINTS
-------------------

Create a worker:
    curl -X POST "http://localhost:8000/api/v1/workers" \
         -H "Content-Type: application/json" \
         -d '{"name":"Charlie Brown","email":"charlie@example.com"}'

List all workers:
    curl "http://localhost:8000/api/v1/workers"

B) SHIFT ENDPOINTS
------------------

Create a shift (worker_id 1):
    curl -X POST "http://localhost:8000/api/v1/shifts" \
         -H "Content-Type: application/json" \
         -d '{
           "worker_id": 1,
           "start_time": "2024-12-15T09:00:00",
           "end_time": "2024-12-15T17:00:00",
           "earnings": 80.0
         }'

List all shifts:
    curl "http://localhost:8000/api/v1/shifts"

Get income guarantee top-up for a shift (shift_id 1):
    curl "http://localhost:8000/api/v1/shifts/1/topup"
    
    Example response: {"topup": 10.0}
    Meaning: If actual earnings were $80 and predicted were $100,
             with 90% threshold, top-up = max(0, 100*0.9 - 80) = $10

C) PREDICTIONS ENDPOINTS (ML)
-----------------------------

Predict hourly earnings:
    curl "http://localhost:8000/api/v1/predictions/earnings?hour=18&day_of_week=4&location=downtown&demand_level=0.8"
    
    Response: {"hour": 18, "location": "downtown", "predicted_hourly_earnings": 25.2}

Forecast demand pattern (24-hour):
    curl "http://localhost:8000/api/v1/predictions/demand-forecast?location=downtown"
    
    Response: {
      "location": "downtown",
      "hourly_demand": {"0": 0.2, "1": 0.15, ..., "18": 1.0, "19": 0.95, ...},
      "peak_hours": [18, 19, 20]
    }

Recommend best shifts by predicted earnings:
    curl "http://localhost:8000/api/v1/predictions/recommend-shifts?location=downtown&date_type=weekday&duration_hours=4.0&top_n=3"
    
    Response: {
      "location": "downtown",
      "recommendations": [
        {"start_hour": 18, "duration_hours": 4.0, "predicted_earnings": 120.0},
        {"start_hour": 17, "duration_hours": 4.0, "predicted_earnings": 110.0},
        {"start_hour": 19, "duration_hours": 4.0, "predicted_earnings": 108.0}
      ]
    }

---

8. CHECK LOGS
=============

Application writes structured JSON logs to:
    logs/app.log

Each log line includes: timestamp, level, message, context.

Example tail:
    tail -f logs/app.log

---

9. TESTING WORKFLOW (Summary)
============================

Recommended order:
1. python scripts/init_db.py             (If starting from scratch)
2. alembic revision --autogenerate -m "Initial schema"
3. alembic upgrade head                  (Apply migrations to PostgreSQL)
4. python scripts/seed_data.py           (Optional: populate test data)
5. python -m pytest tests/ -v            (Run all tests)
6. python -m uvicorn src.main:app --reload  (Start server)
7. Visit http://localhost:8000/docs      (Explore API in Swagger)

---

10. TROUBLESHOOTING
===================

Q: "psycopg2/pg8000 error: connection refused"
A: Check PostgreSQL is running: `psql -U postgres -c "SELECT 1"`

Q: "No such table: workers"
A: Run `alembic upgrade head` to apply migrations

Q: "Email already exists"
A: Each worker must have unique email. Either use new email or clear DB: `alembic downgrade base`

Q: "Port 8000 already in use"
A: Use different port: `python -m uvicorn src.main:app --port 8001`

Q: "ModuleNotFoundError: src not found"
A: Make sure you're running from backend/ directory

Q: "SyntaxError: source code string cannot contain null bytes"
A: UTF-16 encoding issue in __init__.py files. Not applicable anymore (all fixed).

---

11. PROJECT STRUCTURE REFERENCE
================================

backend/
├── src/
│   ├── main.py                      # FastAPI app entry point
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── workers.py           # Worker CRUD endpoints
│   │   │   ├── shifts.py            # Shift CRUD + income guarantee
│   │   │   └── predictions.py       # ML prediction endpoints
│   │   └── __init__.py              # Router aggregation
│   ├── models/
│   │   ├── worker.py                # SQLAlchemy Worker model
│   │   └── shift.py                 # SQLAlchemy Shift model
│   ├── schemas/
│   │   └── __init__.py              # Pydantic validation schemas
│   ├── services/
│   │   └── shifts.py                # Business logic (top-up calculation)
│   ├── ml/
│   │   └── predictors.py            # EarningsPredictor, DemandForecaster, ShiftOptimizer
│   ├── database/
│   │   └── __init__.py              # SQLAlchemy setup
│   └── core/
│       └── config.py                # Settings from .env
├── tests/
│   ├── unit/
│   │   └── test_basic.py            # Basic endpoint tests
│   └── integration/
│       ├── test_workers_shifts.py   # CRUD + income guarantee tests
│       └── test_predictions.py      # ML endpoint tests
├── scripts/
│   ├── init_db.py                   # Create tables (one-shot)
│   ├── seed_data.py                 # Populate test data
│   └── check_nulls.py               # Utility to detect encoding issues
├── alembic/
│   ├── versions/                    # Migration files
│   ├── env.py                       # Alembic environment
│   └── script.py.mako               # Template for migrations
├── alembic.ini                      # Alembic config
├── requirements.txt                 # Python dependencies
└── conftest.py                      # pytest fixtures (DB, API client)

---

END OF QUICK START GUIDE
"""
