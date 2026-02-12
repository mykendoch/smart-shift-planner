"""
Analytics API Endpoints

Routes for earnings analysis and visualization data:
- /api/v1/analytics/worker/{worker_id}/summary - Worker earnings summary
- /api/v1/analytics/worker/{worker_id}/comparison - Earnings vs predicted data
- /api/v1/analytics/worker/{worker_id}/guarantee - Income guarantee analysis
- /api/v1/analytics/worker/{worker_id}/report - HTML earnings report
- /api/v1/analytics/worker/{worker_id}/chart - ASCII text visualization

Fulfills project requirement: "Data visualization tools (e.g. charts for earnings comparison)"
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.analytics.reports import EarningsAnalyzer, format_report_html

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/worker/{worker_id}/summary")
def get_worker_summary(worker_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive earnings summary for a worker.
    
    Returns:
    - total_earnings: Sum of all actual earnings
    - total_predicted: Sum of all predicted earnings
    - total_topup: Total income guarantee payouts
    - num_shifts: Number of shifts worked
    - avg_hourly: Average hourly earnings
    - accuracy: Prediction accuracy percentage
    - guarantee_utilization: % of shifts that received top-up
    - status: Performance assessment
    """
    analyzer = EarningsAnalyzer(db)
    result = analyzer.worker_earnings_summary(worker_id)
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return result


@router.get("/worker/{worker_id}/comparison")
def get_earnings_comparison(worker_id: int, days: int = 30, db: Session = Depends(get_db)):
    """
    Get earnings vs predicted comparison data for charting.
    
    Query Parameters:
    - days: Number of days to include (default 30)
    
    Returns JSON data with:
    - shifts: Array of shift earnings data with actual, predicted, top-up
    - summary: Totals and averages
    
    Use this data to plot:
    - Line chart: actual vs predicted over time
    - Bar chart: earnings distribution
    - Scatter: actual vs predicted correlation
    """
    analyzer = EarningsAnalyzer(db)
    return analyzer.earnings_comparison_data(worker_id, days)


@router.get("/worker/{worker_id}/guarantee")
def get_guarantee_report(worker_id: int, db: Session = Depends(get_db)):
    """
    Income guarantee impact analysis.
    
    Shows:
    - How many shifts received top-up payments
    - Total amount paid in top-ups
    - Detailed list of top-ups and reasons
    - Prediction accuracy assessment
    
    Helps identify if predictions need improvement.
    """
    analyzer = EarningsAnalyzer(db)
    return analyzer.income_guarantee_report(worker_id)


@router.get("/worker/{worker_id}/report")
def get_earnings_report(worker_id: int, db: Session = Depends(get_db)):
    """
    Generate complete HTML earnings report.
    
    Returns HTML page with:
    - Summary statistics
    - Earnings vs predicted comparison table
    - Income guarantee analysis
    - Tips for increasing earnings
    
    Can be viewed in browser or emailed to worker.
    """
    analyzer = EarningsAnalyzer(db)
    html = format_report_html(analyzer, worker_id)
    
    return {
        'worker_id': worker_id,
        'report_html': html,
        'note': 'Save as .html file or render in browser to view formatted report'
    }


@router.get("/worker/{worker_id}/chart")
def get_earnings_chart(worker_id: int, days: int = 7, db: Session = Depends(get_db)):
    """
    Get ASCII text-based earnings comparison chart.
    
    Query Parameters:
    - days: Number of days to include (default 7)
    
    Returns:
    - chart: ASCII bar chart showing actual vs predicted earnings
    - data: JSON data used to generate chart
    
    No graphics library needed - works in terminal or console.
    Shows quick visual comparison without needing frontend chart library.
    
    Example:
    ┌─ Earnings vs Predicted (Last 7 days) ─┐
    │                                         │
    │  Date      Actual   Pred    Chart      │
    │  02-12     85.50    95.00   ████░░░░  │
    │  02-11     92.00    88.00   ████░░░░  │
    │  02-10     78.50    90.00   ███░░░░░  │
    │  ...                                    │
    │  Total:    ...                         │
    └─────────────────────────────────────────┘
    """
    analyzer = EarningsAnalyzer(db)
    chart_text = analyzer.earnings_ascii_chart(worker_id, days)
    comparison_data = analyzer.earnings_comparison_data(worker_id, days)
    
    return {
        'worker_id': worker_id,
        'chart': chart_text,
        'data': comparison_data,
        'note': 'Chart can be printed or displayed in terminal'
    }


@router.get("/all-workers/summary")
def get_all_workers_summary(db: Session = Depends(get_db)):
    """
    Summary statistics for all workers.
    
    Returns:
    - List of all workers with their key metrics
    - Comparison of earnings across workers
    - Performance rankings
    - System-wide statistics
    
    Useful for manager dashboard and performance analytics.
    """
    from src.models import Worker
    
    workers = db.query(Worker).all()
    analyzer = EarningsAnalyzer(db)
    
    summaries = []
    for worker in workers:
        summary = analyzer.worker_earnings_summary(worker.id)
        if 'error' not in summary:
            summaries.append(summary)
    
    if not summaries:
        return {'workers': [], 'message': 'No workers found'}
    
    # Calculate system-wide statistics
    total_earnings = sum(s.get('total_earnings', 0) for s in summaries)
    avg_hourly = sum(s.get('avg_hourly', 0) for s in summaries) / len(summaries)
    avg_accuracy = sum(s.get('accuracy', 0) for s in summaries) / len(summaries)
    
    return {
        'workers': summaries,
        'system_statistics': {
            'num_workers': len(summaries),
            'total_earnings': round(total_earnings, 2),
            'avg_hourly_per_worker': round(avg_hourly, 2),
            'avg_prediction_accuracy': round(avg_accuracy, 1)
        }
    }
