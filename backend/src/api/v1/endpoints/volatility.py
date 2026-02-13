"""
Earnings Volatility API Endpoints

Routes for analyzing income stability metrics.
Accessible to: Drivers (own data) and Admins (all data).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.volatility import VolatilityAnalyzer
from src.services.auth import AuthService

router = APIRouter(prefix="/api/v1/analytics", tags=["volatility"])


def get_current_user(token: str = None, db: Session = Depends(get_db)):
    """Extract current user from JWT token"""
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return token_data


@router.get("/worker/{worker_id}/volatility")
def get_worker_volatility(
    worker_id: int,
    days: int = Query(30, ge=1, le=365),
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Analyze earnings volatility for a worker.
    
    **Access:** 
    - Drivers: Can view own data (worker_id must match current user)
    - Admins: Can view any worker's data
    
    Query Parameters:
    - days: Analysis period (default 30 days)
    
    Returns:
    - Statistics without guarantee (raw earnings)
    - Statistics with guarantee (after top-ups)
    - Impact analysis (volatility reduction %)
    
    Example response:
    {
        "without_guarantee": {
            "mean": 125.50,
            "std_dev": 45.32,
            "coefficient_variation": 36.1
        },
        "with_guarantee": {
            "mean": 132.15,
            "std_dev": 12.50,
            "coefficient_variation": 9.5
        },
        "impact": {
            "volatility_reduction_percent": 72.4,
            "cv_reduction_percent": 73.7
        }
    }
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check access control
    if current_user["role"] == "driver" and current_user["user_id"] != worker_id:
        raise HTTPException(
            status_code=403,
            detail="Drivers can only view their own volatility analysis"
        )
    
    analyzer = VolatilityAnalyzer(db)
    result = analyzer.analyze_worker_volatility(worker_id, days)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.post("/worker/{worker_id}/volatility/snapshot")
def create_volatility_snapshot(
    worker_id: int,
    days: int = Query(30),
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Record a volatility metrics snapshot for a worker.
    
    **Access:** Admins only
    
    Should be called:
    - Weekly to track volatility trends
    - Monthly for comprehensive analysis
    - After significant usage pattern changes
    
    Returns: Stored metrics with timestamps for historical comparison.
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check admin access
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create volatility snapshots"
        )
    
    analyzer = VolatilityAnalyzer(db)
    metrics = analyzer.store_volatility_metrics(worker_id, days)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Could not create metrics")
    
    return {
        "snapshot_id": metrics.id,
        "worker_id": worker_id,
        "period_start": metrics.period_start,
        "period_end": metrics.period_end,
        "volatility_reduction_percent": metrics.volatility_reduction_percent,
        "cv_reduction_percent": metrics.cv_reduction_percent,
        "message": "Metrics snapshot created and stored"
    }


@router.get("/volatility/summary")
def get_volatility_summary(
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Get system-wide volatility summary.
    
    **Access:** Admins only
    
    Shows overall volatility reduction impact across all workers.
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check admin access
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can view system summary"
        )
    
    # This would aggregate all worker volatility metrics
    return {
        "message": "Volatility summary endpoint ready",
        "admin_only": True
    }
