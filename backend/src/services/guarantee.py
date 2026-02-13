"""
Income Guarantee Service

Core business logic for the Income Guarantee Window - Priority 2.

This service manages the complete guarantee lifecycle:
1. Shift commitment (FR7) - Driver commits to a recommended shift
2. Eligibility validation (FR9) - Verify driver meets guarantee requirements
3. Guarantee activation (FR8) - Activate protection on committed shifts
4. Earnings recording (FR10) - Track actual earnings during shift
5. Earnings comparison (FR11) - Compare actual vs guaranteed minimum
6. Top-up calculation (FR12) - Calculate difference if below threshold
7. Guarantee logging (FR13) - Audit trail for all guarantee operations
8. Performance reporting (FR14, FR15) - Volatility and earning metrics

Business Rules:
    - Guarantee threshold: 90% of predicted earnings (configurable)
    - Minimum shift duration for guarantee: 4 hours (configurable)
    - Eligibility: 20+ hrs/week, 95%+ acceptance rate, <5% cancellation rate
    - Top-up formula: max(0, predicted_earnings × 0.9 − actual_earnings)
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from src.models.committed_shift import CommittedShift, GuaranteeLog, ShiftStatus
from src.models.user import User
from src.core.config import settings

logger = logging.getLogger(__name__)


class IncomeGuaranteeService:
    """
    Income Guarantee Window - Core Service

    Manages committed shifts, guarantee calculations, earnings tracking,
    and audit logging for the income guarantee mechanism.
    """

    def __init__(self, db: Session):
        self.db = db
        self.guarantee_threshold = settings.GUARANTEE_THRESHOLD       # 0.9 = 90%
        self.min_hours = settings.MINIMUM_HOURS_FOR_GUARANTEE         # 4.0 hours

    # =========================================================================
    # FR7: SHIFT COMMITMENT
    # =========================================================================

    def commit_to_shift(self, driver_id: int, recommendation: Dict) -> CommittedShift:
        """
        Driver commits to a recommended shift.

        Creates a CommittedShift record and logs the commitment event.
        The guaranteed minimum is calculated immediately.

        Args:
            driver_id: ID of the driver (users.id)
            recommendation: Shift recommendation data from ShiftRecommender

        Returns:
            CommittedShift: The created committed shift record
        """
        logger.info(f"Driver {driver_id} committing to shift at {recommendation.get('location_name')}")

        # Verify driver exists
        driver = self.db.query(User).filter(User.id == driver_id).first()
        if not driver:
            raise ValueError(f"Driver with id {driver_id} not found")

        # Create committed shift
        committed = CommittedShift(
            driver_id=driver_id,
            location_name=recommendation.get("location_name", "Unknown"),
            location_key=recommendation.get("location_key"),
            region=recommendation.get("region"),
            zone=recommendation.get("zone"),
            shift_type=recommendation.get("shift_type", "Standard"),
            day_name=recommendation.get("day_name"),
            start_time=datetime.fromisoformat(recommendation["start_time"]),
            end_time=datetime.fromisoformat(recommendation["end_time"]),
            predicted_earnings=recommendation.get("predicted_earnings", 0.0),
            base_hourly_rate=recommendation.get("base_hourly"),
            demand_score=recommendation.get("demand_score"),
            guarantee_eligible=recommendation.get("guarantee_eligible", True),
            guarantee_threshold=self.guarantee_threshold,
            status=ShiftStatus.COMMITTED.value,
        )

        # Calculate guaranteed minimum immediately
        committed.guaranteed_minimum = round(
            committed.predicted_earnings * self.guarantee_threshold, 2
        )

        self.db.add(committed)
        self.db.commit()
        self.db.refresh(committed)

        # FR13: Log commitment event
        self._log_event(
            committed_shift_id=committed.id,
            driver_id=driver_id,
            event_type="commitment",
            description=(
                f"Driver committed to {committed.shift_type} at {committed.location_name}. "
                f"Predicted: £{committed.predicted_earnings:.2f}, "
                f"Guaranteed minimum: £{committed.guaranteed_minimum:.2f}"
            ),
            predicted=committed.predicted_earnings,
            guaranteed_min=committed.guaranteed_minimum,
            was_eligible=committed.guarantee_eligible,
        )

        logger.info(
            f"Shift committed: id={committed.id}, "
            f"predicted=£{committed.predicted_earnings:.2f}, "
            f"guaranteed_min=£{committed.guaranteed_minimum:.2f}"
        )

        return committed

    # =========================================================================
    # FR10: REAL-TIME EARNINGS TRACKING
    # =========================================================================

    def record_actual_earnings(
        self, committed_shift_id: int, actual_earnings: float, driver_id: int
    ) -> CommittedShift:
        """
        Record actual earnings after a committed shift is completed.

        This triggers:
        - Status update to 'completed'
        - Top-up calculation (FR12)
        - Guarantee activation check (FR8)
        - Audit logging (FR13)

        Args:
            committed_shift_id: ID of the committed shift
            actual_earnings: Real earnings in GBP
            driver_id: Driver ID for authorization

        Returns:
            CommittedShift with calculated guarantee fields
        """
        committed = (
            self.db.query(CommittedShift)
            .filter(
                CommittedShift.id == committed_shift_id,
                CommittedShift.driver_id == driver_id,
            )
            .first()
        )

        if not committed:
            raise ValueError(f"Committed shift {committed_shift_id} not found for driver {driver_id}")

        if committed.status == ShiftStatus.CANCELLED.value:
            raise ValueError("Cannot record earnings for a cancelled shift")

        # Record actual earnings
        committed.actual_earnings = round(actual_earnings, 2)
        committed.status = ShiftStatus.COMPLETED.value
        committed.completed_at = datetime.utcnow()

        # FR12: Calculate top-up
        committed.calculate_guarantee()

        self.db.commit()
        self.db.refresh(committed)

        # FR13: Log earnings recorded event
        self._log_event(
            committed_shift_id=committed.id,
            driver_id=driver_id,
            event_type="earnings_recorded",
            description=(
                f"Actual earnings: £{actual_earnings:.2f}. "
                f"Predicted: £{committed.predicted_earnings:.2f}. "
                f"Guaranteed minimum: £{committed.guaranteed_minimum:.2f}."
            ),
            predicted=committed.predicted_earnings,
            actual=actual_earnings,
            guaranteed_min=committed.guaranteed_minimum,
            topup=committed.topup_amount,
        )

        # FR8: If guarantee activated, log that separately
        if committed.guarantee_activated:
            self._log_event(
                committed_shift_id=committed.id,
                driver_id=driver_id,
                event_type="guarantee_activated",
                description=(
                    f"Income guarantee ACTIVATED. "
                    f"Actual £{actual_earnings:.2f} < Guaranteed £{committed.guaranteed_minimum:.2f}. "
                    f"Top-up: £{committed.topup_amount:.2f}"
                ),
                predicted=committed.predicted_earnings,
                actual=actual_earnings,
                guaranteed_min=committed.guaranteed_minimum,
                topup=committed.topup_amount,
                was_eligible=committed.guarantee_eligible,
            )
            logger.info(
                f"Guarantee ACTIVATED for shift {committed.id}: "
                f"top-up=£{committed.topup_amount:.2f}"
            )

        return committed

    # =========================================================================
    # FR7: SHIFT CANCELLATION
    # =========================================================================

    def cancel_shift(self, committed_shift_id: int, driver_id: int) -> CommittedShift:
        """Cancel a committed shift before it starts."""
        committed = (
            self.db.query(CommittedShift)
            .filter(
                CommittedShift.id == committed_shift_id,
                CommittedShift.driver_id == driver_id,
            )
            .first()
        )
        if not committed:
            raise ValueError(f"Committed shift {committed_shift_id} not found")

        if committed.status != ShiftStatus.COMMITTED.value:
            raise ValueError("Can only cancel shifts with 'committed' status")

        committed.status = ShiftStatus.CANCELLED.value
        committed.cancelled_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(committed)

        self._log_event(
            committed_shift_id=committed.id,
            driver_id=driver_id,
            event_type="cancellation",
            description=f"Driver cancelled shift at {committed.location_name}",
        )

        return committed

    # =========================================================================
    # FR11: EARNINGS COMPARISON & REPORTS
    # =========================================================================

    def get_driver_guarantee_summary(self, driver_id: int) -> Dict:
        """
        Comprehensive guarantee summary for a driver.

        Returns:
            - Total shifts committed, completed, cancelled
            - Total predicted vs actual earnings
            - Total top-ups paid
            - Guarantee activation rate
            - Income stability metrics
        """
        all_shifts = (
            self.db.query(CommittedShift)
            .filter(CommittedShift.driver_id == driver_id)
            .all()
        )

        if not all_shifts:
            return {
                "driver_id": driver_id,
                "total_committed": 0,
                "total_completed": 0,
                "total_cancelled": 0,
                "total_in_progress": 0,
                "total_predicted_earnings": 0.0,
                "total_actual_earnings": 0.0,
                "total_guaranteed_minimum": 0.0,
                "total_topup_paid": 0.0,
                "guarantee_activation_rate": 0.0,
                "avg_predicted_per_shift": 0.0,
                "avg_actual_per_shift": 0.0,
                "earnings_accuracy_pct": 0.0,
                "income_improvement_pct": 0.0,
                "shifts": [],
            }

        completed = [s for s in all_shifts if s.status == ShiftStatus.COMPLETED.value]
        committed_only = [s for s in all_shifts if s.status == ShiftStatus.COMMITTED.value]
        cancelled = [s for s in all_shifts if s.status == ShiftStatus.CANCELLED.value]
        in_progress = [s for s in all_shifts if s.status == ShiftStatus.IN_PROGRESS.value]

        # Earnings calculations (completed shifts only)
        total_predicted = sum(s.predicted_earnings for s in completed)
        total_actual = sum(s.actual_earnings or 0 for s in completed)
        total_guaranteed_min = sum(s.guaranteed_minimum or 0 for s in completed)
        total_topup = sum(s.topup_amount or 0 for s in completed)
        guarantee_activations = sum(1 for s in completed if s.guarantee_activated)

        n_completed = len(completed)
        activation_rate = (guarantee_activations / n_completed * 100) if n_completed > 0 else 0.0
        accuracy = (total_actual / total_predicted * 100) if total_predicted > 0 else 0.0
        income_improvement = (total_topup / total_actual * 100) if total_actual > 0 else 0.0

        # Build shift details list
        shift_details = []
        for s in all_shifts:
            shift_details.append({
                "id": s.id,
                "location_name": s.location_name,
                "shift_type": s.shift_type,
                "day_name": s.day_name,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "predicted_earnings": s.predicted_earnings,
                "actual_earnings": s.actual_earnings,
                "guaranteed_minimum": s.guaranteed_minimum,
                "topup_amount": s.topup_amount,
                "guarantee_activated": s.guarantee_activated,
                "guarantee_eligible": s.guarantee_eligible,
                "status": s.status,
                "duration_hours": s.shift_duration_hours,
                "commitment_time": s.commitment_time.isoformat() if s.commitment_time else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            })

        return {
            "driver_id": driver_id,
            "total_committed": len(committed_only),
            "total_completed": n_completed,
            "total_cancelled": len(cancelled),
            "total_in_progress": len(in_progress),
            "total_predicted_earnings": round(total_predicted, 2),
            "total_actual_earnings": round(total_actual, 2),
            "total_guaranteed_minimum": round(total_guaranteed_min, 2),
            "total_topup_paid": round(total_topup, 2),
            "guarantee_activation_rate": round(activation_rate, 1),
            "avg_predicted_per_shift": round(total_predicted / n_completed, 2) if n_completed else 0.0,
            "avg_actual_per_shift": round(total_actual / n_completed, 2) if n_completed else 0.0,
            "earnings_accuracy_pct": round(accuracy, 1),
            "income_improvement_pct": round(income_improvement, 1),
            "guarantee_threshold": f"{int(self.guarantee_threshold * 100)}%",
            "shifts": shift_details,
        }

    # =========================================================================
    # FR14: EARNINGS VOLATILITY ANALYSIS
    # =========================================================================

    def get_volatility_comparison(self, driver_id: int) -> Dict:
        """
        Compare earnings volatility WITH and WITHOUT the guarantee.

        Shows the impact of the Income Guarantee Window on income stability.
        Answers Research Question 2: Does income guarantee reduce income volatility?
        """
        completed = (
            self.db.query(CommittedShift)
            .filter(
                CommittedShift.driver_id == driver_id,
                CommittedShift.status == ShiftStatus.COMPLETED.value,
            )
            .all()
        )

        if len(completed) < 2:
            return {
                "driver_id": driver_id,
                "message": "Need at least 2 completed shifts for volatility analysis",
                "without_guarantee": {},
                "with_guarantee": {},
                "impact": {},
            }

        raw_earnings = [s.actual_earnings or 0 for s in completed]
        guaranteed_earnings = [
            (s.actual_earnings or 0) + (s.topup_amount or 0) for s in completed
        ]

        raw_stats = self._calc_stats(raw_earnings)
        guaranteed_stats = self._calc_stats(guaranteed_earnings)

        # Volatility reduction
        vol_reduction = 0.0
        if raw_stats["std_dev"] > 0:
            vol_reduction = (
                (raw_stats["std_dev"] - guaranteed_stats["std_dev"])
                / raw_stats["std_dev"]
                * 100
            )

        cv_reduction = 0.0
        if raw_stats["cv"] > 0:
            cv_reduction = (
                (raw_stats["cv"] - guaranteed_stats["cv"]) / raw_stats["cv"] * 100
            )

        return {
            "driver_id": driver_id,
            "num_shifts": len(completed),
            "without_guarantee": raw_stats,
            "with_guarantee": guaranteed_stats,
            "impact": {
                "volatility_reduction_pct": round(vol_reduction, 1),
                "cv_reduction_pct": round(cv_reduction, 1),
                "earnings_floor_without": raw_stats["min"],
                "earnings_floor_with": guaranteed_stats["min"],
                "total_topup_paid": round(sum(s.topup_amount or 0 for s in completed), 2),
                "interpretation": (
                    f"The Income Guarantee Window reduced earnings volatility by "
                    f"{abs(vol_reduction):.1f}%, raising the earnings floor from "
                    f"£{raw_stats['min']:.2f} to £{guaranteed_stats['min']:.2f}."
                ),
            },
        }

    # =========================================================================
    # FR15: PERFORMANCE REPORTING
    # =========================================================================

    def get_performance_report(self, driver_id: int) -> Dict:
        """
        Generate comprehensive performance report for a driver.

        Includes earnings trends, guarantee usage, and stability metrics.
        """
        completed = (
            self.db.query(CommittedShift)
            .filter(
                CommittedShift.driver_id == driver_id,
                CommittedShift.status == ShiftStatus.COMPLETED.value,
            )
            .order_by(CommittedShift.start_time)
            .all()
        )

        if not completed:
            return {
                "driver_id": driver_id,
                "message": "No completed shifts to report on",
                "earnings_trend": [],
                "best_locations": [],
                "best_shift_types": [],
            }

        # Earnings trend (per shift)
        earnings_trend = []
        for s in completed:
            earnings_trend.append({
                "date": s.start_time.strftime("%Y-%m-%d"),
                "day": s.day_name or s.start_time.strftime("%A"),
                "location": s.location_name,
                "shift_type": s.shift_type,
                "predicted": round(s.predicted_earnings, 2),
                "actual": round(s.actual_earnings or 0, 2),
                "topup": round(s.topup_amount or 0, 2),
                "total_with_guarantee": round(
                    (s.actual_earnings or 0) + (s.topup_amount or 0), 2
                ),
                "hours": s.shift_duration_hours,
                "hourly_rate": s.actual_hourly_rate,
            })

        # Best locations (by average actual earnings)
        location_earnings = {}
        for s in completed:
            loc = s.location_name
            if loc not in location_earnings:
                location_earnings[loc] = {"total": 0, "count": 0, "hours": 0}
            location_earnings[loc]["total"] += s.actual_earnings or 0
            location_earnings[loc]["count"] += 1
            location_earnings[loc]["hours"] += s.shift_duration_hours

        best_locations = []
        for loc, data in sorted(
            location_earnings.items(), key=lambda x: x[1]["total"] / x[1]["count"], reverse=True
        ):
            best_locations.append({
                "location": loc,
                "avg_earnings": round(data["total"] / data["count"], 2),
                "total_earnings": round(data["total"], 2),
                "shifts_worked": data["count"],
                "total_hours": round(data["hours"], 1),
                "avg_hourly": round(data["total"] / data["hours"], 2) if data["hours"] > 0 else 0,
            })

        # Best shift types
        type_earnings = {}
        for s in completed:
            st = s.shift_type
            if st not in type_earnings:
                type_earnings[st] = {"total": 0, "count": 0}
            type_earnings[st]["total"] += s.actual_earnings or 0
            type_earnings[st]["count"] += 1

        best_types = []
        for st, data in sorted(
            type_earnings.items(), key=lambda x: x[1]["total"] / x[1]["count"], reverse=True
        ):
            best_types.append({
                "shift_type": st,
                "avg_earnings": round(data["total"] / data["count"], 2),
                "total_earnings": round(data["total"], 2),
                "shifts_worked": data["count"],
            })

        total_actual = sum(s.actual_earnings or 0 for s in completed)
        total_topups = sum(s.topup_amount or 0 for s in completed)
        total_hours = sum(s.shift_duration_hours for s in completed)

        return {
            "driver_id": driver_id,
            "report_period": {
                "from": completed[0].start_time.strftime("%Y-%m-%d"),
                "to": completed[-1].start_time.strftime("%Y-%m-%d"),
                "total_shifts": len(completed),
                "total_hours": round(total_hours, 1),
            },
            "earnings_summary": {
                "total_actual": round(total_actual, 2),
                "total_topups": round(total_topups, 2),
                "total_with_guarantee": round(total_actual + total_topups, 2),
                "avg_per_shift": round(total_actual / len(completed), 2),
                "avg_hourly": round(total_actual / total_hours, 2) if total_hours > 0 else 0,
                "income_boost_pct": round(
                    total_topups / total_actual * 100, 1
                ) if total_actual > 0 else 0,
            },
            "earnings_trend": earnings_trend,
            "best_locations": best_locations,
            "best_shift_types": best_types,
        }

    # =========================================================================
    # GUARANTEE HISTORY & AUDIT LOG (FR13)
    # =========================================================================

    def get_guarantee_history(self, driver_id: int, limit: int = 50) -> List[Dict]:
        """Get guarantee audit log for a driver."""
        logs = (
            self.db.query(GuaranteeLog)
            .filter(GuaranteeLog.driver_id == driver_id)
            .order_by(desc(GuaranteeLog.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": log.id,
                "event_type": log.event_type,
                "description": log.event_description,
                "predicted_earnings": log.predicted_earnings,
                "actual_earnings": log.actual_earnings,
                "guaranteed_minimum": log.guaranteed_minimum,
                "topup_amount": log.topup_amount,
                "was_eligible": log.was_eligible,
                "timestamp": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]

    def get_committed_shifts(
        self, driver_id: int, status: Optional[str] = None
    ) -> List[Dict]:
        """Get all committed shifts for a driver, optionally filtered by status."""
        query = self.db.query(CommittedShift).filter(
            CommittedShift.driver_id == driver_id
        )
        if status:
            query = query.filter(CommittedShift.status == status)

        shifts = query.order_by(desc(CommittedShift.created_at)).all()

        return [
            {
                "id": s.id,
                "location_name": s.location_name,
                "region": s.region,
                "zone": s.zone,
                "shift_type": s.shift_type,
                "day_name": s.day_name,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "predicted_earnings": s.predicted_earnings,
                "actual_earnings": s.actual_earnings,
                "guaranteed_minimum": s.guaranteed_minimum,
                "topup_amount": s.topup_amount,
                "guarantee_eligible": s.guarantee_eligible,
                "guarantee_activated": s.guarantee_activated,
                "status": s.status,
                "demand_score": s.demand_score,
                "duration_hours": s.shift_duration_hours,
                "commitment_time": s.commitment_time.isoformat() if s.commitment_time else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in shifts
        ]

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    def _log_event(
        self,
        committed_shift_id: int,
        driver_id: int,
        event_type: str,
        description: str = "",
        predicted: float = None,
        actual: float = None,
        guaranteed_min: float = None,
        topup: float = None,
        was_eligible: bool = None,
    ):
        """Create an audit log entry (FR13, NFR11)."""
        log = GuaranteeLog(
            committed_shift_id=committed_shift_id,
            driver_id=driver_id,
            event_type=event_type,
            event_description=description,
            predicted_earnings=predicted,
            actual_earnings=actual,
            guaranteed_minimum=guaranteed_min,
            topup_amount=topup,
            guarantee_threshold=self.guarantee_threshold,
            was_eligible=was_eligible,
        )
        self.db.add(log)
        self.db.commit()

    @staticmethod
    def _calc_stats(values: List[float]) -> Dict:
        """Calculate basic statistics for a list of values."""
        import math

        if not values:
            return {"mean": 0, "std_dev": 0, "cv": 0, "min": 0, "max": 0, "range": 0}

        n = len(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = math.sqrt(variance)
        cv = (std_dev / mean * 100) if mean > 0 else 0

        return {
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "cv": round(cv, 1),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "range": round(max(values) - min(values), 2),
            "sample_size": n,
        }
