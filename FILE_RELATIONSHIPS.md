# Smart Shift Planner - File Relationships & Dependencies

## Quick Reference: What Each File Does

### 🚀 Entry Point
- **`src/main.py`** - Starts the FastAPI application → imports all routers

---

## Detailed File Relationships

### LAYER 1: HTTP Requests → Endpoints

#### `api/v1/endpoints/workers.py`
```
Purpose: Handle worker CRUD operations
├── IMPORTS:
│   ├── from src.models import Worker          [gets Worker ORM]
│   ├── from src.schemas import WorkerCreate, WorkerRead  [validates requests]
│   └── from src.database import get_db        [gets DB session]
├── FUNCTIONS:
│   ├── create_worker_endpoint()  →  creates new worker record
│   └── list_workers_endpoint()   →  fetches all workers
└── FLOW: Request → Validate (schema) → Query DB (model) → Response (schema)
```

#### `api/v1/endpoints/shifts.py`
```
Purpose: Handle shift CRUD and income guarantee
├── IMPORTS:
│   ├── from src.models import Worker, Shift  [gets ORM models]
│   ├── from src.schemas import ShiftCreate, ShiftRead  [validates]
│   ├── from src.services.shifts import create_shift, compute_topup  [business logic]
│   ├── from src.database import get_db  [DB session]
│   └── from src.core.config import settings  [gets GUARANTEE_THRESHOLD]
├── FUNCTIONS:
│   ├── create_shift_endpoint()      → validates worker, creates shift via service
│   ├── list_shifts_endpoint()       → fetches shifts with pagination
│   └── shift_topup()               → calls compute_topup from service
└── FLOW: Request → Service layer → Model → Response
```

#### `api/v1/endpoints/predictions.py`
```
Purpose: ML prediction endpoints
├── IMPORTS:
│   └── from src.ml.predictors import EarningsPredictor, DemandForecaster, ShiftOptimizer
├── FUNCTIONS:
│   ├── predict_earnings()       → calls EarningsPredictor
│   ├── forecast_demand()        → calls DemandForecaster
│   └── recommend_shifts()       → calls ShiftOptimizer
└── FLOW: Query params → ML model → Predictions → JSON response
```

---

### LAYER 2: Schemas (Request/Response Validation)

#### `schemas/__init__.py`
```
Purpose: Pydantic models for data validation
├── WorkerCreate
│   ├── Used by: endpoints/workers.py (POST input)
│   └── Fields: name, email
├── WorkerRead
│   ├── Used by: endpoints/workers.py (GET response)
│   └── Converts: Worker ORM → JSON
├── ShiftCreate
│   ├── Used by: endpoints/shifts.py (POST input)
│   └── Fields: worker_id, start_time, end_time, earnings, predicted_earnings
└── ShiftRead
    ├── Used by: endpoints/shifts.py (GET response)
    └── Converts: Shift ORM → JSON

RELATIONSHIP:
WorkerCreate → validates request → WorkerCreate object →
  endpoint function → creates Worker model → returns Worker model →
  WorkerRead → formats → JSON response
```

---

### LAYER 3: ORM Models (Database)

#### `models/worker.py`
```
Purpose: Database schema for workers table
├── Class: Worker(Base)
│   ├── id: int (primary key)
│   ├── name: str
│   ├── email: str (unique)
│   ├── created_at: datetime
│   └── shifts: relationship([Shift])  ← links to shifts table
├── USED BY:
│   ├── endpoints/workers.py → db.query(Worker)
│   ├── endpoints/shifts.py → check if worker exists
│   ├── schemas → WorkerRead uses this model
│   └── database/__init__.py → Base class definition
└── IMPORTS FROM: database/__init__.py (gets Base, engine)
```

#### `models/shift.py`
```
Purpose: Database schema for shifts table
├── Class: Shift(Base)
│   ├── id: int (primary key)
│   ├── worker_id: int (foreign key → workers.id)
│   ├── start_time: datetime
│   ├── end_time: datetime
│   ├── earnings: float (actual)
│   ├── predicted_earnings: float (ML prediction)
│   ├── created_at: datetime
│   └── worker: relationship(Worker)  ← links to workers table
├── USED BY:
│   ├── endpoints/shifts.py → db.query(Shift)
│   ├── services/shifts.py → create and query Shift
│   ├── schemas → ShiftRead uses this model
│   └── database/__init__.py → Base class definition
└── IMPORTS FROM: database/__init__.py, models/worker.py
```

---

### LAYER 4: Business Logic (Services)

#### `services/shifts.py`
```
Purpose: Core business logic for shift operations
├── IMPORTS:
│   ├── from src.models import Shift         [gets ORM model]
│   ├── from sqlalchemy.orm import Session   [DB session type]
│   └── from datetime import datetime        [time operations]
├── FUNCTIONS:
│   ├── create_shift(db, worker_id, start_time, end_time, earnings, predicted_earnings)
│   │   └── Steps:
│   │       1. Creates Shift ORM object
│   │       2. db.add(shift)
│   │       3. db.commit() → writes to database
│   │       4. db.refresh(shift) → gets generated fields (id, created_at)
│   │       5. Returns Shift object
│   │
│   ├── list_shifts(db, skip, limit)
│   │   └── Returns query results with pagination
│   │
│   └── compute_topup(shift, threshold)
│       └── Calculates: max(0, predicted_earnings × threshold - actual_earnings)
│
├── USED BY: endpoints/shifts.py
└── CALLER FLOW: endpoint → service → model → database → return
```

---

### LAYER 5: Database Connection

#### `database/__init__.py`
```
Purpose: SQLAlchemy setup and session management
├── COMPONENTS:
│   ├── Base = declarative_base()
│   │   ├── Used by: models/worker.py, models/shift.py
│   │   └── Purpose: All ORM models inherit from Base
│   │
│   ├── engine = create_engine(DATABASE_URL)
│   │   ├── Connection to: PostgreSQL via pg8000
│   │   ├── URL from: config.DATABASE_URL
│   │   └── Configured with: echo=DEBUG (logging)
│   │
│   ├── SessionLocal = sessionmaker(bind=engine)
│   │   └── Factory for creating DB sessions
│   │
│   └── get_db() → Generator[Session]
│       ├── Used by: FastAPI Depends() in all endpoints
│       ├── Creates: request-scoped database session
│       ├── Yields: Session object to endpoint
│       └── Cleans up: session closes after request
│
├── IMPORTS FROM:
│   ├── config.DATABASE_URL (PostgreSQL connection string)
│   ├── sqlalchemy (ORM framework)
│   └── pg8000 (PostgreSQL driver - automatic via sqlalchemy)
│
└── DEPENDENCY CHAIN:
    main.py → endpoints → get_db() → SessionLocal() → engine → PostgreSQL
```

---

### LAYER 6: Configuration

#### `core/config.py`
```
Purpose: Centralized application settings
├── SETTINGS:
│   ├── DATABASE_URL = os.getenv("DATABASE_URL")
│   │   └── Used by: database/__init__.py
│   │
│   ├── ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
│   │   └── Used by: main.py (startup logging)
│   │
│   ├── DEBUG = os.getenv("DEBUG") == "True"
│   │   └── Used by: database/__init__.py (echo=DEBUG)
│   │
│   └── GUARANTEE_THRESHOLD = float(os.getenv("GUARANTEE_THRESHOLD", 0.9))
│       └── Used by: endpoints/shifts.py → compute_topup()
│
├── IMPORTS FROM: python-dotenv (loads .env file)
│
└── USED BY: database/__init__.py, endpoints/shifts.py, main.py
```

---

### LAYER 7: Machine Learning Models

#### `ml/predictors.py`
```
Purpose: Earnings predictions and recommendations
├── CLASS: EarningsPredictor
│   ├── Method: predict(hour, day_of_week, location, demand_level)
│   ├── Logic: Statistical estimation of earnings
│   └── Returns: float (predicted earnings)
│
├── CLASS: DemandForecaster
│   ├── Method: forecast(location, hours_ahead=24)
│   ├── Logic: Demand pattern analysis
│   └── Returns: dict with demand forecasts
│
└── CLASS: ShiftOptimizer
    ├── Method: recommend_shifts(location, date_type, duration_hours, top_n)
    ├── Logic: Optimal shift recommendations
    └── Returns: list of recommended shifts

USED BY: endpoints/predictions.py (directly instantiates and calls methods)
```

---

### LAYER 8: Application Entry Point

#### `main.py`
```
Purpose: Initialize and configure FastAPI application
├── IMPORTS:
│   ├── from fastapi import FastAPI, CORSMiddleware
│   ├── from src.api.v1.endpoints import workers, shifts, predictions
│   ├── from src.core.config import settings
│   └── from logging.config import dictConfig
│
├── INITIALIZATION:
│   ├── app = FastAPI(title="Smart Shift Planner")
│   ├── dictConfig(LOGGING_CONFIG) → setup logging
│   └── app.add_middleware(CORSMiddleware) → enable CORS
│
├── ROUTER REGISTRATION:
│   ├── app.include_router(workers.router)
│   ├── app.include_router(shifts.router)
│   └── app.include_router(predictions.router)
│
├── EVENT HANDLERS:
│   ├── @app.on_event("startup") → logs startup
│   └── @app.on_event("shutdown") → logs shutdown
│
└── EXECUTION:
    Command: uvicorn src.main:app --reload
    └── Starts FastAPI server on http://localhost:8000
```

---

## Complete Request-Response Flow (Example: Create Shift)

```
┌─────────────────────────────────────────────────────────────────┐
│ CLIENT REQUEST                                                  │
│ POST /api/v1/shifts/                                           │
│ {                                                               │
│   "worker_id": 2,                                              │
│   "start_time": "2026-02-12T08:00:00",                        │
│   "end_time": "2026-02-12T16:00:00",                          │
│   "earnings": 85.0,                                            │
│   "predicted_earnings": 95.0                                   │
│ }                                                               │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. SCHEMA VALIDATION                                            │
│    schemas/__init__.py::ShiftCreate                             │
│    ✓ Validates JSON structure                                   │
│    ✓ Checks data types                                          │
│    ✓ Validates email format (if present)                        │
│    ✓ Creates ShiftCreate object                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. ENDPOINT FUNCTION                                            │
│    api/v1/endpoints/shifts.py::create_shift_endpoint()         │
│    ├─ Gets payload: ShiftCreate (validated)                     │
│    ├─ Gets db: Session (from get_db dependency)                │
│    │  └─ database/__init__.py creates request-scoped session    │
│    └─ Executes endpoint logic                                   │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. WORKER VALIDATION                                            │
│    endpoint queries: db.query(Worker).filter(...)              │
│    ├─ models/worker.py::Worker (ORM model)                     │
│    ├─ Checks: does worker_id=2 exist?                          │
│    └─ If not: HTTPException(404)                               │
│    If yes: continues                                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. BUSINESS LOGIC (Service Layer)                              │
│    services/shifts.py::create_shift()                          │
│    ├─ Input: worker_id, start_time, end_time, earnings, etc.  │
│    ├─ Creates: Shift ORM object                                │
│    │  └─ shift = Shift(db_fields...)                           │
│    ├─ Saves: db.add(shift)                                     │
│    ├─ Commits: db.commit()                                     │
│    │  └─ Sends SQL INSERT to PostgreSQL                        │
│    ├─ Refreshes: db.refresh(shift)                             │
│    │  └─ Gets generated id and created_at from database        │
│    └─ Returns: shift (Shift ORM object)                        │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. DATABASE LAYER (PostgreSQL)                                 │
│    database/__init__.py                                         │
│    ├─ engine (SQLAlchemy engine)                               │
│    │  └─ connection: postgresql://localhost:5432/gigeconomy    │
│    ├─ Driver: pg8000 (Python PostgreSQL adapter)               │
│    ├─ SQL: INSERT INTO shifts (worker_id, ...) VALUES (...)   │
│    └─ Returns: new shift record with generated id              │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. RESPONSE SCHEMA                                              │
│    schemas/__init__.py::ShiftRead                              │
│    ├─ Takes: Shift ORM object from service                     │
│    ├─ Converts: ORM → JSON-serializable dict                   │
│    │  (using model_config ConfigDict(from_attributes=True))    │
│    └─ Includes: id, worker_id, start_time, end_time, etc.     │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. HTTP RESPONSE                                                │
│    main.py (FastAPI routing)                                   │
│    Status: 201 Created                                          │
│    Body:                                                        │
│    {                                                            │
│      "id": 5,                                                  │
│      "worker_id": 2,                                            │
│      "start_time": "2026-02-12T08:00:00",                      │
│      "end_time": "2026-02-12T16:00:00",                        │
│      "earnings": 85.0,                                          │
│      "predicted_earnings": 95.0,                                │
│      "created_at": "2026-02-12T09:30:45.123456"                │
│    }                                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Import Chain (Dependency Hierarchy)

```
main.py
├── imports → api/v1/endpoints/workers.py
│   ├── imports → models/worker.py
│   ├── imports → schemas/__init__.py
│   └── imports → database/__init__.py
│       ├── imports → core/config.py
│       └── imports → models (Base)
│
├── imports → api/v1/endpoints/shifts.py
│   ├── imports → models/shift.py
│   ├── imports → models/worker.py
│   ├── imports → services/shifts.py
│   │   └── imports → models/shift.py
│   ├── imports → schemas/__init__.py
│   ├── imports → database/__init__.py
│   └── imports → core/config.py
│
└── imports → api/v1/endpoints/predictions.py
    └── imports → ml/predictors.py
```

---

## Testing File Relationships

```
tests/
├── conftest.py
│   ├── Provides: test database fixture
│   ├── Provides: test client fixture
│   └── Used by: all test files
│
├── unit/test_basic.py
│   ├── Tests: core functions (no DB calls)
│   └── Uses: pytest
│
└── integration/
    ├── test_workers_shifts.py
    │   ├── Tests: endpoint functions
    │   ├── Uses: test database from conftest
    │   ├── Imports: FastAPI TestClient, test fixtures
    │   └── Calls: API endpoints (POST, GET)
    │
    └── test_predictions.py
        ├── Tests: ML prediction endpoints
        ├── Uses: test fixtures
        └── Verifies: prediction output format
```

---

## Summary: The "Layers" of the Application

| Layer | Files | Purpose | Dependencies |
|-------|-------|---------|---|
| **HTTP** | `main.py` | Start server, register routes | FastAPI, uvicorn |
| **Endpoints** | `api/v1/endpoints/*.py` | Handle requests | schemas, models, services, config |
| **Schemas** | `schemas/__init__.py` | Validate requests/responses | Pydantic |
| **Services** | `services/shifts.py` | Business logic | models, database |
| **Models** | `models/*.py` | Database schema | SQLAlchemy |
| **Database** | `database/__init__.py` | Connection pool | SQLAlchemy, pg8000 |
| **Config** | `core/config.py` | Settings management | python-dotenv |
| **ML** | `ml/predictors.py` | ML predictions | (no external libs) |

Each layer only imports from layers below it (no circular imports).

---

## Recommended Reading Order

1. **`INSTALLATION_GUIDE.md`** - How to set up locally
2. **`PROJECT_STRUCTURE.md`** - What each directory contains
3. **`FILE_RELATIONSHIPS.md`** (this file) - How files interact
4. **API Docs** - http://localhost:8000/docs (interactive examples)
5. **Backend Code** - Review actual files in order: config → database → models → schemas → services → endpoints
