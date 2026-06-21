from fastapi import APIRouter

from app.api.v1 import alerts, health, notifications, weather_events

router = APIRouter(prefix="/api/v1")

router.include_router(weather_events.router)
router.include_router(alerts.router)
router.include_router(notifications.router)
router.include_router(health.router)
