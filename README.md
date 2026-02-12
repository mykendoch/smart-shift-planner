# smart-shift-planner

**Status: ✅ COMPLETE** — Backend fully implemented with all 15 tests passing

Intelligent gig economy shift scheduling and income guarantee platform.

## 🎯 Project Overview

Smart Shift Planner helps gig economy workers (drivers, delivery workers, freelancers) 
make informed decisions about shifts with an **income guarantee safety net**.

**Key Features:**
- 📊 Predict shift earnings before accepting
- 💰 Guarantee workers earn ≥90% of predicted amount
- 🤖 ML-powered shift recommendations
- 📈 Track earnings and top-ups
- 🔍 Transparent income guarantee calculation

## 🚀 Quick Start

### 1. Set up database (first time only)
```bash
cd backend
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### 2. Start the API server
```bash
python -m uvicorn src.main:app --reload
```

### 3. Open interactive API documentation
```
http://localhost:8000/docs
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [backend/QUICKSTART.md](backend/QUICKSTART.md) | Step-by-step setup guide (11 sections) |
| [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md) | Detailed architecture and design |
| [backend/PROJECT_COMPLETION_REPORT.md](backend/PROJECT_COMPLETION_REPORT.md) | Full completion checklist |
| [backend/QUICK_REFERENCE.md](backend/QUICK_REFERENCE.md) | Command reference & cheat sheet |

## 🧪 Testing (All Passing)

```bash
# Run all tests (15 total)
python -m pytest tests/ -v

# Run only unit tests
python -m pytest tests/unit/ -v

# Run only integration tests
python -m pytest tests/integration/ -v
```

**Test Results:**
- ✅ 2 unit tests
- ✅ 8 worker/shift CRUD + income guarantee tests
- ✅ 5 ML prediction tests

## 🏗️ Architecture

```
FastAPI Application
    ↓
API Layer (endpoints/workers, shifts, predictions)
    ↓
Services Layer (business logic, income guarantee)
    ↓
Models Layer (SQLAlchemy ORM)
    ↓
PostgreSQL Database
```

## 🤖 ML Predictions

Three ML models for shift optimization:

1. **EarningsPredictor** - Predict hourly earnings
2. **DemandForecaster** - 24-hour demand patterns
3. **ShiftOptimizer** - Recommend best shifts

Formula: `earnings = base_rate × time_mult × day_mult × demand_mult`

Example: A $25/hour downtown shift at 6pm Friday with high demand = $33.60/hour

## 💡 Income Guarantee Mechanism

Workers are guaranteed to earn 90% of predicted earnings:

```
Example:
  Predicted: $100 (system calculates this)
  Actual: $80 (what worker earned)
  Guarantee: 90% × $100 = $90
  Top-up: max(0, $90 - $80) = $10
  Total paid: $80 + $10 = $90
```

## 📁 Project Structure

```
backend/
├── src/
│   ├── main.py                 # FastAPI app
│   ├── api/v1/endpoints/       # REST endpoints
│   ├── models/                 # SQLAlchemy ORM
│   ├── schemas/                # Pydantic validation
│   ├── services/               # Business logic
│   ├── ml/                      # ML models
│   ├── database/                # SQLAlchemy setup
│   └── core/                    # Configuration
├── tests/                       # 15 passing tests
├── scripts/                     # Utilities (seed, init)
├── alembic/                     # Database migrations
└── [Documentation files]
```

## 🔌 API Endpoints

### Workers
- `POST /api/v1/workers` - Create worker
- `GET /api/v1/workers` - List all workers

### Shifts
- `POST /api/v1/shifts` - Log completed shift
- `GET /api/v1/shifts` - List all shifts
- `GET /api/v1/shifts/{id}/topup` - Get income guarantee top-up

### Predictions (ML)
- `GET /api/v1/predictions/earnings` - Predict hourly earnings
- `GET /api/v1/predictions/demand-forecast` - 24-hour demand pattern
- `GET /api/v1/predictions/recommend-shifts` - Best shifts by earnings

## 💻 Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.115.0 |
| Server | Uvicorn 0.32.1 |
| Database | PostgreSQL + pg8000 |
| ORM | SQLAlchemy 2.0.36 |
| Validation | Pydantic v2 |
| Migrations | Alembic 1.11.1 |
| Testing | pytest 8.3.4 |
| Logging | python-json-logger |

## 🛠️ Configuration

Environment variables (`.env`):
```
DATABASE_URL=postgresql+pg8000://postgres:password@localhost:5432/gigeconomy
SECRET_KEY=your-secret-key
GUARANTEE_THRESHOLD=0.9
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "relation \"workers\" does not exist" | Run `alembic upgrade head` |
| "Port 8000 already in use" | Use `--port 8001` |
| "Connection refused" | Start PostgreSQL server |
| "ModuleNotFoundError" | Ensure you're in `backend/` directory |

See [backend/QUICKSTART.md](backend/QUICKSTART.md#10-troubleshooting) for more.

## 📊 Project Status

✅ **Completed:**
- Core API endpoints (workers, shifts)
- ML prediction models (3 classes)
- Income guarantee logic
- Database schema (Alembic ready)
- Comprehensive tests (15/15 passing)
- Full documentation
- Deployment checklist

⏳ **Future:** User authentication, payment processing, advanced ML, analytics dashboard

## 📖 Getting Started

1. **Read:** [backend/QUICKSTART.md](backend/QUICKSTART.md)
2. **Understand:** [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md)
3. **Reference:** [backend/QUICK_REFERENCE.md](backend/QUICK_REFERENCE.md)
4. **Deploy:** See Deployment section in QUICKSTART.md

## 🎓 Academic Notes

This is a research project exploring income stability mechanisms for gig economy workers.
The income guarantee threshold (90%) balances platform sustainability with worker support.

## 📝 License

Educational/Research project. See LICENSE file for details.

## 👥 Contributing

Fork, create feature branch, submit pull request.

All code must:
- Pass 15 tests (`pytest tests/ -v`)
- Follow type hints conventions
- Include docstrings
- Work with PostgreSQL
