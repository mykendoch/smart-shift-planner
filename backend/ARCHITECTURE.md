"""
Smart Shift Planner - Backend Architecture Overview
====================================================

Project Goal:
  Build a gig economy platform that:
  - Tracks worker shifts and earnings
  - Predicts shift earnings using ML models
  - Guarantees minimum income (90% of predicted earnings)
  - Recommends optimal shifts for maximum returns
  - Stores all data in PostgreSQL with structured logging

---

ARCHITECTURE LAYERS
===================

1. API LAYER (src/api/v1/endpoints/)
   Purpose: HTTP request/response handling
   
   a) workers.py
      - POST   /api/v1/workers              Create new worker
      - GET    /api/v1/workers              List all workers
      Dependencies: FastAPI, Pydantic schemas, SQLAlchemy models
      
   b) shifts.py
      - POST   /api/v1/shifts               Log a completed shift
      - GET    /api/v1/shifts               List all shifts
      - GET    /api/v1/shifts/{id}/topup   Calculate income guarantee top-up
      Dependencies: Services layer, schemas
      
   c) predictions.py (NEW - ML)
      - GET    /api/v1/predictions/earnings             Predict hourly earnings
      - GET    /api/v1/predictions/demand-forecast      24-hour demand pattern
      - GET    /api/v1/predictions/recommend-shifts     Top N recommended shifts
      Dependencies: ML predictor classes, datetime

2. SERVICES LAYER (src/services/)
   Purpose: Business logic and domain rules
   
   shifts.py
   - compute_topup(shift, threshold=0.9)
     Calculate: max(0, predicted_earnings * threshold - actual_earnings)
     Example: If predicted=$100, actual=$80, threshold=0.9:
              topup = max(0, 100*0.9 - 80) = max(0, 10) = $10
   
   Dependencies: Models, logging

3. ML LAYER (src/ml/predictors.py - NEW)
   Purpose: Machine learning models for predictions
   
   a) EarningsPredictor
      - Method: Multiplier-based model
      - Formula: earnings = base_rate[location] × time_multiplier[hour] × 
                            day_multiplier[dow] × demand_multiplier[level]
      - Key rates:
        Base rates (hourly): downtown=$25, suburbs=$18, rural=$15
        Time multipliers: 9-5=$1.0, 5-9pm=$1.4, 9pm-9am=$0.8
        Day multipliers: weekday=$1.1, weekend=$1.3, Friday=$1.2
        Demand: 0.2× to 1.2× based on level (0.0-1.0)
      - Output: predicted_hourly_earnings for any time/location
      
   b) DemandForecaster
      - Method: Lookup-based hourly patterns
      - Patterns:
        Off-peak (midnight-7am): 0.2-0.3
        Morning (7am-9am): 0.5-0.7
        Midday (9am-5pm): 0.7-0.9
        Evening peak (5pm-9pm): 0.8-1.0
        Night (9pm-midnight): 0.4-0.6
      - Output: 24-hour demand profile, peak hours detection
      
   c) ShiftOptimizer
      - Method: Ranks shifts by predicted earnings
      - Input: location, date_type (weekday/weekend), duration, top_n
      - Scans all 24 hours, calculates earnings for each start time
      - Returns: Top N shifts sorted by predicted_earnings (highest first)
      - Example: For 4-hour shift downtown on Friday:
        Rank 1: 6pm-10pm = $120.0
        Rank 2: 5pm-9pm  = $116.0
        Rank 3: 7pm-11pm = $110.0
   
   Dependencies: datetime, logging, EarningsPredictor, DemandForecaster

4. DATABASE LAYER (src/database/)
   Purpose: PostgreSQL/SQLAlchemy ORM setup
   
   __init__.py
   - engine: SQLAlchemy engine (postgresql+pg8000://...)
   - SessionLocal: Session factory for request-scoped DB access
   - Base: Declarative base for ORM models
   - get_db(): FastAPI dependency for injecting DB session into endpoints
   
   Dependencies: SQLAlchemy, settings.DATABASE_URL

5. MODEL LAYER (src/models/)
   Purpose: ORM representations of database tables
   
   a) worker.py
      Table: workers
      Columns: id (PK), name, email (unique), created_at (auto-timestamp)
      Relationship: has many shifts (one-to-many)
      
   b) shift.py
      Table: shifts
      Columns: id (PK), worker_id (FK→workers.id), start_time, end_time,
               earnings (actual, float), predicted_earnings (float, nullable),
               created_at (auto-timestamp)
      Relationship: belongs_to worker
   
   Dependencies: SQLAlchemy declarative, datetime

6. SCHEMA LAYER (src/schemas/)
   Purpose: Pydantic request/response models for validation and serialization
   
   Classes:
   - WorkerCreate: name, email (validated, required)
   - WorkerRead: id, name, email, created_at (for GET responses)
   - ShiftCreate: worker_id, start_time, end_time, earnings (required)
   - ShiftRead: id, worker_id, start_time, end_time, earnings, predicted_earnings, created_at
   
   Configuration: ConfigDict(from_attributes=True) for SQLAlchemy ORM → Pydantic
   Validation: EmailStr for email uniqueness, positive earnings
   
   Dependencies: Pydantic, email-validator

7. CONFIG LAYER (src/core/)
   Purpose: Application settings from environment
   
   config.py
   - DATABASE_URL: PostgreSQL connection string
   - SECRET_KEY: For JWT tokens (auth)
   - ALGORITHM: "HS256" for JWT
   - ACCESS_TOKEN_EXPIRE_MINUTES: 30
   - GUARANTEE_THRESHOLD: 0.9 (90% of predicted earnings)
   - LOG_LEVEL: "INFO"
   - ENVIRONMENT: "development" / "production"
   
   Loading: From .env file via python-dotenv
   Pattern: Pydantic BaseSettings with ConfigDict
   
   Dependencies: pydantic-settings, dotenv

8. MAIN APPLICATION (src/main.py)
   Purpose: FastAPI app initialization and router aggregation
   
   Startup:
   - Log system information (Python version, OS, PostgreSQL connection)
   - Initialize logs/ directory
   - Attach CORS middleware (allow all origins in dev)
   - Mount all v1 routers (workers, shifts, predictions)
   
   Endpoints:
   - GET  /                  Project info and health summary
   - GET  /health           Health status (always 200)
   - GET  /api/v1/info      API version and available routes
   - /api/v1/workers        (workers.py routes)
   - /api/v1/shifts         (shifts.py routes)
   - /api/v1/predictions    (predictions.py routes - ML)
   
   Documentation:
   - GET  /docs             Swagger UI (interactive)
   - GET  /redoc            ReDoc (alternative API docs)
   - GET  /openapi.json     OpenAPI spec (raw)
   
   Dependencies: FastAPI, all routers

---

DATA FLOW EXAMPLES
==================

Example 1: Worker Creates & Logs Shift
--------------------------------------
  User (Mobile App)
    ↓
    POST /api/v1/shifts
    {
      "worker_id": 1,
      "start_time": "2024-12-15T17:00:00",
      "end_time": "2024-12-15T21:00:00",
      "earnings": 85.0
    }
    ↓
    [shifts.py endpoint]
    ↓
    [Shift model persists to PostgreSQL]
    ↓
    ✅ Response: {"id": 42, "worker_id": 1, "earnings": 85.0, ...}


Example 2: Check Income Guarantee Top-Up
-----------------------------------------
  Worker earned: $85
  Actual time: 4pm-8pm (evening peak)
  Location: downtown
  
  Frontend calculates predicted earnings:
  Predicted = 25 (base) × 1.4 (evening) × 1.2 (Friday) = $42/hour × 4 = $168
  
  GET /api/v1/shifts/42/topup
    ↓
    [shifts.py endpoint calls compute_topup()]
    ↓
    compute_topup(shift, threshold=0.9):
      topup = max(0, 168 × 0.9 - 85)
            = max(0, 151.2 - 85)
            = max(0, 66.2)
            = $66.2
    ↓
    ✅ Response: {"shift_id": 42, "topup": 66.2}
    
  Interpretation: Worker's income guaranteed to 90% of predicted.
                  Earned $85, but platform pays additional $66.20 → total $151.20.


Example 3: Get ML Predictions
------------------------------
  User wants to know the best shift tomorrow (Friday) in downtown area.
  
  Frontend calls:
  GET /api/v1/predictions/recommend-shifts?location=downtown&date_type=weekday&duration_hours=4&top_n=3
    ↓
    [predictions.py endpoint]
    ↓
    [ShiftOptimizer.recommend_shifts()]
      For each potential start hour (0-20):
        For each location/day:
          earnings = EarningsPredictor(hour, day_of_week, location, demand_level)
    
    Rankings (4-hour shifts):
      1. 6pm-10pm: base(25) × eve(1.4) × fri(1.2) × 4h = $336
      2. 5pm-9pm:  base(25) × eve(1.4) × fri(1.2) × 4h = $336
      3. 4pm-8pm:  base(25) × cross(~1.2) × fri(1.2) × 4h = ~$320
    
    (Actual calculation considers hourly variation within each 4-hour window)
    ↓
    ✅ Response: 
    {
      "recommendations": [
        {"start_hour": 18, "duration_hours": 4.0, "predicted_earnings": 336.0},
        {"start_hour": 17, "duration_hours": 4.0, "predicted_earnings": 320.0},
        {"start_hour": 19, "duration_hours": 4.0, "predicted_earnings": 310.0}
      ]
    }

---

DATABASE SCHEMA
===============

Table: workers
  Column          Type            Constraints
  ─────────────────────────────────────────────
  id              INTEGER         PRIMARY KEY, auto-increment
  name            VARCHAR(255)    NOT NULL
  email           VARCHAR(255)    UNIQUE, NOT NULL
  created_at      TIMESTAMP       DEFAULT NOW(), NOT NULL

Index: idx_workers_email (for quick lookups)


Table: shifts
  Column              Type            Constraints
  ─────────────────────────────────────────────────
  id                  INTEGER         PRIMARY KEY, auto-increment
  worker_id           INTEGER         FOREIGN KEY (workers.id), NOT NULL
  start_time          TIMESTAMP       NOT NULL
  end_time            TIMESTAMP       NOT NULL
  earnings            FLOAT           NOT NULL (actual earned)
  predicted_earnings  FLOAT           NULLABLE (ML prediction)
  created_at          TIMESTAMP       DEFAULT NOW(), NOT NULL

Index: idx_shifts_worker_id (for filtering by worker)
Check: end_time > start_time (ensure valid duration)

---

TESTING STRATEGY
================

1. UNIT TESTS (tests/unit/test_basic.py)
   - No database required
   - Fast execution (~100ms)
   - Check: Root endpoint, health check
   
2. INTEGRATION TESTS (tests/integration/)
   
   a) test_workers_shifts.py
      - Uses SQLAlchemy session with rollback for isolation
      - Tests: CRUD operations, foreign key validation, constraints
      - Coverage: Worker creation (duplicate check), shift creation, income guarantee
      
   b) test_predictions.py
      - Tests: ML prediction endpoints, demand forecasting
      - Validates: Peak hour earnings > off-peak, weekend > weekday
      - No DB dependency (ML models are pure functions)

3. FIXTURES (tests/conftest.py)
   - Pytest fixtures for consistent test setup
   - DB Session: Provides clean SQLAlchemy session per test
   - Client: TestClient with overridden dependency (uses test DB)
   - Sample Data: worker/shift fixtures for assertions

---

DEPLOYMENT CHECKLIST
====================

[ ] PostgreSQL running and accessible
[ ] .env file with correct DATABASE_URL
[ ] Alembic migrations created and applied (alembic upgrade head)
[ ] Database tables created (run init_db.py or Alembic)
[ ] All Python dependencies installed (pip install -r requirements.txt)
[ ] Run all tests pass (python -m pytest tests/ -v)
[ ] Start API server (python -m uvicorn src.main:app)
[ ] Verify endpoints in Swagger UI (http://localhost:8000/docs)
[ ] Review logs in logs/app.log for errors
[ ] Load test with seed data (python scripts/seed_data.py)

---

KEY DESIGN DECISIONS
====================

1. Multiplier-Based ML Model
   Why: Simple, interpretable, doesn't require training data.
   Instead of training on historical data, we use domain knowledge:
   - Location affects base rate
   - Time of day affects demand
   - Day of week affects demand
   Multiplying these gives reasonable earnings predictions.

2. 90% Income Guarantee Threshold
   Why: Balances platform sustainability with worker income stability.
   Too high (100%): Platform bears all risk, may not be viable.
   Too low (70%): Doesn't meaningfully help workers.
   90%: Reasonable safety net, incentivizes shift completion.

3. PostgreSQL + SQLAlchemy
   Why: Production-grade relational database with ORM for Python.
   Alternatives considered: MongoDB (unstructured), SQLite (single-file, limited concurrency).

4. FastAPI
   Why: Modern async Python framework with auto-generated OpenAPI docs.
   Benefits: Type hints, automatic validation, excellent performance.

5. Alembic for Migrations
   Why: Version control for database schema changes.
   Important for: Team collaboration, deployment consistency, rollback capability.

6. Structured JSON Logging
   Why: Machine-readable logs for production monitoring and debugging.
   Includes: timestamp, level, message, context.

---

FUTURE ENHANCEMENTS
====================

1. Authentication (JWT)
   - Endpoints to issue/verify tokens
   - Middleware to validate authorization headers

2. Advanced ML
   - Train models on historical data (earnings per hour/location/day)
   - Support vector machines (SVM) for shift recommendations
   - Neural networks for demand forecasting

3. Real-Time Updates
   - WebSockets for live shift availability
   - Push notifications for shift recommendations

4. Analytics Dashboard
   - Worker earnings trends over time
   - Platform-wide demand patterns
   - Top earning shifts/locations

5. Payment Integration
   - Stripe/PayPal for disbursing top-ups
   - Wallet management for workers

6. Mobile App
   - React Native/Flutter frontend
   - Push notifications
   - Offline shift logging

---

TROUBLESHOOTING REFERENCE
==========================

Q: "psycopg2.OperationalError: connection refused"
A: PostgreSQL not running. Start with: pg_ctl start -D /path/to/data

Q: "relation \\"workers\\" does not exist"
A: Migrations not applied. Run: alembic upgrade head

Q: "IntegrityError: duplicate key value violates unique constraint"
A: Email already exists. Delete worker or use new email.

Q: "SyntaxError: source code string cannot contain null bytes"
A: UTF-16 encoding in file. Recreate as UTF-8. (Already fixed in this codebase.)

Q: "ModuleNotFoundError: src"
A: Working directory wrong. cd to backend/ directory.

Q: "Permission denied: /logs/app.log"
A: logs/ directory not writable. Create with: mkdir -p logs && chmod 755 logs

Q: "AssertionError: <Response [404]> != <Response [200]>"
A: Endpoint not found. Check router mounting in src/main.py.

---

END OF ARCHITECTURE OVERVIEW
"""
