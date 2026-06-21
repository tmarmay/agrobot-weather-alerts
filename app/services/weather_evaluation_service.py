from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.repositories.weather_event_repository import WeatherEventRepository


class WeatherEvaluationService:

    def __init__(self) -> None:
        self.weather_event_repo = WeatherEventRepository()
        self.notification_repo = NotificationRepository()

    async def evaluate_pending_alerts(self, session: AsyncSession) -> list[Notification]:
        matches = await self.weather_event_repo.get_unevaluated_matches(session)
        notifications = []
        for weather_event, alert in matches:
            notification = await self.notification_repo.create(
                session,
                alert_id=alert.id,
                weather_event_id=weather_event.id,
            )
            notifications.append(notification)
        return notifications
