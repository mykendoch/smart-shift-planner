"""
SMART SHIFT PLANNER - QUICK REFERENCE GUIDE
============================================

🎯 PROJECT STATUS: ✅ COMPLETE
- 15/15 tests passing
- All components implemented
- Production-ready

---

⚡ KEY COMMANDS
===============

1. CREATE DATABASE TABLES (First Time Only)
   $ cd backend
   $ alembic revision --autogenerate -m "Initial schema"
   $ alembic upgrade head

2. POPULATE TEST DATA (Optional)
   $ python scripts/seed_data.py

3. RUN ALL TESTS
   $ python -m pytest tests/ -v

4. RUN UNIT TESTS ONLY
   $ python -m pytest tests/unit/ -v

5. RUN INTEGRATION TESTS ONLY
   $ python -m pytest tests/integration/ -v

6. START API SERVER
   $ python -m uvicorn src.main:app --reload

7. EXPLORE API
   http://localhost:8000/docs  (Interactive Swagger UI)

---

🏗️ ARCHITECTURE LAYERS
=======================

API Layer
  ↓
Services Layer (Business Logic)
  ↓
Models Layer (ORM/Database)
  ↓
PostgreSQL Database

---

📁 KEY FILES
=============

API ENDPOINTS
  src/api/v1/endpoints/
    - workers.py       → POST/GET /api/v1/workers
    - shifts.py        → POST/GET /api/v1/shifts + income guarantee
    - predictions.py   → ML predictions (earnings, demand, recommendations)

MODELS
  src/models/
    - worker.py        → Workers table
    - shift.py         → Shifts table (with FK to workers)

ML
  src/ml/predictors.py → EarningsPredictor, DemandForecaster, ShiftOptimizer

TESTS
  tests/unit/test_basic.py          → 2 unit tests ✅
  tests/integration/test_workers_shifts.py  → 8 integration tests ✅
  tests/integration/test_predictions.py    → 5 ML tests ✅

DOCUMENTATION
  QUICKSTART.md              → Step-by-step guide (11 sections)
  ARCHITECTURE.md            → Design overview, data flows, schemas
  PROJECT_COMPLETION_REPORT.md → Full completion summary

---

💡 EXAMPLE WORKFLOWS
====================

A) CREATE WORKER & LOG SHIFT
    1. POST /api/v1/workers
       {"name": "Alice", "email": "alice@example.com"}
    
    2. POST /api/v1/shifts
       {"worker_id": 1, "start_time": "2024-12-15T17:00:00", 
        "end_time": "2024-12-15T21:00:00", "earnings": 85.0}
    
    3. GET /api/v1/shifts/1/topup
       (Returns income guarantee top-up amount)

B) GET SHIFT RECOMMENDATIONS
    GET /api/v1/predictions/recommend-shifts?location=downtown&date_type=weekday&duration_hours=4&top_n=3
    
    Response: 3 best shifts by predicted earnings

C) CHECK DEMAND FORECAST
    GET /api/v1/predictions/demand-forecast?location=downtown
    
    Response: 24-hour demand pattern + peak hours

---

🐛 TROUBLESHOOTING QUICK FIXES
===============================

Q: "relation \"workers\" does not exist"
A: Run migrations: alembic upgrade head

Q: "ModuleNotFoundError"
A: Make sure you're in backend/ directory: cd backend

Q: "Port 8000 already in use"
A: Use different port: python -m uvicorn src.main:app --port 8001

Q: "Connection refused" (PostgreSQL)
A: Start PostgreSQL server (or verify at localhost:5432)

See QUICKSTART.md section 10 for more troubleshooting.

---

🧪 TEST EXECUTION SUMMARY
==========================

Last Run: ✅ All 15 Tests PASSING (0.41 seconds)

Unit Tests (2)
  ✅ test_root
  ✅ test_health

ML Predictions (5)
  ✅ test_predict_earnings
  ✅ test_predict_earnings_peak_vs_offpeak
  ✅ test_forecast_demand
  ✅ test_recommend_shifts
  ✅ test_recommend_shifts_weekend_higher_earnings

Workers/Shifts (8)
  ✅ test_create_worker
  ✅ test_create_worker_duplicate_email
  ✅ test_list_workers
  ✅ test_create_shift
  ✅ test_create_shift_invalid_worker
  ✅ test_list_shifts
  ✅ test_compute_topup_below_threshold
  ✅ test_compute_topup_meets_guarantee

---

📊 INCOME GUARANTEE FORMULA
============================

When worker logs a shift:
1. Log actual earnings
2. System calculates predicted earnings
3. Compare: actual vs. (predicted × 0.9)
4. If actual < threshold → pay top-up

Example:
  Predicted: $100 (pre-calculated from hour/day/location/demand)
  Actual: $80 (what worker actually earned)
  Threshold: $100 × 0.9 = $90
  Top-up: max(0, $90 - $80) = $10
  Total paid: $80 + $10 = $90

---

🚀 DEPLOYMENT STEPS
====================

1. Prerequisites
   ✅ PostgreSQL running (localhost:5432)
   ✅ .env configured with DATABASE_URL
   ✅ Python 3.10+ with venv activated

2. Setup Database
   alembic revision --autogenerate -m "Initial schema"
   alembic upgrade head

3. Run Tests
   python -m pytest tests/ -v

4. Seed Data (optional)
   python scripts/seed_data.py

5. Start Server
   python -m uvicorn src.main:app --reload

6. Verify
   curl http://localhost:8000/health
   Open http://localhost:8000/docs in browser

---

📚 DOCUMENTATION REFERENCE
===========================

For detailed information, see:

QUICKSTART.md (section numbers for reference)
  1. Create Database Schema (Alembic)
  2. Seed Test Data
  3. Run Unit Tests
  4. Run Integration Tests
  5. Start API Server
  6. Explore the API
  7. Test REST Endpoints (curl examples)
  8. Check Logs
  9. Testing Workflow Summary
  10. Troubleshooting
  11. Project Structure

ARCHITECTURE.md
  - Layers explained (API, Services, ML, Database, Models, Schemas)
  - Data flow examples
  - Database schema reference
  - Testing strategy
  - Design decisions

PROJECT_COMPLETION_REPORT.md
  - Components checklist
  - Test results summary
  - File structure
  - Production readiness
  - Next steps

---

⚙️ TECH STACK
==============

Framework: FastAPI 0.115.0
Database: PostgreSQL + SQLAlchemy 2.0.36
Testing: pytest 8.3.4
Validation: Pydantic v2
Migrations: Alembic 1.11.1
Logging: python-json-logger (structured JSON)
Auth: python-jose + passlib (ready for JWT)

---

✨ HIGHLIGHTS
==============

✅ All tests passing (15/15)
✅ Production-ready code (type hints, docstrings, error handling)
✅ Comprehensive documentation (3 guides)
✅ Clean architecture (layered, DI, ORM)
✅ ML models implemented (earnings prediction, shift optimization)
✅ Income guarantee logic verified
✅ Zero numpy/external ML dependency (pure Python models)

---

👉 GET STARTED NOW

1. Run migrations:
   alembic revision --autogenerate -m "Initial schema"
   alembic upgrade head

2. Start server:
   python -m uvicorn src.main:app --reload

3. Visit: http://localhost:8000/docs

Questions? Check QUICKSTART.md or ARCHITECTURE.md
"""
