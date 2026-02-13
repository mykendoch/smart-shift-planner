"""
Worker Eligibility Metrics Model

Tracks worker performance metrics needed for income guarantee eligibility.
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, Boolean, String, func
from sqlalchemy.orm import relationship
from src.database import Base


class WorkerEligibility(Base):
    """
    Tracks worker eligibility for income guarantee protection.
    
    Eligibility rules (configurable):
    - Active hours >= MIN_ACTIVE_HOURS (default: 20/week)
    - Acceptance rate >= MIN_ACCEPTANCE_RATE (default: 95%)
    - Cancellation rate <= MAX_CANCELLATION_RATE (default: 5%)
    - Account active (not suspended/disabled)
    """
    __tablename__ = "worker_eligibility"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to worker
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, unique=True, index=True)
    
    # Performance metrics (calculated from shifts)
    active_hours_week = Column(Float, default=0.0)      # Hours worked this week
    total_active_hours = Column(Float, default=0.0)     # Total hours all-time
    acceptance_rate = Column(Float, default=1.0)        # % of offers accepted (0-1)
    cancellation_rate = Column(Float, default=0.0)      # % of shifts cancelled (0-1)
    average_rating = Column(Float, default=5.0)         # Star rating (1-5)
    
    # Status
    is_eligible = Column(Boolean, default=True)         # Overall eligibility
    eligibility_reason = Column(String, default="")     # Why ineligible (if not)
    
    # Metadata
    last_updated = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    account_active = Column(Boolean, default=True)      # Not suspended


class VolatilityMetrics(Base):
    """
    Stores volatility metrics for analyzing earnings stability.
    
    Useful for:
    - Answering research question 2 (does guarantee reduce volatility?)
    - Tracking impact of system usage
    - Comparing workers
    """
    __tablename__ = "volatility_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to worker
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    
    # Period being measured
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # WITHOUT guarantee (raw earnings)
    earnings_without_guarantee_mean = Column(Float)
    earnings_without_guarantee_std_dev = Column(Float)
    earnings_without_guarantee_cv = Column(Float)        # Coefficient of variation %
    earnings_without_guarantee_min = Column(Float)
    earnings_without_guarantee_max = Column(Float)
    earnings_without_guarantee_range = Column(Float)
    earnings_without_guarantee_q1 = Column(Float)        # 25th percentile
    earnings_without_guarantee_median = Column(Float)    # 50th percentile
    earnings_without_guarantee_q3 = Column(Float)        # 75th percentile
    earnings_without_guarantee_iqr = Column(Float)       # Q3 - Q1
    
    # WITH guarantee (actual earnings after top-ups)
    earnings_with_guarantee_mean = Column(Float)
    earnings_with_guarantee_std_dev = Column(Float)
    earnings_with_guarantee_cv = Column(Float)
    earnings_with_guarantee_min = Column(Float)
    earnings_with_guarantee_max = Column(Float)
    earnings_with_guarantee_range = Column(Float)
    
    # Impact analysis
    volatility_reduction_percent = Column(Float)         # (old_std - new_std) / old_std × 100
    cv_reduction_percent = Column(Float)
    earnings_floor_amount = Column(Float)                # Minimum earnings with guarantee
    
    # Metadata
    sample_size = Column(Integer)                        # Number of shifts analyzed
    created_at = Column(DateTime, server_default=func.now())
    analysis_type = Column(String, default="weekly")     # weekly, monthly, overall


class PredictionAccuracy(Base):
    """
    Records individual prediction accuracy for analysis and model improvement.
    
    Accuracy metrics:
    - MAE: Mean Absolute Error (average $ difference)
    - MAPE: Mean Absolute Percentage Error (% error)
    - RMSE: Root Mean Squared Error (penalizes large errors)
    - R²: Coefficient of determination (0-1 goodness of fit)
    """
    __tablename__ = "prediction_accuracy"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to shift
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False, index=True)
    
    # Prediction details
    predicted_earnings = Column(Float, nullable=False)
    actual_earnings = Column(Float, nullable=False)
    
    # Error calculations
    absolute_error = Column(Float)      # |predicted - actual|
    percentage_error = Column(Float)    # (|predicted - actual| / actual) × 100
    signed_error = Column(Float)        # predicted - actual (can be negative)
    
    # Context
    prediction_time = Column(DateTime)  # When prediction was made
    actual_time = Column(DateTime)      # When shift occurred
    location = Column(String)
    hour_of_day = Column(Integer)
    day_of_week = Column(Integer)
    
    # Metadata
    model_version = Column(String, default="1.0")
    recorded_at = Column(DateTime, server_default=func.now())


class WorkerSurvey(Base):
    """
    Worker feedback survey responses.
    
    Stores anonymised survey data about:
    - Income stress levels
    - Work schedule satisfaction
    - App usefulness
    - Decision-making improvements
    """
    __tablename__ = "worker_surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to worker (kept for non-anonymized access, hashed for export)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    
    # Survey Responses (Likert scale 1-5)
    income_stress_level = Column(Integer)                # 1=very stressed, 5=not stressed
    work_schedule_satisfaction = Column(Integer)         # 1=very unsatisfied, 5=very satisfied
    app_usefulness = Column(Integer)                     # 1=not useful, 5=very useful
    decision_making_improvement = Column(Integer)        # 1=worse, 5=much better
    shift_planning_ease = Column(Integer)                # 1=difficult, 5=very easy
    earnings_stability = Column(Integer)                 # 1=very unstable, 5=very stable
    
    # Open-ended responses
    positive_feedback = Column(String(500), nullable=True)
    negative_feedback = Column(String(500), nullable=True)
    suggestions = Column(String(500), nullable=True)
    
    # Metadata
    response_date = Column(DateTime, server_default=func.now())
    days_using_system = Column(Integer)                  # Days since registration
    num_shifts_using_system = Column(Integer)            # Number of shifts completed with system
    
    # Anonymization
    is_anonymized = Column(Boolean, default=False)       # For export
    worker_id_hash = Column(String(64), nullable=True)   # SHA-256 hash for anonymized reports
