from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class WorkerCreate(BaseModel):
    name: str
    email: EmailStr


class WorkerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: EmailStr
    created_at: Optional[datetime]


class ShiftCreate(BaseModel):
    worker_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    earnings: float = 0.0
    predicted_earnings: Optional[float] = 0.0


class ShiftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    worker_id: int
    start_time: datetime
    end_time: Optional[datetime]
    earnings: float
    predicted_earnings: float
    created_at: Optional[datetime]
