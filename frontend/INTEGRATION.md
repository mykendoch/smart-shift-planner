# Frontend-Backend Integration Guide

## Architecture Overview

```
┌─────────────────┐
│  Browser        │
│  (Next.js)      │
└────────┬────────┘
         │ HTTP/HTTPS
         │ JWT Token in Header
         │
┌────────▼────────────────────────┐
│  FastAPI Backend                │
│  (Python)                       │
│                                 │
│  ├── AuthService               │
│  ├── VolatilityAnalyzer        │
│  ├── AccuracyAnalyzer          │
│  ├── SurveyManager             │
│  └── EligibilityChecker        │
└────────┬────────────────────────┘
         │
┌────────▼────────────────────────┐
│  PostgreSQL Database            │
│  - User (with roles)            │
│  - WorkerEligibility            │
│  - VolatilityMetrics            │
│  - PredictionAccuracy           │
│  - WorkerSurvey                 │
└─────────────────────────────────┘
```

## Authentication Flow

```
1. User fills login form
   │
2. POST /api/v1/auth/login
   ├─ email: "driver@example.com"
   ├─ password: "password123"
   │
3. Backend verifies password with BCrypt
   │
4. Returns JWT token
   ├─ payload: {user_id, role, exp}
   │
5. Frontend stores in localStorage
   │
6. Get Authorization header for all future requests
   ├─ "Authorization: Bearer eyJhbGc..."

```

## API Calls with Token

Every request includes:
```
Authorization: Bearer <jwt_token>
```

Axios interceptor automatically adds this header (see `lib/api.ts`):

```typescript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## Feature Implementation Details

### 1. FR14: Income Volatility (Driver View)

**Frontend Flow**:
```
Driver → Dashboard → "Income Insights" Link
    ↓
Load VolatilityPage
    ↓
useVolatility(user.id, days=30)
    ↓
GET /api/v1/analytics/worker/{user.id}/volatility?days=30
    ↓
Backend calculates statistics (mean, std, CV, percentiles)
    ↓
Display charts and metrics
```

**Display Elements**:
- Volatility reduction percentage
- Statistical comparisons (with/without guarantee)
- Line and bar charts from Recharts
- 9-metric breakdown (mean, std, min, max, quartiles, IQR)

**Data Structure Received**:
```typescript
{
  without_guarantee: {
    mean: 125.00,
    std: 45.32,
    variance: 2053.90,
    cv: 36.26,  // Coefficient of variation
    min: 50.00,
    max: 250.00,
    q1: 95.00,
    median: 118.50,
    q3: 150.00,
    iqr: 55.00
  },
  with_guarantee: { /* similar */ },
  impact: {
    volatility_reduction_percent: 73.5
  }
}
```

### 2. NFR3: Model Accuracy (Admin View)

**Frontend Flow**:
```
Admin → Dashboard → "Model Performance" Link
    ↓
Load AccuracyPage
    ↓
useAccuracy()
    ↓
GET /api/v1/models/accuracy/summary?location=...&hour=...
    ↓
Backend provides MAPE/MAE/RMSE/R² metrics
    ↓
Display with compliance status
```

**Compliance Thresholds**:
```
MAPE ≤ 10% → Excellent
MAPE ≤ 15% → Good
MAPE ≤ 20% → Acceptable  ← Specification target
MAPE > 20%  → Poor
```

**Data Structure Received**:
```typescript
{
  overall: {
    mape: 18.5,      // Mean Absolute Percentage Error
    mae: 42.10,      // Mean Absolute Error
    rmse: 58.75,     // Root Mean Squared Error
    r2: 0.88,        // R² Score
    accuracy_level: "Acceptable"
  },
  by_location: [
    { location: "downtown", mape: 16.2, r2: 0.89 },
    { location: "airport", mape: 20.1, r2: 0.85 }
  ],
  by_hour: [
    { hour: "6am", mape: 15.5 },
    { hour: "9am", mape: 14.2 }
  ]
}
```

### 3. FR16: Survey Feedback (Driver Submission → Admin Aggregation)

**Driver Submission Flow**:
```
Driver → Dashboard → "Feedback" Link
    ↓
SurveysPage shows 6 Likert questions
    ↓
User selects 1-5 for each question:
  - Income stress level
  - Schedule satisfaction
  - App usefulness
  - Decision-making improvement
  - Shift planning ease
  - Earnings stability
    ↓
POST /api/v1/surveys/submit
{
  income_stress_level: 4,
  schedule_satisfaction: 3,
  app_usefulness: 5,
  decision_making_improvement: 4,
  shift_planning_ease: 4,
  earnings_stability: 4,
  feedback: "Works great!"
}
    ↓
Backend stores in WorkerSurvey table (with timestamp)
    ↓
Show success message
```

**Admin Aggregation Flow**:
```
Admin → Dashboard → "Survey Reports" Link
    ↓
GET /api/v1/surveys/aggregate-report
    ↓
Backend calculates averages:
{
  income_stress: { avg: 3.2, interpretation: "Moderate" },
  schedule_satisfaction: { avg: 3.8, ... },
  app_usefulness: { avg: 4.1, ... },
  decision_making: { avg: 3.9, ... },
  shift_planning: { avg: 4.0, ... },
  earnings_stability: { avg: 4.2, ... },
  feedback_themes: [
    "Income more predictable",
    "Need better notifications",
    "Calendar integration request"
  ]
}
    ↓
Display star ratings and themes
```

**Research Export**:
```
Admin → "Export Anonymized Data" Button
    ↓
GET /api/v1/surveys/export-anonymized
    ↓
Backend hashes worker IDs with SHA-256
    ↓
Returns downloadable CSV:
worker_id_hashed, response_date, income_stress, ..., feedback
abc123def456,     2024-01-15,    4,            ..., "Great app!"
```

### 4. FR9: Eligibility Management (Enforcement)

**Driver Eligibility Check**:
```
Driver → Dashboard → "Eligibility" Link
    ↓
GET /api/v1/eligibility/worker/{user.id}
    ↓
Backend checks 4 criteria:
  ✓ Active hours/week ≥ 20
  ✓ Acceptance rate ≥ 95%
  ✓ Cancellation rate ≤ 5%
  ✓ Average rating ≥ 4.0
    ↓
Display status cards (✓/✗) for each criteria
    ↓
Show overall eligibility: Eligible or Not Eligible
```

**Admin Eligibility Management**:
```
Admin → "Workers" → Select Worker → "Suspend Eligibility"
    ↓
POST /api/v1/eligibility/worker/{worker_id}/suspend
    ↓
Backend sets worker status = "suspended"
    ↓
Next guarantee shift request returns 403 Forbidden

Later: POST /api/v1/eligibility/worker/{worker_id}/reactivate
    ↓
Status = "active", access restored
```

**Data Structure Received**:
```typescript
{
  worker_id: "1",
  is_eligible: true,
  status: "active",
  active_hours_week: 28,
  acceptance_rate: 0.97,
  cancellation_rate: 0.02,
  avg_rating: 4.8,
  checks: {
    active_hours_check: true,
    acceptance_rate_check: true,
    cancellation_rate_check: true,
    rating_check: true
  }
}
```

## Component Hierarchy

```
layout.tsx (Root)
├── app/layout.tsx
│   ├── login/page.tsx
│   ├── register/page.tsx
│   └── dashboard/
│       ├── layout.tsx (Navigation)
│       ├── page.tsx (Main dashboard)
│       │
│       ├── [DRIVER ONLY]
│       │   ├── volatility/page.tsx (FR14)
│       │   │   └── useVolatility hook
│       │   ├── surveys/page.tsx (FR16)
│       │   │   ├── useSubmitSurvey hook
│       │   │   └── useMysurveys hook
│       │   └── eligibility/page.tsx (FR9)
│       │       └── useEligibility hook
│       │
│       └── [ADMIN ONLY]
│           ├── analytics/page.tsx
│           ├── accuracy/page.tsx (NFR3)
│           │   └── useAccuracy hook
│           ├── survey-admin/page.tsx (FR16 aggregate)
│           └── workers/page.tsx (FR9 management)
```

## State Management

**Zustand Store** (`lib/store.ts`):
```typescript
state: {
  user: User | null,      // Current user profile
  token: string | null,   // JWT token
  isLoading: boolean,
  error: string | null
}

actions: {
  register(),      // POST /auth/register
  login(),         // POST /auth/login
  logout(),        // Clear token
  loadUserFromToken()  // GET /auth/me
}
```

**Component-Level State**:
```typescript
// Per-component data fetching
const { data, loading, error } = useVolatility(workerId, days);

// Form submission
const { submit, loading, error } = useSubmitSurvey();
```

## Error Handling

**401 Unauthorized** (Token expired):
```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.setState({ user: null, token: null });
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**Other Errors** (caught in components):
```typescript
try {
  await apiService.submitSurvey(data);
} catch (err: any) {
  setError(err.response?.data?.detail || 'Failed to submit');
}
```

## Performance Considerations

1. **Token in localStorage**: Persists across page reloads
2. **Route-level code splitting**: Each page loaded separately
3. **Data fetching on mount**: useEffect hooks fetch on component load
4. **No automatic refetching**: User must manually refresh or re-navigate
5. **Axios caching**: No caching layer (all requests fresh)

## Testing Integration

To test each feature:

1. **Authentication**:
```bash
# Test with invalid credentials
POST http://localhost:8000/api/v1/auth/login
{ "email": "bad@example.com", "password": "wrong" }
# Should get 401 Unauthorized
```

2. **Volatility**:
```bash
# Test with valid token
GET http://localhost:8000/api/v1/analytics/worker/1/volatility
Authorization: Bearer <token>
# Should return volatility statistics
```

3. **Survey**:
```bash
# Test submission
POST http://localhost:8000/api/v1/surveys/submit
{ "income_stress_level": 4, ... }
# Should return 201 Created
```

## Database Schema Integration

```
Frontend → API → ORM → Database

User (from user.py):
  ├─ id (primary key)
  ├─ email (unique)
  ├─ password_hash
  ├─ full_name
  ├─ phone
  ├─ role (DRIVER/ADMIN enum)
  ├─ is_active boolean
  └─ is_verified boolean

WorkerEligibility → eligibility.py:
  ├─ worker_id (FK → User)
  ├─ is_eligible boolean
  ├─ status (active/suspended)
  ├─ active_hours_week float
  ├─ acceptance_rate float
  └─ avg_rating float

VolatilityMetrics → volatility.py:
  ├─ worker_id (FK → User)
  ├─ with_guarantee json object
  ├─ without_guarantee json object
  └─ created_at timestamp

PredictionAccuracy → accuracy.py:
  ├─ shift_id FK
  ├─ predicted_earnings
  ├─ actual_earnings
  ├─ mape float
  ├─ mae float
  └─ rmse float

WorkerSurvey → survey.py:
  ├─ worker_id (FK → User)
  ├─ income_stress_level 1-5
  ├─ schedule_satisfaction 1-5
  ├─ app_usefulness 1-5
  ├─ decision_making_improvement 1-5
  ├─ shift_planning_ease 1-5
  ├─ earnings_stability 1-5
  ├─ feedback text
  └─ response_date timestamp
```

## Deployment Checklist

- [ ] Backend running at production URL
- [ ] Database migrations applied
- [ ] Demo users seeded in database
- [ ] `NEXT_PUBLIC_API_BASE_URL` set to production backend URL
- [ ] Frontend built: `npm run build`
- [ ] Verify all pages load without 401 errors
- [ ] Test authentication flow end-to-end
- [ ] Test each role (driver, admin) features
- [ ] Verify data appears correctly after API calls
- [ ] Check console for JavaScript errors
- [ ] Monitor network requests for failed API calls

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| CORS Error | Backend doesn't allow frontend domain | Add frontend URL to backend CORS origins |
| 401 on every request | Token invalid/missing | Clear localStorage, re-login |
| API calls timeout | Backend not running | Start FastAPI: `python -m uvicorn main:app --reload` |
| Blank page after login | Routes not matching | Check dashboard layout navigation links |
| Data not updating | Stale data or cache | Manually refresh page (F5) |
| "Cannot find module" | Missing dependency | Run `npm install` |

## Next: Database Migrations

Before using the frontend, ensure backend has the new models:

```bash
cd backend
alembic revision --autogenerate -m "add_user_auth_and_metrics"
alembic upgrade head
python scripts/seed_data.py  # Create demo accounts
```

Then start backend and frontend together for full integration testing.
