# Smart Shift Planner - Project Structure & Architecture

## Project Overview

Smart Shift Planner is a FastAPI-based backend system that helps gig economy workers optimize shift scheduling and provides income guarantee calculations. The project uses PostgreSQL for data storage and includes ML prediction capabilities.

---

## Directory Structure

```
smart-shift-planner/
├── backend/                           # Backend API application
│   ├── src/                          # Source code (main application)
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── api/                      # API endpoints
│   │   │   └── v1/
│   │   │       └── endpoints/        # Endpoint controllers
│   │   ├── models/                   # Database ORM models
│   │   ├── schemas/                  # Pydantic validation schemas
│   │   ├── services/                 # Business logic layer
│   │   ├── ml/                       # Machine learning models
│   │   ├── core/                     # Configuration and constants
│   │   └── database/                 # Database connection setup
│   ├── tests/                        # Automated tests
│   │   ├── unit/                     # Unit tests
│   │   └── integration/              # Integration tests
│   ├── scripts/                      # Utility scripts
│   ├── alembic/                      # Database migrations
│   ├── requirements.txt              # Python dependencies
│   └── debug_db.py                   # Database connection tester
├── frontend/                          # (Future) Frontend application
├── ml_models/                         # Trained model files storage
├── data/                              # Raw and processed data files
├── docs/                              # Documentation files
└── README.md                          # Project overview
```

---

## Backend Directory Details

### `/backend/src/` - Main Application Source Code

#### **`main.py`** - Application Entry Point
- **Purpose**: Initializes and configures the FastAPI application
- **Responsibilities**:
  - Create FastAPI app instance
  - Configure CORS (Cross-Origin Resource Sharing)
  - Register API routers
  - Setup logging and error handlers
  - Define startup/shutdown events
- **Dependencies**: FastAPI, uvicorn, all routers
- **Key Functions**: Creates `app` object used by Uvicorn

---

### `/backend/src/api/v1/endpoints/` - API Endpoints

#### **`workers.py`** - Worker Management Endpoints
- **Purpose**: Handle worker creation, retrieval, and updates
- **Endpoints**:
  - `POST /api/v1/workers/` - Create new worker
  - `GET /api/v1/workers/` - List all workers
- **Dependencies**: 
  - SQLAlchemy (database access)
  - Pydantic (validation)
  - `src.models.Worker` (ORM model)
  - `src.schemas` (WorkerCreate, WorkerRead)
  - `src.services` (business logic)
- **Request/Response**: Validates input with Pydantic schemas

#### **`shifts.py`** - Shift Management Endpoints
- **Purpose**: Handle shift scheduling and income guarantee calculations
- **Endpoints**:
  - `POST /api/v1/shifts/` - Create shift record
  - `GET /api/v1/shifts/` - List shifts with filters
  - `GET /api/v1/shifts/{id}/topup` - Calculate income guarantee
- **Dependencies**:
  - `src.models.Shift` (ORM)
  - `src.services.shifts` (create_shift, compute_topup)
  - `src.core.config` (GUARANTEE_THRESHOLD)
- **Business Logic**: Validates worker exists, calculates topup

#### **`predictions.py`** - ML Prediction Endpoints
- **Purpose**: Provide earnings predictions and shift recommendations
- **Endpoints**:
  - `GET /api/v1/predictions/earnings` - Predict hourly earnings
  - `GET /api/v1/predictions/demand-forecast` - Forecast demand levels
  - `GET /api/v1/predictions/recommend-shifts` - Get optimal shifts
- **Dependencies**: `src.ml.predictors` (ML models)
- **Query Parameters**: Location, time, demand level, etc.

---

### `/backend/src/models/` - Database ORM Models

#### **`worker.py`** - Worker Database Model
- **Purpose**: Define database schema for workers
- **Fields**:
  - `id`: Primary key
  - `name`: Worker name
  - `email`: Unique email identifier
  - `created_at`: Timestamp
- **Relationships**: One-to-many with Shifts
- **Constraints**: Email must be unique
- **ORM**: SQLAlchemy declarative model
- **Direct Dependency**: From `src.models import Worker`

#### **`shift.py`** - Shift Database Model
- **Purpose**: Define database schema for work shifts
- **Fields**:
  - `id`: Primary key
  - `worker_id`: Foreign key to Worker
  - `start_time`: Shift start datetime
  - `end_time`: Shift end datetime
  - `earnings`: Actual earnings
  - `predicted_earnings`: ML-predicted earnings
  - `created_at`: Timestamp
- **Relationships**: Many-to-one with Worker
- **Constraints**: worker_id must exist in workers table
- **Direct Dependency**: From `src.models import Shift`

---

### `/backend/src/schemas/` - Pydantic Validation

#### **`__init__.py`** - Request/Response Schemas
- **Purpose**: Validate incoming requests and format responses
- **Classes**:
  - `WorkerCreate` - Validates worker POST requests (name, email)
  - `WorkerRead` - Formats worker responses (includes id, created_at)
  - `ShiftCreate` - Validates shift POST requests
  - `ShiftRead` - Formats shift responses
- **Configuration**: Pydantic ConfigDict with `from_attributes=True`
- **Usage**: FastAPI uses these for automatic validation and documentation
- **Dependencies**: Pydantic v2, email-validator

---

### `/backend/src/services/` - Business Logic Layer

#### **`shifts.py`** - Shift Service Functions
- **Purpose**: Contain core business logic for shift operations
- **Functions**:
  - `create_shift()` - Create and persist shift record
  - `list_shifts()` - Query shifts with pagination
  - `compute_topup()` - Calculate income guarantee (max(0, predicted×0.9 - actual))
- **Database Access**: Uses SQLAlchemy Session
- **Dependencies**: 
  - `src.models.Shift` (ORM)
  - `src.database` (Session management)
- **Logic Layer**: Separates business logic from endpoint code

---

### `/backend/src/ml/` - Machine Learning Models

#### **`predictors.py`** - ML Prediction Classes
- **Purpose**: Provide earnings prediction and optimization algorithms
- **Classes**:
  - `EarningsPredictor` - Predicts hourly earnings based on factors
  - `DemandForecaster` - Forecasts demand levels by location/time
  - `ShiftOptimizer` - Recommends optimal shifts
- **No Dependencies on pandas/numpy**: Pure Python implementation
- **Algorithms**: Statistical models and heuristics
- **Integration**: Called by endpoints in `predictions.py`

---

### `/backend/src/core/` - Configuration

#### **`config.py`** - Application Settings
- **Purpose**: Centralized configuration management
- **Variables**:
  - `DATABASE_URL` - PostgreSQL connection string
  - `GUARANTEE_THRESHOLD` - Income guarantee factor (0.9 = 90%)
  - `ENVIRONMENT` - Dev/production mode
  - `DEBUG` - Debug logging enabled/disabled
- **Source**: Reads from `.env` file via python-dotenv
- **Usage**: Imported across application for consistent settings

---

### `/backend/src/database/` - Database Setup

#### **`__init__.py`** - Database Connection & Session
- **Purpose**: Initialize database connection and session factory
- **Components**:
  - `engine` - SQLAlchemy engine for PostgreSQL
  - `SessionLocal` - Session factory for database sessions
  - `Base` - Declarative base for all models
  - `get_db()` - Dependency function for FastAPI
- **Connection**: Uses `DATABASE_URL` from config
- **ORM Setup**: Base imported by models for table definitions
- **Session Management**: FastAPI dependency for request-scoped sessions

---

### `/backend/tests/` - Automated Testing

#### **`conftest.py`** - Pytest Configuration
- **Purpose**: Share test fixtures and configuration
- **Fixtures** (reusable test data):
  - Database connections
  - Test client
  - Sample test data
- **Scope**: Used by all test files

#### **`unit/test_basic.py`** - Unit Tests
- **Purpose**: Test individual functions in isolation
- **Tests**: Worker creation, shift creation, validation
- **No Database**: Uses mocks where needed
- **Execution**: `pytest tests/unit/ -v`

#### **`integration/test_workers_shifts.py`** - Integration Tests
- **Purpose**: Test API endpoints with real database
- **Tests**: Full request/response cycles
- **Database**: Uses test database connection
- **Execution**: `pytest tests/integration/ -v`

#### **`integration/test_predictions.py`** - ML Testing
- **Purpose**: Test ML prediction endpoints
- **Tests**: Earnings predictions, demand forecasts
- **Execution**: `pytest tests/integration/test_predictions.py -v`

---

### `/backend/scripts/` - Utility Scripts

#### **`init_db.py`** - Database Initialization
- **Purpose**: Create tables and schema on fresh setup
- **Usage**: `python scripts/init_db.py`

#### **`seed_data.py`** - Sample Data Population
- **Purpose**: Insert test workers and shifts for development
- **Usage**: `python scripts/seed_data.py`

#### **`check_nulls.py`** - Data Quality Check
- **Purpose**: Find null values in database
- **Usage**: `python scripts/check_nulls.py`

---

### `/backend/alembic/` - Database Migrations

#### **`versions/` Directory** - Migration Files
- **Purpose**: Version control for database schema changes
- **File**: `e6f6ba83c2dc_initial_schema.py` - Creates workers and shifts tables
- **Execution**: `alembic upgrade head`
- **Rollback**: `alembic downgrade -1`

#### **`env.py`** - Migration Configuration
- **Purpose**: Configure Alembic environment and logging

#### **`script.py.mako`** - Migration Template
- **Purpose**: Template for generating new migrations

---

## Dependency Graph

### Core Dependencies (Required)

```
fastapi                 → Creates REST API
  └─ APIRouter, HTTPException, etc.

uvicorn[standard]       → ASGI web server
  └─ Runs FastAPI app

sqlalchemy==2.0.36      → ORM for database
  ├─ src/models/*       → Defines tables
  ├─ src/database/*     → Database connection
  └─ src/services/*     → Database queries

pg8000==1.31.2          → PostgreSQL adapter
  └─ sqlalchemy         → Connects to PostgreSQL

pydantic-settings       → Config from .env
python-dotenv==1.0.1    → Load .env file

email-validator==2.3.0  → Validate email fields
  └─ WorkerCreate schema
```

### Testing Dependencies

```
pytest==8.3.4           → Test framework
httpx==0.27.2          → HTTP client for testing
```

### Logging & Monitoring

```
python-json-logger      → Structured logging
```

### Security Dependencies (Future)

```
python-jose[crypto]     → JWT tokens
passlib[bcrypt]        → Password hashing
```

---

## Data Flow

### Request → Response Flow (Example: Create Shift)

```
1. Client Request (JSON)
   ↓
2. FastAPI receives at POST /api/v1/shifts/
   ↓
3. Pydantic schema (ShiftCreate) validates JSON
   ↓
4. Endpoint function (shifts.py) receives validated data
   ↓
5. Endpoint queries Worker model to verify worker_id exists
   ↓
6. Service layer (services/shifts.py) creates Shift record via SQLAlchemy
   ↓
7. SQLAlchemy ORM generates SQL and sends to PostgreSQL via pg8000
   ↓
8. Database returns new Shift record
   ↓
9. Pydantic schema (ShiftRead) formats response
   ↓
10. FastAPI returns JSON response (201 Created)
```

---

## Environment Configuration

### Required `.env` Variables

```env
# Database (PostgreSQL)
DATABASE_URL=postgresql://postgres:Ndoch@localhost:5432/gigeconomy

# Application
ENVIRONMENT=development
DEBUG=True
GUARANTEE_THRESHOLD=0.9

# Security (JWT for future auth)
SECRET_KEY=your-secret-key
ALGORITHM=HS256
```

---

## How to Run Each Component

### Run Application
```bash
cd backend
uvicorn src.main:app --reload
```

### Run Tests
```bash
cd backend
pytest tests/ -v
```

### Database Migration
```bash
cd backend
alembic upgrade head
```

### Seed Test Data
```bash
cd backend
python scripts/seed_data.py
```

---

## File Dependencies Summary

| File | Depends On | Used By |
|------|-----------|---------|
| `main.py` | FastAPI, routers | Uvicorn (entry point) |
| `workers.py` | models, schemas, services | API client |
| `shifts.py` | models, schemas, services, config | API client |
| `predictions.py` | ml/predictors | API client |
| `worker.py` | sqlalchemy, database | services, schemas |
| `shift.py` | sqlalchemy, database, worker | services, schemas |
| `shifts.py` (service) | models, database | endpoints |
| `config.py` | python-dotenv | database, shifts |
| `database/__init__.py` | sqlalchemy, pg8000, config | models |
| `predictors.py` | (no external ML libs) | endpoints |

---

## Next Steps for Development

1. **Frontend**: Create React/Vue.js UI in `/frontend` directory
2. **Authentication**: Implement JWT in endpoints using python-jose
3. **Advanced ML**: Add pandas/numpy-based models when needed
4. **Deployment**: Use Dockerfile and Kubernetes for production
5. **Monitoring**: Add prometheus metrics and Grafana dashboards

See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for setup instructions.
