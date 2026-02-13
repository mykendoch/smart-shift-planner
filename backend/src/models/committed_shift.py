"""
Committed Shift Database Model

Represents a shift that a driver has committed to via the Smart Shift Planner.
This is the core of the Income Guarantee Window - when a driver commits to a
shift and meets eligibility requirements, the system guarantees 90% of
predicted earnings. If actual earnings fall below this threshold, the driver
receives a top-up payment.

Lifecycle:
    1. Driver views AI shift recommendations (Priority 1)
    2. Driver commits to a recommended shift → CommittedShift is CREATED (status=committed)
    3. Shift starts → status changes to in_progress
    4. Shift ends → Driver records actual earnings → status changes to completed
    5. System calculates top-up: max(0, predicted_earnings * 0.9 - actual_earnings)
    6. If top-up > 0, guarantee is activated and logged

Fulfils Requirements:
    FR7  - Shift Commitment
    FR8  - Guarantee Activation
    FR10 - Real-Time Earnings Tracking
    FR11 - Earnings Comparison
    FR12 - Top-Up Calculation
    FR13 - Guarantee Logging (via GuaranteeLog)
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from src.database import Base


class ShiftStatus(str, PyEnum):
    """Status lifecycle for a committed shift"""
    COMMITTED = "committed"         # Driver has committed, shift not started
    IN_PROGRESS = "in_progress"     # Shift currently active
    COMPLETED = "completed"         # Shift finished, actual earnings recorded
    CANCELLED = "cancelled"         # Driver cancelled before shift started


class CommittedShift(Base):
    """
    Committed Shift ORM Model

    Tracks the full lifecycle of a driver's committed shift from
    commitment through to completion and guarantee resolution.

    Database Table: committed_shifts

    Key Fields:
        - predicted_earnings: ML-predicted amount (set at commitment)
        - actual_earnings: Real amount earned (set after shift)
        - guaranteed_minimum: predicted_earnings * GUARANTEE_THRESHOLD
        - topup_amount: max(0, guaranteed_minimum - actual_earnings)
        - guarantee_activated: True if topup > 0
    """
    __tablename__ = "committed_shifts"

    # PRIMARY KEY
    id = Column(Integer, primary_key=True, index=True)

    # DRIVER REFERENCE (links to users table)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # SHIFT DETAILS (from recommendation)
    location_name = Column(String(256), nullable=False)
    location_key = Column(String(128), nullable=True)
    region = Column(String(128), nullable=True)
    zone = Column(String(128), nullable=True)
    shift_type = Column(String(128), nullable=False)       # Morning Rush, Evening Peak, etc.
    day_name = Column(String(20), nullable=True)            # Monday, Tuesday, etc.

    # TIME WINDOW
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # EARNINGS
    predicted_earnings = Column(Float, nullable=False)      # ML prediction at commitment
    actual_earnings = Column(Float, nullable=True)          # Recorded after shift completion
    base_hourly_rate = Column(Float, nullable=True)         # Base rate from recommendation
    demand_score = Column(Float, nullable=True)             # Demand score (0-100)

    # INCOME GUARANTEE (FR8, FR11, FR12)
    guarantee_eligible = Column(Boolean, default=True)      # Eligible based on recommendation
    guarantee_threshold = Column(Float, default=0.9)        # 90% guarantee threshold
    guaranteed_minimum = Column(Float, nullable=True)       # predicted_earnings * threshold
    topup_amount = Column(Float, default=0.0)               # Difference paid to driver
    guarantee_activated = Column(Boolean, default=False)     # True if topup was needed

    # STATUS & LIFECYCLE
    status = Column(String(20), default=ShiftStatus.COMMITTED.value)
    commitment_time = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # METADATA
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def calculate_guarantee(self):
        """
        Calculate income guarantee fields after actual earnings are recorded.
        
        Formula: top_up = max(0, predicted_earnings * threshold - actual_earnings)
        Example: predicted=£100, actual=£80, threshold=0.9
                 guaranteed_min = £100 * 0.9 = £90
                 top_up = max(0, £90 - £80) = £10
        """
        self.guaranteed_minimum = round(self.predicted_earnings * self.guarantee_threshold, 2)

        if self.actual_earnings is not None:
            self.topup_amount = round(
                max(0.0, self.guaranteed_minimum - self.actual_earnings), 2
            )
            self.guarantee_activated = self.topup_amount > 0
        return self

    @property
    def shift_duration_hours(self):
        """Calculate shift duration in hours"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return round(delta.total_seconds() / 3600, 2)
        return 0.0

    @property
    def actual_hourly_rate(self):
        """Calculate actual hourly rate from earnings"""
        hours = self.shift_duration_hours
        if hours > 0 and self.actual_earnings:
            return round(self.actual_earnings / hours, 2)
        return 0.0

    def __repr__(self):
        return (
            f"<CommittedShift id={self.id} driver={self.driver_id} "
            f"status={self.status} location={self.location_name}>"
        )


class GuaranteeLog(Base):
    """
    Guarantee Activation Audit Log (FR13)

    Records every guarantee activation and top-up calculation for
    auditing, research analysis, and compliance purposes.

    All predictions, commitments, and guarantee calculations are
    logged here for review and research evaluation (NFR11).
    """
    __tablename__ = "guarantee_logs"

    id = Column(Integer, primary_key=True, index=True)

    # REFERENCES
    committed_shift_id = Column(Integer, ForeignKey("committed_shifts.id"), nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # EVENT DETAILS
    event_type = Column(String(64), nullable=False)         # commitment, earnings_recorded, guarantee_activated, cancellation
    event_description = Column(String(512), nullable=True)

    # FINANCIAL DATA (snapshot at time of event)
    predicted_earnings = Column(Float, nullable=True)
    actual_earnings = Column(Float, nullable=True)
    guaranteed_minimum = Column(Float, nullable=True)
    topup_amount = Column(Float, nullable=True)
    guarantee_threshold = Column(Float, nullable=True)

    # ELIGIBILITY (snapshot)
    was_eligible = Column(Boolean, nullable=True)
    eligibility_reason = Column(String(256), nullable=True)

    # METADATA
    created_at = Column(DateTime, server_default=func.now())
    ip_address = Column(String(45), nullable=True)

    def __repr__(self):
        return f"<GuaranteeLog id={self.id} type={self.event_type} shift={self.committed_shift_id}>"
