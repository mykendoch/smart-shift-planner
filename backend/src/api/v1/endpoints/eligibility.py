"""
Worker Eligibility API Endpoints

Routes for checking and managing worker eligibility for income guarantee.
Accessible to: Admins (manage) and Drivers (view own status).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.eligibility import EligibilityChecker
from src.services.auth import AuthService

router = APIRouter(prefix="/api/v1/eligibility", tags=["eligibility"])


def get_current_user(token: str = None, db: Session = Depends(get_db)):
    """Extract current user from JWT token"""
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return token_data


@router.get("/worker/{worker_id}")
def get_eligibility_status(
    worker_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Check worker eligibility for income guarantee protection.
    
    **Access:**
    - Drivers: Can view own status (worker_id must match current user)
    - Admins: Can view any worker's status
    
    Returns:
    {
        "worker_id": 1,
        "is_eligible": true,
        "status_checks": {
            "active_hours": {"met": true, "value": 25.5, "required": 20.0},
            "acceptance_rate": {"met": true, "value": 96.0, "required": 95.0},
            "cancellation_rate": {"met": true, "value": 2.0, "required": 5.0},
            "account_status": {"met": true, "value": "Active"}
        },
        "reason": "All checks passed",
        "guarantee_protection": "✓ Enabled"
    }
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check access control
    if current_user["role"] == "driver" and current_user["user_id"] != worker_id:
        raise HTTPException(
            status_code=403,
            detail="Drivers can only view their own eligibility"
        )
    
    checker = EligibilityChecker(db)
    return checker.get_eligibility_status(worker_id)


@router.post("/worker/{worker_id}/recalculate")
def recalculate_eligibility(
    worker_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Recalculate eligibility metrics from recent shift data.
    
    **Access:** Admins only
    
    Call this:
    - After each shift completes
    - When worker performance changes
    - During worker review periods
    
    Returns updated eligibility status and metrics.
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check admin access
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can recalculate eligibility"
        )
    
    checker = EligibilityChecker(db)
    eligibility = checker.update_metrics(worker_id)
    
    if not eligibility:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    return {
        "worker_id": worker_id,
        "is_eligible": eligibility.is_eligible,
        "metrics": {
            "active_hours_week": round(eligibility.active_hours_week, 1),
            "acceptance_rate": round(eligibility.acceptance_rate * 100, 1),
            "cancellation_rate": round(eligibility.cancellation_rate * 100, 1)
        },
        "reason": eligibility.eligibility_reason
    }


@router.post("/worker/{worker_id}/suspend")
def suspend_worker(
    worker_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Suspend worker account (removes guarantee eligibility).
    
    **Access:** Admins only
    
    Use for:
    - Policy violations
    - Low acceptance rates
    - Quality issues
    
    Returns suspension confirmation.
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check admin access
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can suspend accounts"
        )
    
    checker = EligibilityChecker(db)
    result = checker.suspend_account(worker_id)
    
    return {
        **result,
        "action": "Account suspended - Income guarantee disabled"
    }


@router.post("/worker/{worker_id}/reactivate")
def reactivate_worker(
    worker_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Reactivate suspended worker account.
    
    **Access:** Admins only
    
    Use when:
    - Suspension period ends
    - Issues have been resolved
    - Worker demonstrates compliance
    
    Note: Worker must pass eligibility checks again.
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check admin access
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can reactivate accounts"
        )
    
    checker = EligibilityChecker(db)
    result = checker.reactivate_account(worker_id)
    
    return result
