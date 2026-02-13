"""
Volatility Analysis Service

Calculates earnings variance and stability metrics to answer:
"To what extent does income guarantee reduce income volatility?"
"""
import math
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.models.shift import Shift
from src.models.eligibility_metrics import VolatilityMetrics


class VolatilityAnalyzer:
    """
    Analyzes earnings volatility and income stability.
    
    Key metrics:
    - Standard Deviation: Spread of earnings
    - Coefficient of Variation: Std Dev / Mean (normalized)
    - Range: Max - Min
    - Quartiles: 25th, 50th (median), 75th percentiles
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_statistics(self, earnings: List[float]) -> Dict:
        """
        Calculate statistical measures of earnings.
        
        Returns:
        {
            "mean": average earnings,
            "std_dev": standard deviation,
            "variance": variance,
            "coefficient_variation": CV percentage,
            "min": minimum earning,
            "max": maximum earning,
            "range": max - min,
            "percentiles": {"q1": ..., "median": ..., "q3": ...},
            "iqr": interquartile range
        }
        """
        if not earnings:
            return {
                "mean": 0, "std_dev": 0, "variance": 0,
                "coefficient_variation": 0, "min": 0, "max": 0,
                "range": 0, "percentiles": {}, "iqr": 0
            }
        
        n = len(earnings)
        sorted_earnings = sorted(earnings)
        
        # Mean
        mean = sum(earnings) / n
        
        # Variance and Standard Deviation
        variance = sum((x - mean) ** 2 for x in earnings) / n
        std_dev = math.sqrt(variance)
        
        # Coefficient of Variation (normalize by mean)
        cv = (std_dev / mean * 100) if mean > 0 else 0
        
        # Range
        min_earning = min(earnings)
        max_earning = max(earnings)
        range_val = max_earning - min_earning
        
        # Percentiles (using linear interpolation)
        def percentile(data, p):
            index = (p / 100) * (len(data) - 1)
            lower = int(index)
            upper = lower + 1
            if upper >= len(data):
                return data[lower]
            weight = index - lower
            return data[lower] * (1 - weight) + data[upper] * weight
        
        q1 = percentile(sorted_earnings, 25)
        median = percentile(sorted_earnings, 50)
        q3 = percentile(sorted_earnings, 75)
        iqr = q3 - q1
        
        return {
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "variance": round(variance, 2),
            "coefficient_variation": round(cv, 2),
            "min": round(min_earning, 2),
            "max": round(max_earning, 2),
            "range": round(range_val, 2),
            "percentiles": {
                "q1": round(q1, 2),
                "median": round(median, 2),
                "q3": round(q3, 2)
            },
            "iqr": round(iqr, 2),
            "sample_size": n
        }
    
    def analyze_worker_volatility(self, worker_id: int, days: int = 30) -> Dict:
        """
        Analyze volatility for a worker over time period.
        
        Compares:
        1. Raw earnings (without guarantee)
        2. Earnings after top-ups (with guarantee)
        
        Shows impact of income guarantee on stability.
        """
        # Get shifts in period
        cutoff = datetime.utcnow() - timedelta(days=days)
        shifts = self.db.query(Shift).filter(
            Shift.worker_id == worker_id,
            Shift.created_at >= cutoff
        ).all()
        
        if not shifts:
            return {"error": f"No shifts found for worker {worker_id} in last {days} days"}
        
        # Calculate earnings with and without guarantee
        raw_earnings = []        # Actual earnings (no guarantee)
        guaranteed_earnings = [] # Earnings after top-up
        
        for shift in shifts:
            actual = shift.earnings or 0.0
            predicted = shift.predicted_earnings or 0.0
            
            # Raw (no guarantee)
            raw_earnings.append(actual)
            
            # With guarantee (add top-up if applicable)
            expected = predicted * 0.9  # 90% threshold
            topup = max(0.0, expected - actual)
            with_guarantee = actual + topup
            guaranteed_earnings.append(with_guarantee)
        
        # Calculate statistics
        stats_raw = self.calculate_statistics(raw_earnings)
        stats_guaranteed = self.calculate_statistics(guaranteed_earnings)
        
        # Calculate reduction in volatility
        if stats_raw["std_dev"] > 0:
            volatility_reduction = (
                (stats_raw["std_dev"] - stats_guaranteed["std_dev"]) / 
                stats_raw["std_dev"] * 100
            )
        else:
            volatility_reduction = 0
        
        if stats_raw["coefficient_variation"] > 0:
            cv_reduction = (
                (stats_raw["coefficient_variation"] - stats_guaranteed["coefficient_variation"]) /
                stats_raw["coefficient_variation"] * 100
            )
        else:
            cv_reduction = 0
        
        return {
            "worker_id": worker_id,
            "period": f"Last {days} days",
            "without_guarantee": stats_raw,
            "with_guarantee": stats_guaranteed,
            "impact": {
                "volatility_reduction_percent": round(volatility_reduction, 2),
                "cv_reduction_percent": round(cv_reduction, 2),
                "earnings_floor_raw": min(raw_earnings) if raw_earnings else 0,
                "earnings_floor_with_guarantee": min(guaranteed_earnings) if guaranteed_earnings else 0,
                "improvement": "Income guarantee reduced volatility by {:.1f}%".format(volatility_reduction)
            }
        }
    
    def store_volatility_metrics(self, worker_id: int, days: int = 30) -> VolatilityMetrics:
        """
        Calculate and store volatility metrics for a worker.
        
        Call periodically (e.g., weekly) to track volatility over time.
        """
        analysis = self.analyze_worker_volatility(worker_id, days)
        
        if "error" in analysis:
            return None
        
        # Create database record
        metrics = VolatilityMetrics(
            worker_id=worker_id,
            period_start=datetime.utcnow() - timedelta(days=days),
            period_end=datetime.utcnow(),
            
            # Without guarantee
            earnings_without_guarantee_mean=analysis["without_guarantee"]["mean"],
            earnings_without_guarantee_std_dev=analysis["without_guarantee"]["std_dev"],
            earnings_without_guarantee_cv=analysis["without_guarantee"]["coefficient_variation"],
            earnings_without_guarantee_min=analysis["without_guarantee"]["min"],
            earnings_without_guarantee_max=analysis["without_guarantee"]["max"],
            earnings_without_guarantee_range=analysis["without_guarantee"]["range"],
            earnings_without_guarantee_q1=analysis["without_guarantee"]["percentiles"]["q1"],
            earnings_without_guarantee_median=analysis["without_guarantee"]["percentiles"]["median"],
            earnings_without_guarantee_q3=analysis["without_guarantee"]["percentiles"]["q3"],
            earnings_without_guarantee_iqr=analysis["without_guarantee"]["iqr"],
            
            # With guarantee
            earnings_with_guarantee_mean=analysis["with_guarantee"]["mean"],
            earnings_with_guarantee_std_dev=analysis["with_guarantee"]["std_dev"],
            earnings_with_guarantee_cv=analysis["with_guarantee"]["coefficient_variation"],
            earnings_with_guarantee_min=analysis["with_guarantee"]["min"],
            earnings_with_guarantee_max=analysis["with_guarantee"]["max"],
            earnings_with_guarantee_range=analysis["with_guarantee"]["range"],
            
            # Impact
            volatility_reduction_percent=analysis["impact"]["volatility_reduction_percent"],
            cv_reduction_percent=analysis["impact"]["cv_reduction_percent"],
            earnings_floor_amount=analysis["impact"]["earnings_floor_raw"],
            
            sample_size=analysis["without_guarantee"]["sample_size"],
            analysis_type="monthly"
        )
        
        self.db.add(metrics)
        self.db.commit()
        self.db.refresh(metrics)
        
        return metrics
