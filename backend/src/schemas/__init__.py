# Pydantic Validation Schemas
#
# Defines data validation for:
# - Incoming API requests (Create schemas)
# - Outgoing API responses (Read schemas)
#
# Pydantic automatically validates incoming JSON against these schemas
# and converts response data to JSON from these schemas.

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


# ============================================================================
# WORKER SCHEMAS
# ============================================================================

class WorkerCreate(BaseModel):
    """
    Validation schema for creating a new worker (POST request).
    
    Validates incoming JSON from client:
        {"name": "John Doe", "email": "john@example.com"}
    
    Fields:
        name: Worker's full name (required, string)
        email: Email address (required, validated email format)
    
    FastAPI will reject requests with missing/invalid fields before
    reaching the endpoint function.
    """
    name: str  # Required text field
    email: EmailStr  # Required email (validated by email-validator library)


class WorkerRead(BaseModel):
    """
    Response schema for returning worker data (GET response).
    
    Converts Worker ORM object to JSON for API response:
        {"id": 1, "name": "John Doe", "email": "john@example.com", "created_at": "2026-02-12T..."}
    
    Fields:
        id: Database record ID
        name: Worker's name
        email: Email address
        created_at: When record was created (optional, may be null)
    
    ConfigDict(from_attributes=True): Converts SQLAlchemy ORM objects to Pydantic models
    Allows: WorkerRead.from_orm(worker_db_object)
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: EmailStr
    created_at: Optional[datetime]



# ============================================================================
# SHIFT SCHEMAS
# ============================================================================

class ShiftCreate(BaseModel):
    """
    Validation schema for creating a new shift (POST request).
    
    Validates incoming JSON from client:
        {
            "worker_id": 2,
            "start_time": "2026-02-12T08:00:00",
            "end_time": "2026-02-12T16:00:00",
            "earnings": 85.50,
            "predicted_earnings": 95.00
        }
    
    Fields:
        worker_id: ID of worker who worked this shift (required)
        start_time: Shift start datetime (required)
        end_time: Shift end datetime (optional, can be null for ongoing)
        earnings: Actual earnings received (default: 0.0)
        predicted_earnings: ML model prediction (default: 0.0)
    
    Top-up calculation:
        top_up = max(0, predicted_earnings × 0.9 - earnings)
        If worker earned $80 but predicted was $100: top_up = max(0, 100×0.9 - 80) = $10
    """
    worker_id: int  # Which worker worked this shift (must exist in workers table)
    start_time: datetime  # When shift started (required)
    end_time: Optional[datetime] = None  # When shift ended (optional)
    earnings: float = 0.0  # Actual earnings (default: zero)
    predicted_earnings: Optional[float] = 0.0  # ML prediction (default: zero)


class ShiftRead(BaseModel):
    """
    Response schema for returning shift data (GET response).
    
    Converts Shift ORM object to JSON:
        {
            "id": 5,
            "worker_id": 2,
            "start_time": "2026-02-12T08:00:00",
            "end_time": "2026-02-12T16:00:00",
            "earnings": 85.50,
            "predicted_earnings": 95.00,
            "created_at": "2026-02-12T09:30:45.123456"
        }
    
    ConfigDict(from_attributes=True): Converts SQLAlchemy Shift to Pydantic model
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int  # Shift record ID
    worker_id: int  # Which worker
    start_time: datetime  # Shift start
    end_time: Optional[datetime]  # Shift end (can be null)
    earnings: float  # What was earned
    predicted_earnings: float  # What was predicted
    created_at: Optional[datetime]  # When record was created
