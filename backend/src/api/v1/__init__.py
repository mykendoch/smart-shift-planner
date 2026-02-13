from fastapi import APIRouter

from .endpoints.workers import router as workers_router
from .endpoints.shifts import router as shifts_router
from .endpoints.predictions import router as predictions_router
from .endpoints.analytics import router as analytics_router
from .endpoints.auth import router as auth_router
from .endpoints.volatility import router as volatility_router
from .endpoints.accuracy import router as accuracy_router
from .endpoints.surveys import router as surveys_router
from .endpoints.eligibility import router as eligibility_router
from .endpoints.guarantee import router as guarantee_router
from .endpoints.admin import router as admin_router

router = APIRouter()
router.include_router(workers_router)
router.include_router(shifts_router)
router.include_router(predictions_router)
router.include_router(analytics_router)
router.include_router(auth_router)
router.include_router(volatility_router)
router.include_router(accuracy_router)
router.include_router(surveys_router)
router.include_router(eligibility_router)
router.include_router(guarantee_router)
router.include_router(admin_router)

