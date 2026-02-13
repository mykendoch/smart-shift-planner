"""
Statistical Analysis Tools

Analyzes the Smart Shift Planner data to answer research questions:
1. How effective is AI shift scheduling?
2. Does income guarantee reduce volatility?
3. Impact on productivity/decision-making
4. System sustainability

Generates analysis reports and visualizations.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import statistics
from typing import List, Dict, Tuple
import json

sys.path.insert(0, str(Path(__file__).parent))

from src.database import SessionLocal
from src.models import Worker, Shift
from src.core.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger("analytics")


class StatisticalAnalyzer:
    """Analyze shift data to answer research questions."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.results = {}
    
    def get_all_shifts(self) -> List[Shift]:
        """Get all shifts from database."""
        return self.db.query(Shift).all()
    
    def get_worker_shifts(self, worker_id: int) -> List[Shift]:
        """Get all shifts for a specific worker."""
        return self.db.query(Shift).filter(Shift.worker_id == worker_id).all()
    
    # ========================================================================
    # RESEARCH QUESTION 1: Effectiveness of AI-based shift scheduling
    # ========================================================================
    
    def analyze_earnings_impact(self) -> Dict:
        """
        Analyze if following shift recommendations would increase earnings.
        
        Compares:
        - Actual earnings by hour worked
        - Peak hours (high earnings potential)
        - Off-peak hours (low earnings potential)
        """
        logger.info("Analyzing earnings impact of shift recommendations...")
        
        shifts = self.get_all_shifts()
        if not shifts:
            logger.warning("No shifts found")
            return {}
        
        # Group shifts by start hour to see patterns
        hourly_earnings = {}
        for shift in shifts:
            if not shift.start_time or not shift.earnings:
                continue
            
            hour = shift.start_time.hour
            if hour not in hourly_earnings:
                hourly_earnings[hour] = []
            hourly_earnings[hour].append(shift.earnings)
        
        # Calculate statistics by hour
        hour_stats = {}
        for hour in range(24):
            earnings_list = hourly_earnings.get(hour, [])
            if earnings_list:
                hour_stats[hour] = {
                    'count': len(earnings_list),
                    'total': sum(earnings_list),
                    'avg': sum(earnings_list) / len(earnings_list),
                    'max': max(earnings_list),
                    'min': min(earnings_list),
                    'stdev': statistics.stdev(earnings_list) if len(earnings_list) > 1 else 0
                }
        
        # Find peak hours (top 5)
        sorted_hours = sorted(hour_stats.items(), key=lambda x: x[1]['avg'], reverse=True)
        peak_hours = sorted_hours[:5]
        low_hours = sorted_hours[-5:]
        
        result = {
            'peak_hours': {
                hour: stats for hour, stats in peak_hours
            },
            'low_hours': {
                hour: stats for hour, stats in low_hours
            },
            'peak_avg_hourly': sum(s[1]['avg'] for s in peak_hours) / len(peak_hours),
            'low_avg_hourly': sum(s[1]['avg'] for s in low_hours) / len(low_hours),
            'earnings_increase_potential': (
                (sum(s[1]['avg'] for s in peak_hours) / len(peak_hours)) /
                (sum(s[1]['avg'] for s in low_hours) / len(low_hours))
            )
        }
        
        logger.info(f"  Peak hour average: ${result['peak_avg_hourly']:.2f}")
        logger.info(f"  Low hour average: ${result['low_avg_hourly']:.2f}")
        logger.info(f"  Potential earnings increase: {(result['earnings_increase_potential']-1)*100:.1f}%")
        
        return result
    
    # ========================================================================
    # RESEARCH QUESTION 2: Income guarantee reduces volatility
    # ========================================================================
    
    def analyze_income_volatility(self) -> Dict:
        """
        Analyze income volatility before and after income guarantee.
        
        Metrics:
        - Standard deviation of earnings
        - Coefficient of variation
        - Income stability index
        - Top-up impact on volatility
        """
        logger.info("Analyzing income volatility reduction...")
        
        shifts = self.get_all_shifts()
        earnings = [s.earnings for s in shifts if s.earnings]
        
        if not earnings:
            logger.warning("No earnings data")
            return {}
        
        # Volatility metrics
        mean_earnings = statistics.mean(earnings)
        stdev_earnings = statistics.stdev(earnings) if len(earnings) > 1 else 0
        coeff_variation = (stdev_earnings / mean_earnings) if mean_earnings > 0 else 0
        
        # Calculate with top-ups
        earnings_with_topup = []
        total_topups = 0
        
        for shift in shifts:
            if not shift.earnings or not shift.predicted_earnings:
                continue
            
            actual = shift.earnings
            predicted = shift.predicted_earnings
            expected = predicted * 0.9
            topup = max(0, expected - actual)
            total_topups += topup
            
            earnings_with_topup.append(actual + topup)
        
        mean_with_topup = statistics.mean(earnings_with_topup) if earnings_with_topup else 0
        stdev_with_topup = statistics.stdev(earnings_with_topup) if len(earnings_with_topup) > 1 else 0
        coeff_variation_with_topup = (stdev_with_topup / mean_with_topup) if mean_with_topup > 0 else 0
        
        # Calculate volatility reduction percentage
        volatility_reduction = (
            (stdev_earnings - stdev_with_topup) / stdev_earnings * 100
        ) if stdev_earnings > 0 else 0
        
        result = {
            'without_guarantee': {
                'mean': round(mean_earnings, 2),
                'stdev': round(stdev_earnings, 2),
                'coeff_variation': round(coeff_variation, 4),
                'min': min(earnings),
                'max': max(earnings),
                'range': max(earnings) - min(earnings)
            },
            'with_guarantee': {
                'mean': round(mean_with_topup, 2),
                'stdev': round(stdev_with_topup, 2),
                'coeff_variation': round(coeff_variation_with_topup, 4),
                'min': min(earnings_with_topup) if earnings_with_topup else 0,
                'max': max(earnings_with_topup) if earnings_with_topup else 0,
                'range': (max(earnings_with_topup) - min(earnings_with_topup)) if earnings_with_topup else 0
            },
            'volatility_reduction_pct': round(volatility_reduction, 1),
            'total_topups_paid': round(total_topups, 2),
            'topups_as_pct_earnings': round((total_topups / sum(earnings)) * 100, 1) if earnings else 0
        }
        
        logger.info(f"  Volatility reduction: {result['volatility_reduction_pct']}%")
        logger.info(f"  Total top-ups paid: ${result['total_topups_paid']:.2f}")
        logger.info(f"  Stability improvement: CV reduced from {result['without_guarantee']['coeff_variation']:.4f} to {result['with_guarantee']['coeff_variation']:.4f}")
        
        return result
    
    # ========================================================================
    # ADDITIONAL METRICS
    # ========================================================================
    
    def analyze_prediction_accuracy(self) -> Dict:
        """
        Analyze how accurate the earnings predictions were.
        
        Impacts the effectiveness of the income guarantee.
        """
        logger.info("Analyzing prediction accuracy...")
        
        shifts = self.get_all_shifts()
        differences = []
        accuracy_pcts = []
        
        for shift in shifts:
            if not shift.earnings or not shift.predicted_earnings:
                continue
            
            actual = shift.earnings
            predicted = shift.predicted_earnings
            difference = actual - predicted
            differences.append(difference)
            
            if predicted > 0:
                accuracy_pct = (actual / predicted) * 100
                accuracy_pcts.append(accuracy_pct)
        
        if not accuracy_pcts:
            return {}
        
        result = {
            'mean_accuracy_pct': round(statistics.mean(accuracy_pcts), 1),
            'median_accuracy_pct': round(statistics.median(accuracy_pcts), 1),
            'stdev_accuracy_pct': round(statistics.stdev(accuracy_pcts), 1) if len(accuracy_pcts) > 1 else 0,
            'under_prediction_pct': sum(1 for d in differences if d > 0) / len(differences) * 100,
            'over_prediction_pct': sum(1 for d in differences if d < 0) / len(differences) * 100,
            'mean_error': round(statistics.mean(differences), 2),
            'rmse': round((sum(d**2 for d in differences) / len(differences))**0.5, 2)
        }
        
        logger.info(f"  Mean prediction accuracy: {result['mean_accuracy_pct']}%")
        logger.info(f"  Over-predictions: {result['over_prediction_pct']:.1f}% of shifts")
        logger.info(f"  Under-predictions: {result['under_prediction_pct']:.1f}% of shifts")
        
        return result
    
    def analyze_worker_performance(self) -> Dict:
        """
        Analyze individual worker performance and earnings patterns.
        """
        logger.info("Analyzing worker performance...")
        
        workers = self.db.query(Worker).all()
        worker_stats = {}
        
        for worker in workers:
            shifts = self.get_worker_shifts(worker.id)
            if not shifts:
                continue
            
            earnings = [s.earnings for s in shifts if s.earnings]
            if not earnings:
                continue
            
            # Top-up calculation
            topups = []
            for shift in shifts:
                if shift.earnings and shift.predicted_earnings:
                    topup = max(0, shift.predicted_earnings * 0.9 - shift.earnings)
                    topups.append(topup)
            
            worker_stats[worker.name] = {
                'shifts_count': len(shifts),
                'total_earnings': round(sum(earnings), 2),
                'avg_earnings': round(statistics.mean(earnings), 2),
                'stdev_earnings': round(statistics.stdev(earnings), 2) if len(earnings) > 1 else 0,
                'peaks_at_hour': self._find_peak_hour(shifts),
                'total_topups': round(sum(topups), 2),
                'topup_count': len([t for t in topups if t > 0]),
                'topup_percentage': round(len([t for t in topups if t > 0]) / len(topups) * 100, 1) if topups else 0
            }
        
        return worker_stats
    
    def _find_peak_hour(self, shifts: List[Shift]) -> int:
        """Find the hour where a worker earned the most on average."""
        hourly_earnings = {}
        for shift in shifts:
            if shift.start_time and shift.earnings:
                hour = shift.start_time.hour
                if hour not in hourly_earnings:
                    hourly_earnings[hour] = []
                hourly_earnings[hour].append(shift.earnings)
        
        if not hourly_earnings:
            return -1
        
        avg_by_hour = {hour: statistics.mean(e) for hour, e in hourly_earnings.items()}
        return max(avg_by_hour, key=avg_by_hour.get)
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report."""
        logger.info("Generating analysis report...")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'data_summary': {
                'total_shifts': len(self.get_all_shifts()),
                'total_workers': self.db.query(Worker).count(),
                'date_range_days': self._get_data_range_days()
            },
            'research_question_1_earnings_impact': self.analyze_earnings_impact(),
            'research_question_2_volatility_reduction': self.analyze_income_volatility(),
            'prediction_accuracy': self.analyze_prediction_accuracy(),
            'worker_performance': self.analyze_worker_performance()
        }
        
        return json.dumps(report, indent=2, default=str)
    
    def _get_data_range_days(self) -> int:
        """Calculate data range in days."""
        shifts = self.get_all_shifts()
        if not shifts:
            return 0
        
        dates = [s.start_time for s in shifts if s.start_time]
        if not dates:
            return 0
        
        return (max(dates) - min(dates)).days
    
    def run(self):
        """Run all analyses and save report."""
        try:
            logger.info("="*70)
            logger.info("STATISTICAL ANALYSIS - SMART SHIFT PLANNER")
            logger.info("="*70)
            
            report = self.generate_report()
            
            # Save report
            report_path = Path("logs") / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                f.write(report)
            
            logger.info(f"✓ Report saved to: {report_path}")
            logger.info("="*70)
            
            return report
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}", exc_info=True)
            raise
        finally:
            self.db.close()


if __name__ == "__main__":
    analyzer = StatisticalAnalyzer()
    report = analyzer.run()
