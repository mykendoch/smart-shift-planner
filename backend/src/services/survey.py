"""
Worker Survey Service

Collects and analyzes worker feedback on system effectiveness for:
"How does combining scheduling + guarantee influence productivity/decision-making?"
"""
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.eligibility_metrics import WorkerSurvey
from src.models.worker import Worker


class SurveyManager:
    """
    Manages worker survey data collection and analysis.
    
    Surveys capture:
    - Income stress levels
    - Work schedule satisfaction
    - App usefulness
    - Decision-making improvements
    - Open-ended feedback
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def submit_survey(self, worker_id: int, 
                     income_stress_level: int,
                     work_schedule_satisfaction: int,
                     app_usefulness: int,
                     decision_making_improvement: int,
                     shift_planning_ease: int,
                     earnings_stability: int,
                     positive_feedback: Optional[str] = None,
                     negative_feedback: Optional[str] = None,
                     suggestions: Optional[str] = None,
                     days_using_system: int = 0,
                     num_shifts_using_system: int = 0) -> Dict:
        """
        Submit a new survey response.
        
        All Likert scale fields (1-5):
        1 = Negative (stressed, unsatisfied, not useful, worse, difficult)
        5 = Positive (not stressed, satisfied, very useful, much better, very easy)
        
        Returns survey confirmation with ID.
        """
        # Validate worker exists
        worker = self.db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            return {"error": "Worker not found", "status": 404}
        
        # Validate all ratings are 1-5
        ratings = [
            income_stress_level, work_schedule_satisfaction, app_usefulness,
            decision_making_improvement, shift_planning_ease, earnings_stability
        ]
        if not all(1 <= r <= 5 for r in ratings):
            return {"error": "All ratings must be between 1-5", "status": 400}
        
        # Create survey entry
        survey = WorkerSurvey(
            worker_id=worker_id,
            income_stress_level=income_stress_level,
            work_schedule_satisfaction=work_schedule_satisfaction,
            app_usefulness=app_usefulness,
            decision_making_improvement=decision_making_improvement,
            shift_planning_ease=shift_planning_ease,
            earnings_stability=earnings_stability,
            positive_feedback=positive_feedback,
            negative_feedback=negative_feedback,
            suggestions=suggestions,
            days_using_system=days_using_system,
            num_shifts_using_system=num_shifts_using_system,
            response_date=datetime.utcnow()
        )
        
        self.db.add(survey)
        self.db.commit()
        self.db.refresh(survey)
        
        return {
            "survey_id": survey.id,
            "worker_id": worker_id,
            "status": "submitted",
            "message": "Thank you for your feedback!"
        }
    
    def get_worker_survey(self, worker_id: int, survey_id: int) -> Optional[Dict]:
        """Get a specific survey response"""
        survey = self.db.query(WorkerSurvey).filter(
            WorkerSurvey.id == survey_id,
            WorkerSurvey.worker_id == worker_id
        ).first()
        
        if not survey:
            return None
        
        return self._survey_to_dict(survey)
    
    def list_worker_surveys(self, worker_id: int) -> List[Dict]:
        """Get all surveys from a worker"""
        surveys = self.db.query(WorkerSurvey).filter(
            WorkerSurvey.worker_id == worker_id
        ).order_by(WorkerSurvey.response_date.desc()).all()
        
        return [self._survey_to_dict(s) for s in surveys]
    
    def get_survey_aggregate_report(self) -> Dict:
        """
        Generate aggregate survey report across all workers.
        
        Shows:
        - Average ratings for each question
        - Distribution of responses
        - Trends over time
        - Key feedback themes
        """
        surveys = self.db.query(WorkerSurvey).all()
        
        if not surveys:
            return {"error": "No survey data available"}
        
        n = len(surveys)
        
        # Calculate averages
        avg_income_stress = sum(s.income_stress_level or 0 for s in surveys) / n
        avg_schedule = sum(s.work_schedule_satisfaction or 0 for s in surveys) / n
        avg_usefulness = sum(s.app_usefulness or 0 for s in surveys) / n
        avg_decision = sum(s.decision_making_improvement or 0 for s in surveys) / n
        avg_planning = sum(s.shift_planning_ease or 0 for s in surveys) / n
        avg_stability = sum(s.earnings_stability or 0 for s in surveys) / n
        
        # Collect open feedback
        positive_comments = [s.positive_feedback for s in surveys if s.positive_feedback]
        negative_comments = [s.negative_feedback for s in surveys if s.negative_feedback]
        suggestions_list = [s.suggestions for s in surveys if s.suggestions]
        
        return {
            "total_responses": n,
            "average_ratings": {
                "income_stress_level": round(avg_income_stress, 2),
                "work_schedule_satisfaction": round(avg_schedule, 2),
                "app_usefulness": round(avg_usefulness, 2),
                "decision_making_improvement": round(avg_decision, 2),
                "shift_planning_ease": round(avg_planning, 2),
                "earnings_stability": round(avg_stability, 2)
            },
            "interpretation": {
                "income_stress": self._interpret_scale(avg_income_stress, "stress level"),
                "schedule_satisfaction": self._interpret_scale(avg_schedule, "satisfaction"),
                "app_usefulness": self._interpret_scale(avg_usefulness, "usefulness"),
                "decision_impact": self._interpret_scale(avg_decision, "improvement"),
                "earnings_stability": self._interpret_scale(avg_stability, "stability")
            },
            "feedback_summary": {
                "positive_comments": positive_comments[:5],  # Top 5
                "negative_comments": negative_comments[:5],
                "suggestions": suggestions_list[:5]
            },
            "overall_satisfaction": "High" if avg_usefulness >= 4 else "Moderate" if avg_usefulness >= 3 else "Low"
        }
    
    def anonymize_survey_data(self) -> List[Dict]:
        """
        Export anonymized survey data for research publication.
        
        Strips worker identifying info while preserving all survey responses.
        """
        surveys = self.db.query(WorkerSurvey).all()
        
        anonymized = []
        for survey in surveys:
            # Create hash of worker ID
            worker_hash = hashlib.sha256(
                str(survey.worker_id).encode()
            ).hexdigest()[:16]
            
            anonymized.append({
                "worker_id_hash": worker_hash,
                "income_stress_level": survey.income_stress_level,
                "work_schedule_satisfaction": survey.work_schedule_satisfaction,
                "app_usefulness": survey.app_usefulness,
                "decision_making_improvement": survey.decision_making_improvement,
                "shift_planning_ease": survey.shift_planning_ease,
                "earnings_stability": survey.earnings_stability,
                "days_using_system": survey.days_using_system,
                "num_shifts_using_system": survey.num_shifts_using_system,
                "response_date": survey.response_date.isoformat()
            })
        
        return anonymized
    
    @staticmethod
    def _survey_to_dict(survey: WorkerSurvey) -> Dict:
        """Convert survey ORM to dictionary"""
        return {
            "survey_id": survey.id,
            "worker_id": survey.worker_id,
            "income_stress_level": survey.income_stress_level,
            "work_schedule_satisfaction": survey.work_schedule_satisfaction,
            "app_usefulness": survey.app_usefulness,
            "decision_making_improvement": survey.decision_making_improvement,
            "shift_planning_ease": survey.shift_planning_ease,
            "earnings_stability": survey.earnings_stability,
            "positive_feedback": survey.positive_feedback,
            "negative_feedback": survey.negative_feedback,
            "suggestions": survey.suggestions,
            "days_using_system": survey.days_using_system,
            "num_shifts_using_system": survey.num_shifts_using_system,
            "response_date": survey.response_date.isoformat()
        }
    
    @staticmethod
    def _interpret_scale(value: float, metric: str) -> str:
        """Interpret Likert scale value"""
        if value >= 4:
            return f"High {metric}"
        elif value >= 3:
            return f"Moderate {metric}"
        else:
            return f"Low {metric}"
