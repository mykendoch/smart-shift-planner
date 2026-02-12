# Smart Shift Planner - Installation Guide

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 2GB free space
- **PostgreSQL**: 12 or higher

### Required Software
- Git (for version control)
- PostgreSQL Database Server
- Python Package Manager (pip)

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/mykendoch/smart-shift-planner.git
cd smart-shift-planner
```

### 2. Set Up PostgreSQL Database

#### On Windows:
```bash
# Start PostgreSQL service (if not running)
# Open PostgreSQL command line as administrator
psql -U postgres

# Create database
CREATE DATABASE gigeconomy;

# Verify creation
\l
```

#### On macOS/Linux:
```bash
# Start PostgreSQL
brew services start postgresql  # macOS
sudo service postgresql start   # Ubuntu/Linux

# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE gigeconomy;
```

**Database Credentials** (default):
- Username: `postgres`
- Password: `Ndoch` (or configure your own)
- Host: `localhost`
- Port: `5432`
- Database: `gigeconomy`

### 3. Create Python Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### 4. Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### 5. Configure Environment Variables

Create `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:Ndoch@localhost:5432/gigeconomy

# Application Settings
ENVIRONMENT=development
DEBUG=True
GUARANTEE_THRESHOLD=0.9

# Security (for future JWT authentication)
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
```

### 6. Initialize Database Schema

```bash
# Run Alembic migrations
python -m alembic upgrade head

# Verify database tables were created
# Run debug script to check connection
python debug_db.py
```

### 7. Run the Application

```bash
# Start the Uvicorn server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 8. Access the Application

Open your browser and navigate to:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

---

## Running Tests

```bash
# Activate virtual environment first
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate      # Windows

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/unit/test_basic.py -v

# Run with coverage report
python -m pytest tests/ --cov=src
```

---

## Data Population

### Option 1: Manual Insertion via API

Use Swagger UI at http://localhost:8000/docs:

1. **Create Workers**: POST `/api/v1/workers/`
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com"
   }
   ```

2. **Create Shifts**: POST `/api/v1/shifts/`
   ```json
   {
     "worker_id": 1,
     "start_time": "2026-02-12T08:00:00",
     "end_time": "2026-02-12T16:00:00",
     "earnings": 85.50,
     "predicted_earnings": 95.00
   }
   ```

### Option 2: Automated Seed Script

```bash
# Run seed data script (if available)
python scripts/seed_data.py
```

---

## Troubleshooting

### Issue: PostgreSQL Connection Refused

**Cause**: PostgreSQL service not running or wrong credentials

**Solution**:
1. Verify PostgreSQL is running
2. Check DATABASE_URL in `.env` file
3. Verify database exists: `psql -U postgres -l`

### Issue: Port 8000 Already in Use

**Solution**:
```bash
# Use different port
uvicorn src.main:app --reload --port 8001
```

### Issue: Database Tables Not Found

**Solution**:
```bash
# Reset and recreate database
python debug_db.py
```

### Issue: ModuleNotFoundError

**Solution**:
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

---

## Production Deployment

### Before Deployment:
1. Set `ENVIRONMENT=production` in `.env`
2. Generate strong `SECRET_KEY`
3. Use strong database password
4. Disable `DEBUG=False`
5. Use production WSGI server (Gunicorn)

### Deploy with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 src.main:app
```

---

## Project Structure Reference

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed directory and file information.

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs (interactive Swagger UI)
- **Project Architecture**: See [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md)
- **Code Examples**: See [backend/QUICKSTART.md](backend/QUICKSTART.md)
