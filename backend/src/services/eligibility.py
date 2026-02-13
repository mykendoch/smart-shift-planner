"""
Eligibility Validation Service

Verifies worker eligibility for income guarantee protection based on:
- Active hours worked
- Acceptance rate
- Cancellation rate
- Account status
"""
from sqlalchemy.orm import Session
from typing import Dict

from src.models.worker import Worker
from src.models.eligibility_metrics import WorkerEligibility
from src.core.config import settings


class EligibilityChecker:
    """
    Validates worker eligibility for income guarantee.
    
    Rules Configuration (src/core/config.py):
    - MIN_ACTIVE_HOURS_PER_WEEK: 20.0 hours
    - MIN_ACCEPTANCE_RATE: 0.95 (95%)
    - MAX_CANCELLATION_RATE: 0.05 (5%)
    - MIN_AVERAGE_RATING: 4.0 stars
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.min_active_hours = getattr(settings, 'MIN_ACTIVE_HOURS_PER_WEEK', 20.0)
        self.min_acceptance_rate = getattr(settings, 'MIN_ACCEPTANCE_RATE', 0.95)
        self.max_cancellation_rate = getattr(settings, 'MAX_CANCELLATION_RATE', 0.05)
        self.min_rating = getattr(settings, 'MIN_AVERAGE_RATING', 4.0)
    
    def is_eligible(self, worker_id: int) -> bool:
        """Check if worker is eligible for guarantee"""
        eligibility = self.db.query(WorkerEligibility).filter(
            WorkerEligibility.worker_id == worker_id
        ).first()
        
        if not eligibility:
            return True  # Default to eligible if no record
        
        # All conditions must be met
        active_hours_ok = eligibility.active_hours_week >= self.min_active_hours
        acceptance_ok = eligibility.acceptance_rate >= self.min_acceptance_rate
        cancellation_ok = eligibility.cancellation_rate <= self.max_cancellation_rate
        account_ok = eligibility.account_active
        
        return active_hours_ok and acceptance_ok and cancellation_ok and account_ok
    
    def get_eligibility_status(self, worker_id: int) -> Dict:
        """Get detailed eligibility status and reasons"""
        eligibility = self.db.query(WorkerEligibility).filter(
            WorkerEligibility.worker_id == worker_id
        ).first()
        
        if not eligibility:
            return {
                "worker_id": worker_id,
                "is_eligible": True,
                "reason": "No eligibility record - default eligible"
            }
        
        checks = {
            "active_hours": {
                "met": eligibility.active_hours_week >= self.min_active_hours,
                "value": round(eligibility.active_hours_week, 1),
                "required": self.min_active_hours,
                "status": "✓ Met" if eligibility.active_hours_week >= self.min_active_hours else "✗ Below threshold"
            },
            "acceptance_rate": {
                "met": eligibility.acceptance_rate >= self.min_acceptance_rate,
                "value": round(eligibility.acceptance_rate * 100, 1),
                "required": round(self.min_acceptance_rate * 100, 1),
                "status": "✓ Met" if eligibility.acceptance_rate >= self.min_acceptance_rate else "✗ Below threshold"
            },
            "cancellation_rate": {
                "met": eligibility.cancellation_rate <= self.max_cancellation_rate,
                "value": round(eligibility.cancellation_rate * 100, 1),
                "required": round(self.max_cancellation_rate * 100, 1),
                "status": "✓ Met" if eligibility.cancellation_rate <= self.max_cancellation_rate else "✗ Exceeds limit"
            },
            "account_status": {
                "met": eligibility.account_active,
                "value": "Active" if eligibility.account_active else "Suspended",
                "status": "✓ Active" if eligibility.account_active else "✗ Suspended"
            }
        }
        
        all_met = all(c["met"] for c in checks.values())
        reasons = [k for k, v in checks.items() if not v["met"]]
        
        return {
            "worker_id": worker_id,
            "is_eligible": all_met,
            "status_checks": checks,
            "failed_checks": reasons,
            "reason": f"Failed checks: {', '.join(reasons)}" if reasons else "All checks passed",
            "guarantee_protection": "✓ Enabled" if all_met else "✗ Not eligible"
        }
    
    def update_metrics(self, worker_id: int) -> WorkerEligibility:
        """
        Recalculate eligibility metrics from worker data.
        Called after each shift or periodically.
        """
        worker = self.db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            return None
        
        # Calculate metrics (in production, would come from platform API)
        # These are placeholder calculations
        active_hours_week = 25.0  # Would be calculated from recent shifts
        acceptance_rate = 0.96     # Would come from platform
        cancellation_rate = 0.02   # Would come from platform
        
        # Get or create eligibility record
        eligibility = self.db.query(WorkerEligibility).filter(
            WorkerEligibility.worker_id == worker_id
        ).first()
        
        if not eligibility:
            eligibility = WorkerEligibility(worker_id=worker_id)
            self.db.add(eligibility)
        
        # Update metrics
        eligibility.active_hours_week = active_hours_week
        eligibility.acceptance_rate = acceptance_rate
        eligibility.cancellation_rate = cancellation_rate
        
        # Determine eligibility
        checks = self.get_eligibility_status(worker_id)
        eligibility.is_eligible = checks["is_eligible"]
        eligibility.eligibility_reason = checks["reason"]
        
        self.db.commit()
        self.db.refresh(eligibility)
        
        return eligibility
    
    def suspend_account(self, worker_id: int) -> Dict:
        """Suspend worker account (removes guarantee eligibility)"""
        eligibility = self.db.query(WorkerEligibility).filter(
            WorkerEligibility.worker_id == worker_id
        ).first()
        
        if eligibility:
            eligibility.account_active = False
            eligibility.eligibility_reason = "Account suspended"
            self.db.commit()
        
        return {
            "worker_id": worker_id,
            "status": "suspended",
            "guarantee_protection": "✗ Suspended"
        }
    
    def reactivate_account(self, worker_id: int) -> Dict:
        """Reactivate worker account"""
        eligibility = self.db.query(WorkerEligibility).filter(
            WorkerEligibility.worker_id == worker_id
        ).first()
        
        if eligibility:
            eligibility.account_active = True
            self.db.commit()
        
        return {
            "worker_id": worker_id,
            "status": "reactivated",
            "message": "Account reactivated - eligibility checks required"
        }
