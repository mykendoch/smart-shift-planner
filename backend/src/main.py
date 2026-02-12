"""
Smart Shift Planner - Gig Economy Optimizer
Main Application Entry Point

Student: Michael Myken (@mykendoch)
Project: AI-driven scheduling and income guarantee for gig workers
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
from pathlib import Path

from src.core.config import settings
from src.api.v1 import router as api_router

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    Smart Shift Planner + Income Guarantee Window
    
    AI-driven scheduling and income guarantee system for gig economy workers.
    
    **Features:**
    - 🎯 Earnings prediction based on time, location, demand
    - 💰 Income guarantee mechanism (90% threshold)
    - 📊 Shift optimization recommendations
    - 📈 Performance analytics
    
    **Research Questions:**
    1. How effective is AI scheduling in increasing earnings?
    2. Does income guarantee reduce financial stress?
    3. How does optimization influence worker productivity?
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)
@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("="*70)
    logger.info("SMART SHIFT PLANNER - GIG ECONOMY OPTIMIZER")
    logger.info(f"Student: Michael Myken (@mykendoch)")
    logger.info(f"Started: {datetime.now()}")
    logger.info(f"Target: Gig Economy Workers (Uber, Delivery, etc.)")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'PostgreSQL'}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("="*70)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Smart Shift Planner shutting down...")


@app.get("/")
def root():
    """
    Root endpoint - Project information
    
    Returns overview of the system and available features
    """
    logger.info("Root endpoint accessed")
    
    return {
        "project": "Smart Shift Planner + Income Guarantee Window",
        "description": "AI-driven earnings optimization for gig economy workers",
        "student": "Michael Myken (@mykendoch)",
        "github": "https://github.com/mykendoch/smart-shift-planner",
        "target_users": [
            "Rideshare drivers (Uber, Lyft)",
            "Delivery drivers (UberEats, DoorDash)",
            "Freelance workers"
        ],
        "features": {
            "earnings_prediction": "Predict hourly earnings based on time/location/demand",
            "income_guarantee": "90% earnings guarantee with automatic top-up",
            "shift_optimization": "AI recommends best times/locations to work",
            "performance_tracking": "Track earnings, hours, efficiency metrics"
        },
        "research_questions": [
            "How effective is AI-based shift scheduling in increasing earnings?",
            "Does income guarantee reduce financial stress for workers?",
            "How does optimization influence worker productivity and decisions?"
        ],
        "status": "running",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "documentation": "/docs"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint
    
    Returns system status and basic diagnostics
    """
    logger.debug("Health check requested")
    
    return {
        "status": "healthy",
        "service": "Smart Shift Planner API",
        "version": settings.VERSION,
        "database": "PostgreSQL (gigeconomy)",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/info")
def api_info():
    """
    API information and capabilities
    
    Returns available endpoints and ML models
    """
    return {
        "api_version": "v1",
        "endpoints": {
            "health": "/health",
            "predict_earnings": "/api/v1/predict-earnings",
            "income_guarantee": "/api/v1/income-guarantee",
            "workers": "/api/v1/workers",
            "shifts": "/api/v1/shifts"
        },
        "ml_models": {
            "earnings_predictor": "Random Forest Regressor (Planned)",
            "demand_forecaster": "Time Series Analysis (Planned)",
            "location_optimizer": "K-Means Clustering (Planned)"
        },
        "business_rules": {
            "guarantee_threshold": f"{int(settings.GUARANTEE_THRESHOLD * 100)}%",
            "minimum_hours": settings.MINIMUM_HOURS_FOR_GUARANTEE
        }
    }


# Run with: uvicorn src.main:app --reload