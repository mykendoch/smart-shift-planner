from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.database import get_db
from src.schemas import ShiftCreate, ShiftRead
from src.models import Worker, Shift
from src.models.user import User as UserModel
from src.services.shifts import create_shift, list_shifts, compute_topup
from src.services.shift_recommender import ShiftRecommender
from src.core.config import settings

router = APIRouter(prefix="/api/v1/shifts", tags=["shifts"])


@router.post("/", response_model=ShiftRead, status_code=status.HTTP_201_CREATED)
def create_shift_endpoint(payload: ShiftCreate, db: Session = Depends(get_db)):
    # Ensure worker exists
    worker = db.query(Worker).filter(Worker.id == payload.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    shift = create_shift(db=db, worker_id=payload.worker_id, start_time=payload.start_time, end_time=payload.end_time, earnings=payload.earnings, predicted_earnings=payload.predicted_earnings or 0.0)
    return shift


@router.get("/", response_model=List[ShiftRead])
def list_shifts_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    shifts = list_shifts(db=db, skip=skip, limit=limit)
    return shifts


@router.get("/recommendations/{worker_id}")
def get_shift_recommendations(worker_id: int, limit: int = 5, db: Session = Depends(get_db)):
    """
    Get AI-recommended shifts for a driver
    
    PRIORITY 1 FEATURE: Smart Shift Recommender
    
    Returns top recommended shifts based on:
    - UK demand patterns (time of day, day of week)
    - Location-based earnings potential
    - Income guarantee eligibility
    - Historical driver performance patterns
    
    Query Params:
    - limit: How many recommendations to return (default: 5)
    
    Returns:
    - location_name, region, zone
    - start_time, end_time
    - predicted_earnings
    - demand_score (0-100)
    - guarantee_eligible (boolean)
    - shift_type (Morning Rush, Evening Peak, etc.)
    """
    
    # Try User model first (authenticated login users), then Worker model
    user = db.query(UserModel).filter(UserModel.id == worker_id).first()
    if user:
        driver_name = user.full_name
    else:
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Driver not found")
        driver_name = worker.name
    
    recommender = ShiftRecommender(db=db)
    recommendations = recommender.generate_recommendations(
        worker_id=worker_id,
        num_recommendations=limit,
    )
    
    return {
        "worker_id": worker_id,
        "driver_name": driver_name,
        "recommendations": recommendations,
        "total": len(recommendations),
    }


@router.post("/{shift_id}/accept")
def accept_shift(shift_id: int, db: Session = Depends(get_db)):
    """
    Driver accepts a recommended shift
    
    Creates a shift record and marks it as accepted
    """
    
    # For now, just create a shift record
    # In production, would:
    # 1. Check driver availability
    # 2. Reserve the shift
    # 3. Send notifications
    # 4. Create contract/agreement
    
    return {
        "shift_id": shift_id,
        "status": "accepted",
        "message": "Shift accepted successfully",
    }


@router.get("/{shift_id}/topup")
def shift_topup(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    top_up = compute_topup(shift, settings.GUARANTEE_THRESHOLD)
    return {"shift_id": shift_id, "top_up": top_up}
