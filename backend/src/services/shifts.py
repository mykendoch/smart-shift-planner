from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from src.models import Shift


def create_shift(db: Session, worker_id: int, start_time: datetime, end_time: Optional[datetime] = None, earnings: float = 0.0, predicted_earnings: float = 0.0) -> Shift:
    """Create a new Shift record and return it."""
    shift = Shift(worker_id=worker_id, start_time=start_time, end_time=end_time, earnings=earnings, predicted_earnings=predicted_earnings)
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


def list_shifts(db: Session, skip: int = 0, limit: int = 100) -> List[Shift]:
    return db.query(Shift).offset(skip).limit(limit).all()


def compute_topup(shift: Shift, threshold: float) -> float:
    """Compute top-up amount according to guarantee threshold.

    If actual earnings are below `predicted_earnings * threshold`, return the difference.
    """
    expected = (shift.predicted_earnings or 0.0) * threshold
    actual = shift.earnings or 0.0
    top_up = max(0.0, expected - actual)
    return top_up
