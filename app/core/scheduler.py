from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.jobs.alert_evaluator import run_alert_evaluator

scheduler = AsyncIOScheduler()


def setup_scheduler() -> AsyncIOScheduler:
    scheduler.add_job(
        run_alert_evaluator,
        trigger="interval",
        seconds=settings.SCHEDULER_INTERVAL_SECONDS,
        id="evaluate_alerts_job",
        replace_existing=True,
    )
    return scheduler
