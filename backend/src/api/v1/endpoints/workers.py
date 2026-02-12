from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models import Worker
from src.schemas import WorkerCreate, WorkerRead

router = APIRouter(prefix="/api/v1/workers", tags=["workers"])


@router.post("/", response_model=WorkerRead, status_code=status.HTTP_201_CREATED)
def create_worker(payload: WorkerCreate, db: Session = Depends(get_db)):
    """Create a new worker"""
    existing = db.query(Worker).filter(Worker.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Worker with this email already exists")

    worker = Worker(name=payload.name, email=payload.email)
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@router.get("/", response_model=List[WorkerRead])
def list_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List workers"""
    workers = db.query(Worker).offset(skip).limit(limit).all()
    return workers
