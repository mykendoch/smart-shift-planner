from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.database import get_db
from src.schemas import ShiftCreate, ShiftRead
from src.models import Worker, Shift
from src.services.shifts import create_shift, list_shifts, compute_topup
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


@router.get("/{shift_id}/topup")
def shift_topup(shift_id: int, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    top_up = compute_topup(shift, settings.GUARANTEE_THRESHOLD)
    return {"shift_id": shift_id, "top_up": top_up}
