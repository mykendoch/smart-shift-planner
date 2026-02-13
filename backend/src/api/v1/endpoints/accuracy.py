"""
Prediction Accuracy API Endpoints

Routes for measuring and monitoring model accuracy.
Accessible to: Admins only (system performance monitoring).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.accuracy import AccuracyAnalyzer
from src.services.auth import AuthService

router = APIRouter(prefix="/api/v1/models", tags=["accuracy"])


def get_current_user(token: str = None, db: Session = Depends(get_db)):
    """Extract current user from JWT token"""
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return token_data


@router.get("/accuracy")
def get_model_accuracy(
    location: str = Query(None),
    hour: int = Query(None, ge=0, le=23),
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Get prediction model accuracy metrics.
    
    **Access:** Admins only
    
    Query Parameters:
    - location: Filter by location (downtown, airport, etc.)
    - hour: Filter by hour of day (0-23)
    
    Returns accuracy metrics:
    - MAE: Mean Absolute Error ($)
    - MAPE: Mean Absolute Percentage Error (%)
    - RMSE: Root Mean Squared Error
    - R²: Goodness of fit (0-1)
    - accuracy_level: Excellent/Good/Acceptable/Poor
    
    Example:
    GET /api/v1/models/accuracy?location=downtown
    Returns: {
        "mae": 8.45,
        "mape": 12.3,
        "rmse": 14.2,
        "r2_score": 0.876,
        "accuracy_level": "Good",
        "meets_threshold": true
    }
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check admin access
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can view accuracy metrics"
        )
    
    analyzer = AccuracyAnalyzer(db)
    result = analyzer.get_model_accuracy(location, hour)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    # Add threshold check
    result["meets_threshold"] = (
        result.get("mape", float("inf")) <= 
        AccuracyAnalyzer.ACCURACY_THRESHOLDS["acceptable"]["mape_max"]
    )
    
    return result


@router.get("/accuracy/summary")
def get_accuracy_summary(
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Get overall model accuracy summary.
    
    **Access:** Admins only
    
    Shows:
    - Overall accuracy metrics
    - Accuracy by location (matrix)
    - Accuracy by time of day (24-hour breakdown)
    - Threshold compliance status
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check admin access
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can view accuracy summary"
        )
    
    analyzer = AccuracyAnalyzer(db)
    return analyzer.get_model_accuracy_summary()
