"""
Prediction Accuracy Analysis Service

Measures model performance against ground truth data to answer:
"Are our earnings predictions accurate enough to be trusted?"
"""
import math
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.eligibility_metrics import PredictionAccuracy


class AccuracyAnalyzer:
    """
    Calculates and tracks prediction accuracy metrics.
    
    Metrics:
    - MAE: Mean Absolute Error ($ difference)
    - MAPE: Mean Absolute Percentage Error (%)
    - RMSE: Root Mean Squared Error
    - R²: Goodness of fit (0-1)
    """
    
    # Thresholds for acceptable accuracy
    ACCURACY_THRESHOLDS = {
        "excellent": {"mape_max": 10, "mae_max": 5},      # ±10% or $5
        "good": {"mape_max": 15, "mae_max": 10},          # ±15% or $10
        "acceptable": {"mape_max": 20, "mae_max": 15},    # ±20% or $15
        "poor": {"mape_max": 30, "mae_max": 25},          # >20% error
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_accuracy_metrics(self, predictions: List[float], 
                                   actuals: List[float]) -> Dict:
        """
        Calculate all accuracy metrics.
        
        Args:
            predictions: List of predicted values
            actuals: List of actual values
        
        Returns:
            Dictionary with all accuracy metrics
        """
        if not predictions or not actuals or len(predictions) != len(actuals):
            return {"error": "Invalid input"}
        
        n = len(predictions)
        
        # Absolute errors
        abs_errors = [abs(p - a) for p, a in zip(predictions, actuals)]
        signed_errors = [p - a for p, a in zip(predictions, actuals)]
        
        # MAE: Mean Absolute Error
        mae = sum(abs_errors) / n
        
        # MAPE: Mean Absolute Percentage Error
        pct_errors = []
        for p, a in zip(predictions, actuals):
            if a != 0:
                pct_errors.append(abs(p - a) / a * 100)
        mape = sum(pct_errors) / len(pct_errors) if pct_errors else 0
        
        # RMSE: Root Mean Squared Error
        squared_errors = [e ** 2 for e in signed_errors]
        mse = sum(squared_errors) / n
        rmse = math.sqrt(mse)
        
        # Mean prediction and actual
        mean_actual = sum(actuals) / n
        
        # R² Score: Goodness of fit (0-1, higher is better)
        ss_res = sum(squared_errors)
        ss_tot = sum((a - mean_actual) ** 2 for a in actuals)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        r2 = max(0, min(1, r2))  # Clamp to 0-1
        
        return {
            "mae": round(mae, 2),
            "mape": round(mape, 2),
            "rmse": round(rmse, 2),
            "r2_score": round(r2, 3),
            "mean_prediction": round(sum(predictions) / n, 2),
            "mean_actual": round(mean_actual, 2),
            "sample_size": n,
            "accuracy_level": self._assess_accuracy(mae, mape)
        }
    
    def _assess_accuracy(self, mae: float, mape: float) -> str:
        """Assess accuracy level based on thresholds"""
        if mape <= self.ACCURACY_THRESHOLDS["excellent"]["mape_max"]:
            return "Excellent"
        elif mape <= self.ACCURACY_THRESHOLDS["good"]["mape_max"]:
            return "Good"
        elif mape <= self.ACCURACY_THRESHOLDS["acceptable"]["mape_max"]:
            return "Acceptable"
        else:
            return "Poor"
    
    def record_prediction_accuracy(self, shift_id: int, 
                                   predicted: float, actual: float,
                                   location: str, hour: int, day: int) -> PredictionAccuracy:
        """Record a prediction and its actual outcome"""
        
        abs_error = abs(predicted - actual)
        pct_error = (abs_error / actual * 100) if actual > 0 else 0
        
        record = PredictionAccuracy(
            shift_id=shift_id,
            predicted_earnings=predicted,
            actual_earnings=actual,
            absolute_error=abs_error,
            percentage_error=pct_error,
            signed_error=predicted - actual,
            location=location,
            hour_of_day=hour,
            day_of_week=day,
            prediction_time=datetime.utcnow(),
            actual_time=datetime.utcnow()
        )
        
        self.db.add(record)
        self.db.commit()
        
        return record
    
    def get_model_accuracy(self, location: str = None, 
                          hour: int = None) -> Dict:
        """
        Get prediction accuracy for model overall or by location/hour.
        
        Can be used to:
        - Verify model meets minimum accuracy threshold
        - Identify weak areas (location/time with poor accuracy)
        - Monitor accuracy over time
        """
        query = self.db.query(PredictionAccuracy)
        
        if location:
            query = query.filter(PredictionAccuracy.location == location)
        if hour is not None:
            query = query.filter(PredictionAccuracy.hour_of_day == hour)
        
        records = query.all()
        
        if not records:
            return {"error": "No accuracy data available"}
        
        predictions = [r.predicted_earnings for r in records]
        actuals = [r.actual_earnings for r in records]
        
        metrics = self.calculate_accuracy_metrics(predictions, actuals)
        
        return {
            "filter": f"location={location or 'all'}, hour={hour or 'all'}",
            **metrics
        }
    
    def get_model_accuracy_summary(self) -> Dict:
        """
        Get overall model accuracy summary with location and hourly breakdowns.
        """
        overall = self.get_model_accuracy()
        
        by_location = {}
        for location in ["downtown", "airport", "highway", "residential"]:
            result = self.get_model_accuracy(location=location)
            if "error" not in result:
                by_location[location] = result
        
        by_hour = {}
        for hour in range(24):
            result = self.get_model_accuracy(hour=hour)
            if "error" not in result:
                by_hour[str(hour)] = result
        
        return {
            "overall": overall,
            "by_location": by_location,
            "by_hour": by_hour,
            "meets_minimum_threshold": (
                overall.get("mape", float("inf")) <= 
                self.ACCURACY_THRESHOLDS["acceptable"]["mape_max"]
            )
        }
