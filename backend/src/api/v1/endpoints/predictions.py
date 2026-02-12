"""Machine Learning / Prediction endpoints.

Exposes ML models for:
- Earnings prediction
- Demand forecasting
- Shift recommendations
"""
from fastapi import APIRouter, Query
from datetime import datetime
from typing import List, Dict

from src.ml.predictors import EarningsPredictor, DemandForecaster, ShiftOptimizer

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])

# Initialize models
earnings_predictor = EarningsPredictor()
demand_forecaster = DemandForecaster()
shift_optimizer = ShiftOptimizer()


@router.get("/earnings")
def predict_earnings(
    hour: int = Query(..., ge=0, le=23),
    day_of_week: int = Query(..., ge=0, le=6),
    location: str = Query("downtown"),
    demand_level: float = Query(0.5, ge=0, le=1),
):
    """
    Predict hourly earnings for a given time and location.

    **Parameters:**
    - hour (0-23): Hour of day
    - day_of_week (0-6): 0=Monday, 6=Sunday
    - location: downtown, airport, highway, residential
    - demand_level (0-1): Current demand level

    **Returns:**
    Estimated hourly earnings
    """
    earnings = earnings_predictor.predict(hour, day_of_week, location, demand_level)
    return {
        "hour": hour,
        "day_of_week": day_of_week,
        "location": location,
        "demand_level": demand_level,
        "predicted_hourly_earnings": round(earnings, 2),
    }


@router.get("/demand-forecast")
def forecast_demand(location: str = Query("downtown")):
    """
    Get demand forecast for all hours at a location.

    **Parameters:**
    - location: downtown, airport, highway, residential

    **Returns:**
    Demand levels (0-1) for each hour
    """
    forecast = {
        hour: demand_forecaster.forecast(location, hour)
        for hour in range(24)
    }
    return {
        "location": location,
        "hourly_demand": forecast,
        "peak_hours": [
            {"hour": h, "demand": d}
            for h, d in demand_forecaster.forecast_peak_hours(location, top_n=5)
        ]
    }


@router.get("/recommend-shifts")
def recommend_shifts(
    location: str = Query("downtown"),
    date_type: str = Query("weekday"),
    duration_hours: float = Query(4.0),
    top_n: int = Query(3, ge=1, le=10),
):
    """
    Get AI recommendations for optimal shift times.

    **Parameters:**
    - location: downtown, airport, highway, residential
    - date_type: weekday or weekend
    - duration_hours: Desired shift duration (hours)
    - top_n: Number of recommendations to return

    **Returns:**
    List of top shift recommendations by predicted earnings
    """
    recommendations = shift_optimizer.recommend_shifts(
        location=location,
        date_type=date_type,
        duration_hours=duration_hours,
        top_n=top_n
    )
    return {
        "location": location,
        "date_type": date_type,
        "duration_hours": duration_hours,
        "recommendations": recommendations,
    }
