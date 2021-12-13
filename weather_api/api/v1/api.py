from fastapi import APIRouter
from .endpoints import router as weather_router

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(weather_router)
