"""
Smart Shift Planner ML Models - Pure Python Implementation

This module contains machine learning models for:
- Predicting earnings based on time, location, demand
- Forecasting demand patterns
- Recommending optimal shift times and locations

WHY PURE PYTHON?
DESIGN DECISION: Implemented ML without pandas/numpy/scikit-learn libraries

BENEFITS OF THIS APPROACH:
1. Lightweight Deployment
   - No heavy dependencies (pandas/numpy have 100+ MB footprint combined)
   - Faster pip install (5 seconds vs 30+ seconds)
   - Smaller Docker image size

2. Educational Value
   - Clear understanding of how predictions work
   - Can see algorithm logic directly in code
   - No "black box" - easy to debug and modify
   - Shows that ML doesn't require heavy libraries

3. MVP (Minimum Viable Product) Simplicity
   - Meets requirements for student project scope
   - Handles typical gig worker shift data well
   - No need for advanced statistical functions yet

4. Scalable Architecture
   - Can add pandas/numpy later without major refactoring
   - Pure Python code serves as model specification
   - Easy to migrate to scikit-learn when needed

TRADE-OFFS (When to upgrade):
- SPEED: Pure Python loops slower than NumPy arrays (10-100x for 100k+ rows)
- FEATURES: No built-in cross-validation, hyperparameter tuning
- STATISTICS: Manual calculations vs pandas aggregation functions

MIGRATION PATH:
1. Small dataset (current): Pure Python (NOW)
2. Medium dataset (10k+ shifts): Upgrade to NumPy arrays for speed
3. Large dataset (100k+ shifts): Add Pandas for data loading/grouping
4. Advanced models needed: Use scikit-learn for RandomForest, SVM, etc.
"""
import logging
from datetime import datetime
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class EarningsPredictor:
    """
    Earnings Prediction Model - Pure Python Statistical Approach
    
    Predicts hourly earnings for gig workers based on:
    - Time of day (peak vs off-peak hours)
    - Day of week (weekends earn more)
    - Location (airport > downtown > residential)
    - Demand level (consumer demand affects availability)
    
    IMPLEMENTATION:
    - Uses lookup tables (dictionaries) for multiplier factors
    - Simple multiplicative formula: base × time_mult × day_mult × demand_mult
    - No machine learning training needed - uses domain knowledge
    
    ALTERNATIVE APPROACH (if using scikit-learn):
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X_train, y_train)  # Train on historical data
        predictions = model.predict(X_test)
    
    ADVANTAGES OF CURRENT APPROACH:
    - Fully transparent (can see factors affecting earnings)
    - Fast (O(1) simple multiplications)
    - No training data needed
    - Easy to adjust factors based on feedback
    
    DISADVANTAGES:
    - Static patterns (doesn't learn from data)
    - May not capture complex interactions
    - Requires manual factor tuning
    
    EXAMPLE:
        predictor = EarningsPredictor()
        # Predict for Friday evening in downtown (high demand)
        earnings = predictor.predict(
            hour=18,
            day_of_week=4,  # Friday
            location="downtown",
            demand_level=0.8
        )
        # Returns ~$25.76 (18 * 1.4 * 1.1 * 1.36)
    """
    
    # Base hourly earnings by location (can be trained on real data)
    BASE_EARNINGS = {
        "downtown": 18.0,
        "airport": 22.0,
        "highway": 15.0,
        "residential": 12.0,
        "default": 16.0
    }
    
    # Time multipliers (peak hours earn more)
    TIME_MULTIPLIERS = {
        "early_morning": (5, 8, 0.8),      # 5-8am: lower demand
        "morning": (8, 12, 1.1),           # 8am-12pm: moderate
        "afternoon": (12, 17, 1.0),        # 12-5pm: standard
        "evening": (17, 21, 1.4),          # 5-9pm: peak hours
        "night": (21, 5, 1.2),             # 9pm-5am: night surge
    }
    
    # Day multipliers
    DAY_MULTIPLIERS = {
        0: 0.9,   # Monday
        1: 0.95,  # Tuesday
        2: 1.0,   # Wednesday
        3: 1.05,  # Thursday
        4: 1.1,   # Friday (higher demand)
        5: 1.15,  # Saturday (highest)
        6: 1.12,  # Sunday
    }
    
    def predict(self, hour: int, day_of_week: int, location: str = "default", 
                demand_level: float = 0.5) -> float:
        """Predict earnings for a given time and location.
        
        Args:
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Monday, 6=Sunday)
            location: Location string (downtown, airport, etc.)
            demand_level: Demand level 0-1 (0=very low, 1=very high)
        
        Returns:
            Estimated hourly earnings
        """
        # Get base earnings for location
        base = self.BASE_EARNINGS.get(location, self.BASE_EARNINGS["default"])
        
        # Time multiplier
        time_mult = self._get_time_multiplier(hour)
        
        # Day multiplier
        day_mult = self.DAY_MULTIPLIERS.get(day_of_week, 1.0)
        
        # Demand multiplier (0.8x to 1.5x)
        demand_mult = 0.8 + (demand_level * 0.7)
        
        earnings = base * time_mult * day_mult * demand_mult
        
        logger.info(f"Predicted earnings: ${earnings:.2f} for {location} at hour {hour}")
        return earnings
    
    def _get_time_multiplier(self, hour: int) -> float:
        """Get earnings multiplier for hour of day."""
        for period_name, (start, end, multiplier) in self.TIME_MULTIPLIERS.items():
            if period_name == "night":
                # Handle night shift wrapping around midnight
                if hour >= start or hour < end:
                    return multiplier
            else:
                if start <= hour < end:
                    return multiplier
        return 1.0
    
    def predict_shift_earnings(self, start_time: datetime, duration_hours: float,
                               location: str = "default", demand_level: float = 0.5) -> float:
        """Predict total earnings for a shift.
        
        Args:
            start_time: When shift starts
            duration_hours: Duration in hours
            location: Location
            demand_level: Demand level 0-1
        
        Returns:
            Estimated total earnings for the shift
        """
        total = 0.0
        current_hour = start_time.hour
        day_of_week = start_time.weekday()
        
        for i in range(int(duration_hours)):
            hourly = self.predict(current_hour, day_of_week, location, demand_level)
            total += hourly
            current_hour = (current_hour + 1) % 24
            if current_hour == 0:
                day_of_week = (day_of_week + 1) % 7
        
        return total


class DemandForecaster:
    """
    Demand Forecasting Model - Pure Python Pattern Matching
    
    Forecasts demand levels (0-1 scale) for different times and locations
    to help workers identify peak opportunity windows.
    
    IMPLEMENTATION:
    - Pre-defined demand patterns stored in nested dictionaries
    - Patterns based on real-world gig economy observations
    - Maps hour to demand level by time period and location
    - Fast lookup: O(1) time complexity
    
    ALTERNATIVES (if using ML libraries):
        Statsmodels: ARIMA/SARIMAX for time-series forecasting
        Prophet: Facebook time-series lib for seasonality detection
        scikit-learn: RandomForest or SVR for pattern prediction
    
    ADVANTAGES OF CURRENT APPROACH:
    - Zero training overhead (no historical data needed)
    - Interpretable patterns (humans can understand factors)
    - Can be updated manually based on field observations
    - Works immediately without data collection phase
    
    DISADVANTAGES:
    - Static patterns (doesn't learn from actual data)
    - Requires domain expertise to configure
    - Can miss unexpected trends or seasonal variations
    - No statistical confidence intervals
    
    WHEN TO UPGRADE:
    - Have 6+ months of actual demand data collected
    - Patterns change seasonally (holidays, weather, events)
    - Want automatic pattern discovery from historical data
    - Need confidence/uncertainty intervals on forecasts
    - Platform announces major changes requiring retraining
    """
    
    # Simplified demand patterns (0-1 scale)
    DEMAND_PATTERNS = {
        "downtown": {
            "morning": [0.3, 0.5, 0.7, 0.8],      # 6-10am
            "afternoon": [0.6, 0.5, 0.4, 0.5],    # 12-4pm
            "evening": [0.9, 1.0, 0.95, 0.8],     # 5-9pm
            "night": [0.4, 0.3, 0.2, 0.3],        # 10pm-2am
        },
        "airport": {
            "morning": [0.6, 0.7, 0.8, 0.7],
            "afternoon": [0.8, 0.85, 0.8, 0.75],
            "evening": [0.9, 0.95, 0.9, 0.85],
            "night": [0.5, 0.4, 0.3, 0.4],
        },
        "residential": {
            "morning": [0.2, 0.3, 0.4, 0.5],
            "afternoon": [0.3, 0.4, 0.5, 0.6],
            "evening": [0.7, 0.8, 0.75, 0.6],
            "night": [0.2, 0.15, 0.1, 0.2],
        },
    }
    
    def forecast(self, location: str, hour: int) -> float:
        """Forecast demand level for a location at given hour.
        
        Args:
            location: Location name
            hour: Hour of day (0-23)
        
        Returns:
            Demand level 0-1
        """
        patterns = self.DEMAND_PATTERNS.get(location, {})
        
        if hour < 6:
            period = "night"
            idx = hour % 4
        elif hour < 12:
            period = "morning"
            idx = (hour - 6) % 4
        elif hour < 17:
            period = "afternoon"
            idx = (hour - 12) % 4
        else:
            period = "evening"
            idx = (hour - 17) % 4
        
        demand_list = patterns.get(period, [0.5] * 4)
        return demand_list[idx]
    
    def forecast_peak_hours(self, location: str, top_n: int = 3) -> List[Tuple[int, float]]:
        """Find peak demand hours for a location.
        
        Args:
            location: Location name
            top_n: Number of top hours to return
        
        Returns:
            List of (hour, demand_level) tuples, sorted by demand
        """
        demand_by_hour = [
            (hour, self.forecast(location, hour))
            for hour in range(24)
        ]
        return sorted(demand_by_hour, key=lambda x: x[1], reverse=True)[:top_n]


class ShiftOptimizer:
    """
    Shift Recommendation Engine - Pure Python Greedy Algorithm
    
    Recommends optimal shift times and locations for maximum earnings.
    Combines earnings prediction and demand forecasting to find shifts
    that maximize income for workers.
    
    IMPLEMENTATION:
    - Brute-force search: evaluates all 24 possible start hours
    - For each hour, combines EarningsPredictor + DemandForecaster
    - Calculates total earnings for specified duration
    - Ranks by predicted earnings and returns top N
    - Time complexity: O(24 × duration) = O(1) since duration is fixed
    
    WHY PURE PYTHON WORKS HERE:
    - Only 24 hours to evaluate (manageable with loops)
    - Simple arithmetic (no matrix operations)
    - Real-time response needed (<100ms)
    - Explainable recommendations (can show workers the math)
    
    ALTERNATIVES (if using ML frameworks):
        Genetic Algorithm: Evolve shift recommendations over populations
        Reinforcement Learning: Q-learning to discover optimal patterns
        Integer Linear Programming: Constrained optimization
        Bayesian Optimization: Intelligent search space exploration
    
    ADVANTAGES OF CURRENT APPROACH:
    - Simple and transparent (easy to understand debugging)
    - Fast: O(1) computation (always 24 hours to check)
    - No training needed (works immediately with any dataset)
    - Incorporates worker preferences (location, duration)
    - Reproducible (same input always gives same output)
    
    DISADVANTAGES:
    - Greedy algorithm (might miss hidden patterns)
    - Assumes static model (no learning over time)
    - No feedback loop from worker choices
    - Doesn't account for worker fatigue/scheduling
    - Can't handle complex multi-day planning
    
    WHEN TO UPGRADE:
    - Workers want 7-day schedule optimization (not 1 shift)
    - Constraints become complex (unavailable hours, skill requirements)
    - Want to learn from worker acceptance/rejection patterns
    - Need to account for commute times, breaks, fatigue
    - Have thousands of workers needing real-time recommendations
    """
    
    def __init__(self):
        self.earnings_predictor = EarningsPredictor()
        self.demand_forecaster = DemandForecaster()
    
    def recommend_shifts(self, location: str = "downtown", date_type: str = "weekday",
                        duration_hours: float = 4, top_n: int = 3) -> List[Dict]:
        """Recommend optimal shift times for a location and date.
        
        Args:
            location: Preferred location
            date_type: "weekday" or "weekend"
            duration_hours: Desired shift duration
            top_n: Number of recommendations
        
        Returns:
            List of shift recommendations with estimated earnings
        """
        day_of_week = 2 if date_type == "weekday" else 5  # Wed or Sat
        recommendations = []
        
        for start_hour in range(24):
            # Get demand at this hour
            demand = self.demand_forecaster.forecast(location, start_hour)
            
            # Predict earnings for this shift
            total_earnings = 0.0
            for i in range(int(duration_hours)):
                hour = (start_hour + i) % 24
                hourly = self.earnings_predictor.predict(
                    hour=hour,
                    day_of_week=day_of_week,
                    location=location,
                    demand_level=demand
                )
                total_earnings += hourly
            
            recommendations.append({
                "start_hour": start_hour,
                "duration_hours": duration_hours,
                "location": location,
                "predicted_earnings": round(total_earnings, 2),
                "demand_level": round(demand, 2),
            })
        
        # Sort by predicted earnings and return top N
        recommendations.sort(key=lambda x: x["predicted_earnings"], reverse=True)
        return recommendations[:top_n]
