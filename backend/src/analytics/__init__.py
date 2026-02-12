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

USAGE - IN CODE:
    from src.analytics.reports import EarningsAnalyzer
    
    analyzer = EarningsAnalyzer(db_session)
    report = analyzer.worker_earnings_summary(worker_id=1)
    status = report['status']
    
    visualization = analyzer.earnings_ascii_chart(worker_id=1)
    print(visualization)  # Text-based chart
    
    data = analyzer.earnings_comparison_data(worker_id=1)
    # Use data with any frontend charting library

USAGE - HTTP ENDPOINTS:
    GET /api/v1/analytics/worker/{worker_id}/summary
        → Earnings statistics and performance status
    
    GET /api/v1/analytics/worker/{worker_id}/comparison?days=30
        → Earnings vs predicted for charting
    
    GET /api/v1/analytics/worker/{worker_id}/guarantee
        → Income guarantee analysis
    
    GET /api/v1/analytics/worker/{worker_id}/report
        → HTML earnings report
    
    GET /api/v1/analytics/worker/{worker_id}/chart?days=7
        → ASCII text visualization
    
    GET /api/v1/analytics/all-workers/summary
        → System-wide statistics
"""

from src.analytics.reports import EarningsAnalyzer, format_report_html

__all__ = ['EarningsAnalyzer', 'format_report_html']
