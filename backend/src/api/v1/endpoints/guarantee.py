"""
Income Guarantee API Endpoints

Priority 2: Income Guarantee Window

Routes for the complete guarantee lifecycle:
  POST /api/v1/guarantee/commit                        - Commit to a shift (FR7)
  POST /api/v1/guarantee/shifts/{id}/actual-earnings    - Record actual earnings (FR10)
  POST /api/v1/guarantee/shifts/{id}/cancel             - Cancel a committed shift
  GET  /api/v1/guarantee/driver/{id}/summary            - Full guarantee summary (FR11)
  GET  /api/v1/guarantee/driver/{id}/shifts             - List committed shifts
  GET  /api/v1/guarantee/driver/{id}/volatility         - Volatility comparison (FR14)
  GET  /api/v1/guarantee/driver/{id}/performance        - Performance report (FR15)
  GET  /api/v1/guarantee/driver/{id}/history            - Audit log (FR13)

All endpoints follow existing authentication patterns and logging conventions.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.guarantee import IncomeGuaranteeService
from src.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/guarantee", tags=["income-guarantee"])


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class CommitRequest(BaseModel):
    """Request body for committing to a shift"""
    driver_id: int
    location_name: str
    location_key: Optional[str] = None
    region: Optional[str] = None
    zone: Optional[str] = None
    shift_type: str
    day_name: Optional[str] = None
    start_time: str                     # ISO format datetime string
    end_time: str                       # ISO format datetime string
    predicted_earnings: float
    base_hourly: Optional[float] = None
    demand_score: Optional[float] = None
    guarantee_eligible: bool = True


class ActualEarningsRequest(BaseModel):
    """Request body for recording actual earnings"""
    actual_earnings: float
    driver_id: int


# ============================================================================
# AUTH HELPER
# ============================================================================

def get_current_user(token: str = None, db: Session = Depends(get_db)):
    """Extract current user from JWT token (optional for flexibility)"""
    if not token:
        return None
    token_data = AuthService.verify_access_token(token)
    return token_data


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/commit")
def commit_to_shift(payload: CommitRequest, db: Session = Depends(get_db)):
    """
    FR7: Commit to a recommended shift.

    Creates a committed shift record in the database with:
    - Predicted earnings from AI recommendation
    - Guaranteed minimum (predicted × 90%)
    - Status set to 'committed'

    The driver can later record actual earnings to trigger
    the income guarantee comparison.
    """
    logger.info(f"Shift commitment request: driver={payload.driver_id}, location={payload.location_name}")

    service = IncomeGuaranteeService(db)

    try:
        committed = service.commit_to_shift(
            driver_id=payload.driver_id,
            recommendation=payload.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "committed",
        "message": f"Successfully committed to {committed.shift_type} at {committed.location_name}",
        "committed_shift": {
            "id": committed.id,
            "location_name": committed.location_name,
            "shift_type": committed.shift_type,
            "day_name": committed.day_name,
            "start_time": committed.start_time.isoformat(),
            "end_time": committed.end_time.isoformat(),
            "predicted_earnings": committed.predicted_earnings,
            "guaranteed_minimum": committed.guaranteed_minimum,
            "guarantee_eligible": committed.guarantee_eligible,
            "status": committed.status,
        },
    }


@router.post("/shifts/{shift_id}/actual-earnings")
def record_actual_earnings(
    shift_id: int,
    payload: ActualEarningsRequest,
    db: Session = Depends(get_db),
):
    """
    FR10 + FR11 + FR12: Record actual earnings and calculate guarantee.

    After a committed shift is completed, the driver records their actual
    earnings. The system then:
    1. Compares actual vs guaranteed minimum (FR11)
    2. Calculates top-up if actual < guaranteed (FR12)
    3. Logs the guarantee activation (FR13)
    4. Returns the complete comparison

    Example:
        Predicted: £100.00
        Guaranteed minimum (90%): £90.00
        Actual: £75.00
        Top-up: £90.00 - £75.00 = £15.00
        Total with guarantee: £90.00
    """
    logger.info(
        f"Recording actual earnings: shift={shift_id}, "
        f"actual=£{payload.actual_earnings:.2f}, driver={payload.driver_id}"
    )

    service = IncomeGuaranteeService(db)

    try:
        committed = service.record_actual_earnings(
            committed_shift_id=shift_id,
            actual_earnings=payload.actual_earnings,
            driver_id=payload.driver_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "earnings_recorded",
        "message": (
            f"Earnings recorded. "
            f"{'Guarantee ACTIVATED — top-up of £' + f'{committed.topup_amount:.2f}' + ' applied.' if committed.guarantee_activated else 'Earnings met guaranteed minimum. No top-up needed.'}"
        ),
        "comparison": {
            "predicted_earnings": committed.predicted_earnings,
            "guaranteed_minimum": committed.guaranteed_minimum,
            "actual_earnings": committed.actual_earnings,
            "topup_amount": committed.topup_amount,
            "total_with_guarantee": round(
                (committed.actual_earnings or 0) + (committed.topup_amount or 0), 2
            ),
            "guarantee_activated": committed.guarantee_activated,
            "guarantee_threshold": f"{int(committed.guarantee_threshold * 100)}%",
        },
    }


@router.post("/shifts/{shift_id}/cancel")
def cancel_committed_shift(
    shift_id: int,
    driver_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Cancel a committed shift before it starts."""
    logger.info(f"Cancellation request: shift={shift_id}, driver={driver_id}")

    service = IncomeGuaranteeService(db)

    try:
        committed = service.cancel_shift(shift_id, driver_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "cancelled",
        "message": f"Shift at {committed.location_name} has been cancelled.",
        "shift_id": committed.id,
    }


@router.get("/driver/{driver_id}/summary")
def get_guarantee_summary(driver_id: int, db: Session = Depends(get_db)):
    """
    FR11 + FR12: Comprehensive guarantee summary.

    Returns complete overview of a driver's guarantee history including:
    - Total committed/completed/cancelled shifts
    - Total predicted vs actual earnings
    - Total top-ups paid
    - Guarantee activation rate
    - Per-shift breakdown with earnings comparison
    """
    logger.info(f"Guarantee summary request: driver={driver_id}")

    service = IncomeGuaranteeService(db)
    return service.get_driver_guarantee_summary(driver_id)


@router.get("/driver/{driver_id}/shifts")
def get_committed_shifts(
    driver_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List all committed shifts for a driver.

    Optional filter by status: committed, in_progress, completed, cancelled
    """
    service = IncomeGuaranteeService(db)
    return service.get_committed_shifts(driver_id, status)


@router.get("/driver/{driver_id}/volatility")
def get_volatility_comparison(driver_id: int, db: Session = Depends(get_db)):
    """
    FR14: Earnings volatility analysis.

    Compares earnings volatility WITH and WITHOUT the income guarantee.
    Shows impact on income stability - directly answers Research Question 2:
    "To what extent does an income guarantee mechanism reduce income volatility?"

    Returns:
    - Statistics without guarantee (raw earnings)
    - Statistics with guarantee (after top-ups)
    - Impact metrics (volatility reduction %, CV reduction %)
    """
    service = IncomeGuaranteeService(db)
    return service.get_volatility_comparison(driver_id)


@router.get("/driver/{driver_id}/performance")
def get_performance_report(driver_id: int, db: Session = Depends(get_db)):
    """
    FR15: Performance reporting.

    Generates summary reports on earnings improvement and stability metrics:
    - Earnings trend over time
    - Best locations and shift types
    - Total earnings with guarantee boost
    - Average hourly rate
    """
    service = IncomeGuaranteeService(db)
    return service.get_performance_report(driver_id)


@router.get("/driver/{driver_id}/history")
def get_guarantee_history(
    driver_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    FR13: Guarantee audit log.

    Returns chronological log of all guarantee events:
    - Commitments, earnings recordings, guarantee activations, cancellations
    - Financial data snapshots at each event
    - Eligibility status at each event

    Fulfils NFR11 (Auditability): All predictions, commitments, and
    guarantee calculations are logged for review and research evaluation.
    """
    service = IncomeGuaranteeService(db)
    return service.get_guarantee_history(driver_id, limit)
