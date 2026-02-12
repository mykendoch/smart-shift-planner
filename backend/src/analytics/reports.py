"""
Analytics and Reporting Module

Provides earnings analysis, comparisons, and visualization data for:
- Earnings trend analysis (actual vs predicted)
- Worker performance reports
- Income guarantee impact analysis
- Demand pattern visualizations
- Historical comparisons

This module fulfills the "Data visualization tools" requirement from the project spec.

APPROACH:
1. Generate data for charts (JSON format) - works with any charting library
2. ASCII text visualizations (pure Python, no library needed)
3. HTML reports (can be viewed in browser)
4. Optional Matplotlib charts (uncomment if matplotlib installed)

USAGE:
    from src.analytics.reports import EarningsAnalyzer
    
    analyzer = EarningsAnalyzer(db_session)
    report = analyzer.worker_earnings_summary(worker_id=1)
    html = report.to_html()
    
    visualization = analyzer.earnings_comparison_chart(worker_id=1)
    print(visualization.to_ascii())  # Text-based chart
    data = visualization.to_json()   # Data for frontend charting
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session

from src.models import Worker, Shift

logger = logging.getLogger(__name__)


class EarningsAnalyzer:
    """
    Earnings Analysis Engine
    
    Analyzes worker earnings data to provide insights on:
    - Actual vs predicted earnings comparison
    - Income guarantee top-ups paid
    - Earning trends over time
    - Performance metrics
    - Worker profitability
    """
    
    def __init__(self, db: Session):
        """Initialize analyzer with database session."""
        self.db = db
    
    def worker_earnings_summary(self, worker_id: int) -> Dict:
        """
        Generate comprehensive earnings summary for a worker.
        
        Returns:
            Dictionary with earnings statistics:
            - total_earnings: Sum of all actual earnings
            - total_predicted: Sum of all predicted earnings
            - total_topup: Total income guarantee payouts
            - num_shifts: Number of shifts worked
            - avg_hourly: Average hourly earnings
            - accuracy: Prediction accuracy percentage
            - guarantee_utilization: % of shifts that received top-up
        
        Example output:
            {
                'worker_id': 1,
                'worker_name': 'John Doe',
                'total_earnings': 1250.75,
                'total_predicted': 1400.00,
                'total_topup': 149.25,
                'num_shifts': 25,
                'avg_hourly': 50.03,
                'accuracy': 89.3,
                'guarantee_utilization': 32.0,  # % of shifts
                'status': 'High performer'
            }
        """
        # Query worker and their shifts
        worker = self.db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            return {'error': f'Worker {worker_id} not found'}
        
        shifts = self.db.query(Shift).filter(Shift.worker_id == worker_id).all()
        
        if not shifts:
            return {
                'worker_id': worker_id,
                'worker_name': worker.name,
                'total_earnings': 0.0,
                'total_predicted': 0.0,
                'total_topup': 0.0,
                'num_shifts': 0,
                'message': 'No shift data available'
            }
        
        # Calculate statistics
        total_earnings = sum(s.earnings or 0.0 for s in shifts)
        total_predicted = sum(s.predicted_earnings or 0.0 for s in shifts)
        
        # Calculate top-ups (income guarantee)
        topups = []
        for shift in shifts:
            expected = (shift.predicted_earnings or 0.0) * 0.9  # 90% guarantee
            actual = shift.earnings or 0.0
            topup = max(0.0, expected - actual)
            topups.append(topup)
        total_topup = sum(topups)
        
        # Calculate metrics
        num_shifts = len(shifts)
        avg_hourly = total_earnings / num_shifts if num_shifts > 0 else 0.0
        accuracy = (total_earnings / total_predicted * 100) if total_predicted > 0 else 0.0
        guarantee_utilization = (sum(1 for t in topups if t > 0) / num_shifts * 100) if num_shifts > 0 else 0.0
        
        # Determine performance status
        if accuracy >= 95:
            status = 'Excellent - Earnings exceed predictions'
        elif accuracy >= 85:
            status = 'Good - Predictions accurate'
        elif accuracy >= 75:
            status = 'Fair - Some variance in earnings'
        else:
            status = 'Needs attention - Large gap between predicted/actual'
        
        return {
            'worker_id': worker_id,
            'worker_name': worker.name,
            'total_earnings': round(total_earnings, 2),
            'total_predicted': round(total_predicted, 2),
            'total_topup': round(total_topup, 2),
            'num_shifts': num_shifts,
            'avg_hourly': round(avg_hourly, 2),
            'accuracy': round(accuracy, 1),
            'guarantee_utilization': round(guarantee_utilization, 1),
            'status': status
        }
    
    def earnings_comparison_data(self, worker_id: int, days: int = 30) -> Dict:
        """
        Get earnings vs predicted comparison data for visualization.
        
        Returns JSON-compatible data for charting:
        {
            'shifts': [
                {
                    'date': '2026-02-12',
                    'start_time': '08:00',
                    'actual': 85.50,
                    'predicted': 95.00,
                    'topup': 0.00,
                    'difference': -9.50
                },
                ...
            ],
            'summary': {
                'total_actual': 1250.75,
                'total_predicted': 1400.00,
                'avg_difference': -12.34
            }
        }
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        shifts = self.db.query(Shift).filter(
            Shift.worker_id == worker_id,
            Shift.created_at >= cutoff
        ).order_by(Shift.created_at).all()
        
        shift_data = []
        for shift in shifts:
            actual = shift.earnings or 0.0
            predicted = shift.predicted_earnings or 0.0
            expected = predicted * 0.9
            topup = max(0.0, expected - actual)
            difference = actual - predicted
            
            shift_data.append({
                'date': shift.start_time.strftime('%Y-%m-%d'),
                'start_time': shift.start_time.strftime('%H:%M'),
                'actual': round(actual, 2),
                'predicted': round(predicted, 2),
                'topup': round(topup, 2),
                'difference': round(difference, 2)
            })
        
        total_actual = sum(s['actual'] for s in shift_data)
        total_predicted = sum(s['predicted'] for s in shift_data)
        avg_diff = (total_actual - total_predicted) / len(shift_data) if shift_data else 0
        
        return {
            'worker_id': worker_id,
            'time_period': f'Last {days} days',
            'shifts': shift_data,
            'summary': {
                'total_actual': round(total_actual, 2),
                'total_predicted': round(total_predicted, 2),
                'avg_difference': round(avg_diff, 2),
                'num_shifts': len(shift_data)
            }
        }
    
    def earnings_ascii_chart(self, worker_id: int, days: int = 7) -> str:
        """
        Generate ASCII text-based earnings comparison chart.
        
        No external libraries needed - pure Python visualization.
        
        Example output:
        ┌─ Earnings vs Predicted (Last 7 days) ─┐
        │                                         │
        │  Date       Actual  Predicted  Chart    │
        │  ─────────────────────────────────────  │
        │  02-12      85.50   95.00     ████░░░  │
        │  02-11      92.00   88.00     █████░░  │
        │  02-10      78.50   90.00     ███░░░░  │
        │  02-09      110.00  105.00    ██████░  │
        │                                         │
        │  Total      366.00  378.00    -3.2%   │
        └─────────────────────────────────────────┘
        """
        data = self.earnings_comparison_data(worker_id, days)
        shifts = data['shifts']
        
        if not shifts:
            return f"No shift data for worker {worker_id}"
        
        # Find max value for scaling
        max_val = max(
            max(s['actual'], s['predicted']) for s in shifts
        )
        max_val = max(max_val, 100)  # Minimum scale
        chart_width = 15
        
        lines = [
            f"┌─ Earnings vs Predicted (Last {days} days) ─┐",
            "│                                           │",
            "│  Date      Actual   Pred    Chart        │",
            "│  ──────────────────────────────────────  │"
        ]
        
        for shift in shifts:
            date = shift['date'].split('-')[2]  # Day only
            actual = shift['actual']
            pred = shift['predicted']
            
            # Create bar chart
            actual_width = int((actual / max_val) * chart_width)
            filled = '█' * actual_width
            empty = '░' * (chart_width - actual_width)
            
            lines.append(
                f"│  {date}    ${actual:7.2f}  ${pred:7.2f}  {filled}{empty}  │"
            )
        
        summary = data['summary']
        avg_pct = (summary['avg_difference'] / summary['total_predicted'] * 100) if summary['total_predicted'] > 0 else 0
        
        lines.extend([
            "│  ──────────────────────────────────────  │",
            f"│  Total: ${summary['total_actual']:7.2f}  ${summary['total_predicted']:7.2f}  {avg_pct:+.1f}%  │",
            "└─────────────────────────────────────────┘"
        ])
        
        return '\n'.join(lines)
    
    def income_guarantee_report(self, worker_id: int) -> Dict:
        """
        Detailed income guarantee analysis.
        
        Shows:
        - Shifts that received top-up payments
        - Top-up amounts and reasons
        - Guarantee effectiveness
        - Prediction accuracy issues
        
        Returns:
            {
                'worker_id': 1,
                'total_shifts': 25,
                'shifts_with_topup': 8,
                'topup_percentage': 32.0,
                'total_topup_paid': 149.25,
                'avg_topup': 18.66,
                'topup_details': [
                    {
                        'date': '2026-02-12',
                        'actual': 80.00,
                        'predicted': 100.00,
                        'gap': -20.00,
                        'topup': 10.00,  # max(0, 100*0.9 - 80)
                        'reason': 'Low demand period'
                    },
                    ...
                ]
            }
        """
        shifts = self.db.query(Shift).filter(Shift.worker_id == worker_id).all()
        
        topup_details = []
        total_topup = 0.0
        
        for shift in shifts:
            actual = shift.earnings or 0.0
            predicted = shift.predicted_earnings or 0.0
            expected = predicted * 0.9
            topup = max(0.0, expected - actual)
            
            if topup > 0:
                gap = actual - predicted
                topup_details.append({
                    'date': shift.start_time.strftime('%Y-%m-%d'),
                    'time': shift.start_time.strftime('%H:%M'),
                    'actual': round(actual, 2),
                    'predicted': round(predicted, 2),
                    'gap': round(gap, 2),
                    'topup': round(topup, 2),
                    'reason': 'Earnings below 90% of prediction'
                })
                total_topup += topup
        
        num_shifts = len(shifts)
        topup_count = len(topup_details)
        topup_pct = (topup_count / num_shifts * 100) if num_shifts > 0 else 0
        avg_topup = (total_topup / topup_count) if topup_count > 0 else 0
        
        return {
            'worker_id': worker_id,
            'total_shifts': num_shifts,
            'shifts_with_topup': topup_count,
            'topup_percentage': round(topup_pct, 1),
            'total_topup_paid': round(total_topup, 2),
            'avg_topup_amount': round(avg_topup, 2),
            'status': 'Income guarantee working as intended' if topup_pct < 50 else 'High top-up utilization - check predictions',
            'topup_details': topup_details
        }


def format_report_html(analyzer: EarningsAnalyzer, worker_id: int) -> str:
    """
    Generate HTML report for earnings analysis (viewable in browser).
    
    Can be served via FastAPI endpoint or saved as file.
    """
    summary = analyzer.worker_earnings_summary(worker_id)
    comparison = analyzer.earnings_comparison_data(worker_id)
    guarantee = analyzer.income_guarantee_report(worker_id)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Worker Earnings Report - {summary.get('worker_name', 'Worker')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #666; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-top: 30px; }}
            .stat {{ display: inline-block; margin: 10px 20px 10px 0; }}
            .stat-label {{ color: #666; font-size: 0.9em; }}
            .stat-value {{ font-size: 1.5em; font-weight: bold; color: #007bff; }}
            .good {{ color: green; }}
            .warning {{ color: orange; }}
            .alert {{ color: red; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #007bff; color: white; }}
            tr:hover {{ background: #f9f9f9; }}
            .chart {{ background: #f9f9f9; padding: 15px; border-radius: 4px; margin: 15px 0; font-family: monospace; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Earnings Report</h1>
            <p><strong>Worker:</strong> {summary.get('worker_name')} (ID: {summary.get('worker_id')})</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>Summary Statistics</h2>
            <div class="stat">
                <div class="stat-label">Total Earnings</div>
                <div class="stat-value">${summary.get('total_earnings', 0):.2f}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Predicted</div>
                <div class="stat-value">${summary.get('total_predicted', 0):.2f}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Income Guarantee Paid</div>
                <div class="stat-value class="good">${summary.get('total_topup', 0):.2f}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Average Hourly</div>
                <div class="stat-value">${summary.get('avg_hourly', 0):.2f}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Prediction Accuracy</div>
                <div class="stat-value">{summary.get('accuracy', 0):.1f}%</div>
            </div>
            
            <h2>Status</h2>
            <p>{summary.get('status', 'N/A')}</p>
            
            <h2>Earnings vs Predicted Comparison</h2>
            <p>Shifts in last 30 days: {comparison['summary']['num_shifts']}</p>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Actual</th>
                    <th>Predicted</th>
                    <th>Top-up</th>
                    <th>Difference</th>
                </tr>
    """
    
    for shift in comparison['shifts'][-10:]:  # Last 10 shifts
        diff_class = 'good' if shift['difference'] >= 0 else 'alert'
        html += f"""
                <tr>
                    <td>{shift['date']} {shift['start_time']}</td>
                    <td>${shift['actual']:.2f}</td>
                    <td>${shift['predicted']:.2f}</td>
                    <td>${shift['topup']:.2f}</td>
                    <td class="{diff_class}">${shift['difference']:+.2f}</td>
                </tr>
        """
    
    html += """
            </table>
            
            <h2>Income Guarantee Analysis</h2>
    """
    
    html += f"""
            <p>Shifts receiving top-up: {guarantee['shifts_with_topup']} / {guarantee['total_shifts']} ({guarantee['topup_percentage']:.1f}%)</p>
            <p>Total top-up paid: ${guarantee['total_topup_paid']:.2f}</p>
            <p>Average top-up: ${guarantee['avg_topup_amount']:.2f}</p>
            <p><strong>Status:</strong> {guarantee['status']}</p>
            
            <h2>Tips for Higher Earnings</h2>
            <ul>
                <li>Check earnings comparison chart to identify peak hours</li>
                <li>Work during periods when actual earnings exceed predictions</li>
                <li>Track which locations have better earning potential</li>
                <li>Adjust schedule based on demand patterns</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return html
