"""
Worker Survey API Endpoints

Routes for survey data collection and analysis.
Accessible to: Drivers (submit own surveys) and Admins (view all data).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from src.database import get_db
from src.services.survey import SurveyManager
from src.services.auth import AuthService

router = APIRouter(prefix="/api/v1/surveys", tags=["surveys"])


# REQUEST SCHEMA
class SurveySubmitRequest(BaseModel):
    """Survey submission request"""
    income_stress_level: int  # 1-5
    work_schedule_satisfaction: int  # 1-5
    app_usefulness: int  # 1-5
    decision_making_improvement: int  # 1-5
    shift_planning_ease: int  # 1-5
    earnings_stability: int  # 1-5
    positive_feedback: Optional[str] = None
    negative_feedback: Optional[str] = None
    suggestions: Optional[str] = None
    days_using_system: int = 0
    num_shifts_using_system: int = 0


def get_current_user(token: str = None, db: Session = Depends(get_db)):
    """Extract current user from JWT token"""
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return token_data


@router.post("/submit")
def submit_survey(
    request: SurveySubmitRequest,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Submit a survey response.
    
    **Access:** Drivers only
    
    All Likert scale fields (1-5):
    - 1 = Negative (stressed, unsatisfied, not useful, difficult)
    - 5 = Positive (not stressed, satisfied, very useful, easy)
    
    Request body example:
    {
        "income_stress_level": 4,
        "work_schedule_satisfaction": 5,
        "app_usefulness": 5,
        "decision_making_improvement": 4,
        "shift_planning_ease": 5,
        "earnings_stability": 4,
        "positive_feedback": "The app helped me plan better",
        "days_using_system": 30,
        "num_shifts_using_system": 15
    }
    
    Returns: {
        "survey_id": 1,
        "worker_id": 5,
        "status": "submitted",
        "message": "Thank you for your feedback!"
    }
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check driver access
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=403,
            detail="Only drivers can submit survey responses"
        )
    
    # Validate ratings
    ratings = [
        request.income_stress_level,
        request.work_schedule_satisfaction,
        request.app_usefulness,
        request.decision_making_improvement,
        request.shift_planning_ease,
        request.earnings_stability
    ]
    if not all(1 <= r <= 5 for r in ratings):
        raise HTTPException(
            status_code=400,
            detail="All ratings must be between 1 and 5"
        )
    
    manager = SurveyManager(db)
    result = manager.submit_survey(
        worker_id=current_user["user_id"],
        income_stress_level=request.income_stress_level,
        work_schedule_satisfaction=request.work_schedule_satisfaction,
        app_usefulness=request.app_usefulness,
        decision_making_improvement=request.decision_making_improvement,
        shift_planning_ease=request.shift_planning_ease,
        earnings_stability=request.earnings_stability,
        positive_feedback=request.positive_feedback,
        negative_feedback=request.negative_feedback,
        suggestions=request.suggestions,
        days_using_system=request.days_using_system,
        num_shifts_using_system=request.num_shifts_using_system
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status", 400),
            detail=result["error"]
        )
    
    return result


@router.get("/my-surveys")
def get_my_surveys(
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all surveys submitted by current driver.
    
    **Access:** Drivers only
    
    Returns list of all survey responses with timestamps.
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check driver access
    if current_user["role"] != "driver":
        raise HTTPException(
            status_code=403,
            detail="Only drivers can view their surveys"
        )
    
    manager = SurveyManager(db)
    surveys = manager.list_worker_surveys(current_user["user_id"])
    
    return {
        "worker_id": current_user["user_id"],
        "total_surveys": len(surveys),
        "surveys": surveys
    }


@router.get("/aggregate-report")
def get_aggregate_report(
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Get aggregate survey report across all workers.
    
    **Access:** Admins only
    
    Shows:
    - Average ratings for each question
    - Distribution of responses
    - Key feedback themes
    - Overall satisfaction level
    
    Returns aggregated data for research and system improvement.
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check admin access
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can view aggregate reports"
        )
    
    manager = SurveyManager(db)
    report = manager.get_survey_aggregate_report()
    
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    
    return report


@router.get("/export-anonymized")
def export_anonymized_data(
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Export anonymized survey data for research.
    
    **Access:** Admins only
    
    Removes all personally identifiable information:
    - Worker IDs hashed (SHA-256)
    - No email addresses
    - No names
    
    Safe for sharing with research partners or publishing.
    
    Returns: List of anonymized survey entries
    """
    # Get current user
    current_user = get_current_user(token, db)
    
    # Check admin access
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can export anonymized data"
        )
    
    manager = SurveyManager(db)
    data = manager.anonymize_survey_data()
    
    return {
        "total_records": len(data),
        "anonymized": True,
        "data": data,
        "note": "All worker IDs have been hashed for privacy"
    }
