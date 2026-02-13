"""
Advanced Logging Configuration

Separates logs into:
- app.log: General application logs (info, debug)
- error.log: Error and warning logs only
- database.log: SQL and database operations
- All in logs/ folder with rotation support
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

# Ensure logs directory exists
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Create loggers for different components
def setup_logging():
    """Configure logging with separated log files and levels."""
    
    # Remove any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Log format with timestamp, level, logger name, and message
    detailed_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ========================================================================
    # APPLICATION LOG - General application info/debug (level: DEBUG and up)
    # ========================================================================
    app_logger = logging.getLogger()  # Root logger
    app_logger.setLevel(logging.DEBUG)
    
    # File handler with rotation (max 5MB, keep 5 backups)
    app_handler = logging.handlers.RotatingFileHandler(
        filename=LOGS_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    app_handler.setLevel(logging.DEBUG)  # Include DEBUG and above
    app_handler.setFormatter(detailed_format)
    app_logger.addHandler(app_handler)
    
    # Console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_format)
    app_logger.addHandler(console_handler)
    
    # ========================================================================
    # ERROR LOG - Errors and warnings only (level: WARNING and up)
    # ========================================================================
    error_handler = logging.handlers.RotatingFileHandler(
        filename=LOGS_DIR / "error.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    error_handler.setLevel(logging.WARNING)  # Only WARNING, ERROR, CRITICAL
    error_handler.setFormatter(detailed_format)
    app_logger.addHandler(error_handler)
    
    # ========================================================================
    # DATABASE LOG - SQL operations and database events
    # ========================================================================
    db_logger = logging.getLogger("sqlalchemy.engine")
    db_logger.setLevel(logging.INFO)
    
    db_handler = logging.handlers.RotatingFileHandler(
        filename=LOGS_DIR / "database.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(detailed_format)
    db_logger.addHandler(db_handler)
    
    # Prevent duplicate logs
    db_logger.propagate = False
    
    # ========================================================================
    # ANALYTICS LOG - Analytics and reporting operations
    # ========================================================================
    analytics_logger = logging.getLogger("analytics")
    analytics_logger.setLevel(logging.DEBUG)
    
    analytics_handler = logging.handlers.RotatingFileHandler(
        filename=LOGS_DIR / "analytics.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    analytics_handler.setLevel(logging.DEBUG)
    analytics_handler.setFormatter(detailed_format)
    analytics_logger.addHandler(analytics_handler)
    analytics_logger.propagate = False
    
    # ========================================================================
    # ML LOG - Machine learning predictions and forecasts
    # ========================================================================
    ml_logger = logging.getLogger("ml")
    ml_logger.setLevel(logging.DEBUG)
    
    ml_handler = logging.handlers.RotatingFileHandler(
        filename=LOGS_DIR / "ml.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    ml_handler.setLevel(logging.DEBUG)
    ml_handler.setFormatter(detailed_format)
    ml_logger.addHandler(ml_handler)
    ml_logger.propagate = False
    
    return {
        'app': app_logger,
        'error': error_handler,
        'database': db_logger,
        'analytics': analytics_logger,
        'ml': ml_logger
    }


def get_logger(name: str) -> logging.Logger:
    """Get a logger by name."""
    return logging.getLogger(name)


if __name__ == "__main__":
    """Test the logging configuration."""
    setup_logging()
    
    # Test app logger
    logger = get_logger("test")
    logger.debug("This is a DEBUG message - goes to app.log and console")
    logger.info("This is an INFO message - goes to app.log and console")
    logger.warning("This is a WARNING message - goes to app.log, error.log, and console")
    logger.error("This is an ERROR message - goes to app.log, error.log, and console")
    
    # Test database logger
    db_logger = get_logger("sqlalchemy.engine")
    db_logger.info("Database query executed")
    
    # Test analytics logger
    analytics = get_logger("analytics")
    analytics.debug("Earnings analysis started")
    
    # Test ML logger
    ml = get_logger("ml")
    ml.debug("Prediction model initialized")
    
    print("\n✓ Logging configuration test complete")
    print(f"✓ Logs directory: {LOGS_DIR.absolute()}")
    print("\nLog files created:")
    for log_file in sorted(LOGS_DIR.glob("*.log")):
        print(f"  - {log_file.name}")
