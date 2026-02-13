# Smart Shift Planner - Database Schema & Data Map

## 📚 Complete Database Overview

### Database File Location
```
backend/smart_shift_planner.db
```

### Total Tables: 8

---

## 🗂️ Detailed Table Schema with Sample Data

### Table 1: `users`
**Purpose:** Store all user accounts (admin, drivers)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    full_name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    role VARCHAR NOT NULL,  -- 'admin' or 'driver'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Sample Data (2 records):**
| id | full_name | email | role | is_active | created_at |
|----|-----------|-------|------|-----------|-----------|
| 1 | Admin User | mykendoche@gmail.com | admin | true | 2026-02-13 |
| 2 | Demo Driver | driver@example.com | driver | true | 2026-02-13 |

**Plus 5-10 synthetic workers:**
| 3 | John Doe | john@example.com | driver | true | 2026-02-13 |
| 4 | Jane Smith | jane@example.com | driver | true | 2026-02-13 |
| ... (more workers) | ... | ... | driver | true | ... |

**Total Records:** ~12-15

---

### Table 2: `shifts`
**Purpose:** Store shift assignments and details

```sql
CREATE TABLE shifts (
    id INTEGER PRIMARY KEY,
    worker_id INTEGER FOREIGN KEY -> users(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR DEFAULT 'pending',  -- pending, completed, cancelled
    earnings FLOAT NOT NULL,
    predicted_earnings FLOAT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Sample Data (First 5 of 100+):**
| id | worker_id | start_time | end_time | status | earnings | predicted_earnings |
|----|-----------|-----------|----------|--------|----------|-------------------|
| 1 | 3 | 2026-02-08 08:00 | 2026-02-08 13:00 | completed | 95.00 | 100.00 |
| 2 | 3 | 2026-02-09 09:00 | 2026-02-09 14:00 | completed | 110.00 | 105.00 |
| 3 | 4 | 2026-02-08 10:00 | 2026-02-08 15:00 | completed | 85.00 | 95.00 |
| 4 | 4 | 2026-02-09 08:00 | 2026-02-09 13:00 | pending | 75.00 | 80.00 |
| ... | ... | ... | ... | ... | ... | ... |

**Total Records:** ~100-150

**Status Distribution:**
- Completed: ~70 records
- Pending: ~20 records
- Cancelled: ~10 records

---

### Table 3: `shift_details`
**Purpose:** Additional detailed information about shifts

```sql
CREATE TABLE shift_details (
    id INTEGER PRIMARY KEY,
    shift_id INTEGER FOREIGN KEY -> shifts(id),
    location VARCHAR,
    shift_type VARCHAR,  -- 'standard', 'premium', 'overtime'
    duration_hours FLOAT,
    hourly_rate FLOAT,
    customer_name VARCHAR,
    notes TEXT,
    created_at TIMESTAMP
)
```

**Sample Data (1 for each shift):**
| id | shift_id | location | shift_type | duration_hours | hourly_rate | customer_name |
|----|----------|----------|-----------|----------------|------------|---------------|
| 1 | 1 | Downtown | standard | 5.0 | 19.00 | ABC Corp |
| 2 | 2 | Uptown | premium | 5.0 | 22.00 | XYZ Inc |
| 3 | 3 | Downtown | standard | 5.0 | 17.00 | ABC Corp |
| ... | ... | ... | ... | ... | ... | ... |

**Total Records:** ~100-150 (1:1 with shifts)

---

### Table 4: `surveys`
**Purpose:** Store worker feedback/survey responses

```sql
CREATE TABLE surveys (
    id INTEGER PRIMARY KEY,
    worker_id INTEGER FOREIGN KEY -> users(id),
    question_id INTEGER FOREIGN KEY -> survey_questions(id),
    response_value INTEGER,  -- 1-5 rating
    response_text TEXT,  -- Open-ended feedback
    submitted_at TIMESTAMP,
    created_at TIMESTAMP
)
```

**Sample Data (30-50 records):**
| id | worker_id | question_id | response_value | response_text | submitted_at |
|----|-----------|-------------|----------------|--------------|--------------|
| 1 | 3 | 1 | 5 | Great shift! | 2026-02-12 15:30 |
| 2 | 3 | 2 | 4 | Good pay | 2026-02-12 15:30 |
| 3 | 4 | 1 | 3 | Average | 2026-02-12 16:45 |
| 4 | 4 | 2 | 2 | Low earnings | 2026-02-12 16:45 |
| ... | ... | ... | ... | ... | ... |

**Total Records:** ~30-50

---

### Table 5: `survey_questions`
**Purpose:** Store survey question templates

```sql
CREATE TABLE survey_questions (
    id INTEGER PRIMARY KEY,
    question_text VARCHAR NOT NULL,
    question_type VARCHAR,  -- 'rating', 'text'
    category VARCHAR,  -- 'earnings', 'safety', 'schedule', 'overall'
    order INTEGER,
    created_at TIMESTAMP
)
```

**Sample Data (Fixed questions):**
| id | question_text | question_type | category | order |
|----|---------------|---------------|----------|-------|
| 1 | How satisfied are you with this shift? | rating | overall | 1 |
| 2 | Was the pay fair? | rating | earnings | 2 |
| 3 | Did you feel safe during work? | rating | safety | 3 |
| 4 | Was the schedule flexible? | rating | schedule | 4 |
| 5 | Any additional feedback? | text | overall | 5 |

**Total Records:** 5-10 (Fixed template)

---

### Table 6: `eligibility_metrics`
**Purpose:** Store calculated eligibility scores for income guarantee

```sql
CREATE TABLE eligibility_metrics (
    id INTEGER PRIMARY KEY,
    worker_id INTEGER FOREIGN KEY -> users(id),
    total_shifts INTEGER,
    completed_shifts INTEGER,
    average_earnings FLOAT,
    earnings_volatility FLOAT,
    eligibility_score FLOAT,  -- 0-100
    meets_guarantee BOOLEAN,
    calculated_at TIMESTAMP,
    created_at TIMESTAMP
)
```

**Sample Data (1 per worker):**
| id | worker_id | total_shifts | completed_shifts | average_earnings | earnings_volatility | eligibility_score | meets_guarantee |
|----|-----------|--------------|-----------------|------------------|-------------------|------------------|-----------------|
| 1 | 3 | 15 | 14 | 102.5 | 12.3 | 87.5 | true |
| 2 | 4 | 12 | 10 | 82.3 | 18.5 | 65.0 | false |
| 3 | 5 | 10 | 9 | 95.0 | 8.2 | 91.0 | true |
| ... | ... | ... | ... | ... | ... | ... | ... |

**Total Records:** ~10-15 (1 per worker)

---

### Table 7: `worker_daily_summary`
**Purpose:** Aggregated daily earnings and statistics

```sql
CREATE TABLE worker_daily_summary (
    id INTEGER PRIMARY KEY,
    worker_id INTEGER FOREIGN KEY -> users(id),
    summary_date DATE NOT NULL,
    shifts_completed INTEGER,
    total_earnings FLOAT,
    total_hours FLOAT,
    average_earnings_per_shift FLOAT,
    created_at TIMESTAMP
)
```

**Sample Data (One per worker per day):**
| id | worker_id | summary_date | shifts_completed | total_earnings | total_hours | avg_earnings_per_shift |
|----|-----------|--------------|-----------------|----------------|-------------|----------------------|
| 1 | 3 | 2026-02-08 | 2 | 205.00 | 10.0 | 102.50 |
| 2 | 3 | 2026-02-09 | 1 | 110.00 | 5.0 | 110.00 |
| 3 | 4 | 2026-02-08 | 1 | 85.00 | 5.0 | 85.00 |
| 4 | 4 | 2026-02-09 | 2 | 155.00 | 9.0 | 77.50 |
| ... | ... | ... | ... | ... | ... | ... |

**Total Records:** ~100+ (Multiple entries per worker across days)

---

### Table 8: `ml_predictions`
**Purpose:** Store ML model predictions for eligibility and income forecasts

```sql
CREATE TABLE ml_predictions (
    id INTEGER PRIMARY KEY,
    worker_id INTEGER FOREIGN KEY -> users(id),
    prediction_type VARCHAR,  -- 'eligibility', 'income_forecast'
    predicted_value FLOAT,
    confidence_score FLOAT,  -- 0-1
    actual_value FLOAT,  -- Set after outcome known
    model_version VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Sample Data (Multiple predictions per worker):**
| id | worker_id | prediction_type | predicted_value | confidence_score | model_version |
|----|-----------|-----------------|-----------------|-----------------|---------------|
| 1 | 3 | income_forecast | 2500.00 | 0.87 | v1.0 |
| 2 | 3 | eligibility | 0.875 | 0.92 | v1.0 |
| 3 | 4 | income_forecast | 1800.00 | 0.72 | v1.0 |
| 4 | 4 | eligibility | 0.65 | 0.85 | v1.0 |
| ... | ... | ... | ... | ... | ... |

**Total Records:** ~20-30 (2-3 predictions per worker)

---

## 📊 Complete Data Summary

| Table | Purpose | Records | Source |
|-------|---------|---------|--------|
| users | Accounts | ~12-15 | Seed scripts |
| shifts | Shift records | ~100-150 | Seed scripts |
| shift_details | Shift details | ~100-150 | Seed scripts |
| surveys | Feedback | ~30-50 | Seed scripts + API |
| survey_questions | Survey template | 5-10 | Seed scripts |
| eligibility_metrics | Calculated scores | ~10-15 | ML service |
| worker_daily_summary | Daily totals | ~100+ | Batch processing |
| ml_predictions | ML outputs | ~20-30 | ML service |

**Total Records:** ~400-600 (Combined across all tables)

**Total Database Size:** ~2-5 MB

---

## 🔍 How to Query Each Table

### Check User Accounts
```sql
SELECT id, full_name, email, role FROM users;
```

### View All Shifts with Worker Info
```sql
SELECT s.id, u.full_name, s.start_time, s.earnings, s.status
FROM shifts s
JOIN users u ON s.worker_id = u.id
ORDER BY s.start_time DESC;
```

### Get Worker Eligibility
```sql
SELECT u.full_name, em.eligibility_score, em.meets_guarantee
FROM eligibility_metrics em
JOIN users u ON em.worker_id = u.id;
```

### Count Surveys by Worker
```sql
SELECT u.full_name, COUNT(s.id) as survey_count
FROM surveys s
JOIN users u ON s.worker_id = u.id
GROUP BY s.worker_id;
```

### Get Daily Earnings Totals
```sql
SELECT summary_date, SUM(total_earnings) as daily_total
FROM worker_daily_summary
GROUP BY summary_date
ORDER BY summary_date DESC;
```

---

## 🔑 Database Relationships

```
users
  ├─ shifts (1:Many)
  │  └─ shift_details (1:1)
  ├─ surveys (1:Many)
  ├─ eligibility_metrics (1:1)
  ├─ worker_daily_summary (1:Many)
  └─ ml_predictions (1:Many)

survey_questions
  └─ surveys (1:Many)
```

---

## 🔄 Data Flow Through System

```
seed_data.py → Database
     ↓
API Server reads from Database
     ↓
Frontend Dashboard displays data
     ↓
User interacts (submits survey, updates profile)
     ↓
Changes saved back to Database
     ↓
ML Service reads database
     ↓
Predictions saved to Database
     ↓
Frontend displays updated Analytics
```

---

## 📝 How to Recreate Data

```bash
# Option 1: Full reset
cd backend
rm smart_shift_planner.db  # Delete old database
python scripts/init_db.py  # Create new empty database
python scripts/seed_data.py  # Populate with fresh data
python scripts/seed_admin.py  # Create admin account

# Option 2: Keep database, just update seed data
python scripts/seed_data.py  # Will add new records if not duplicates
```

---

## ✅ Verification Checklist

To verify all data is properly seeded:

- [ ] Users table has 12-15 records
- [ ] Shifts table has 100+ records
- [ ] Surveys table has 30+ records
- [ ] Eligibility metrics calculated for each worker
- [ ] Daily summaries aggregated by date
- [ ] ML predictions exist for models
- [ ] Admin account can login
- [ ] Demo driver account can login
- [ ] Frontend dashboard loads all data
- [ ] API endpoints return data correctly

---

**For Your Lecturer:**

"All data is synthetic seed data generated from Python scripts in the `backend/scripts/` directory. It's stored in a SQLite database with 8 properly related tables. The system is fully functional with sample data for demonstration purposes."
