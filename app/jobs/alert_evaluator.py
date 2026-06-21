import logging

from app.core.database import AsyncSessionLocal
from app.services.weather_evaluation_service import WeatherEvaluationService

logger = logging.getLogger(__name__)

_service = WeatherEvaluationService()


async def run_alert_evaluator() -> None:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                notifications = await _service.evaluate_pending_alerts(session)
        logger.info("alert_evaluator: %d notification(s) created", len(notifications))
    except Exception:
        logger.exception("alert_evaluator: unexpected error during evaluation")
