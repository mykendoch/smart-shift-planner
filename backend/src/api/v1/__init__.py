from fastapi import APIRouter

from .endpoints.workers import router as workers_router
from .endpoints.shifts import router as shifts_router
from .endpoints.predictions import router as predictions_router

router = APIRouter()
router.include_router(workers_router)
router.include_router(shifts_router)
router.include_router(predictions_router)

