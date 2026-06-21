from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import NotificationStatus
from app.models.alert import Alert
from app.models.notification import Notification


class NotificationRepository:

    async def create(self, session: AsyncSession, **kwargs) -> Notification:
        notification = Notification(**kwargs)
        session.add(notification)
        await session.flush()
        return notification

    async def get_by_id(self, session: AsyncSession, id: int) -> Notification | None:
        result = await session.execute(
            select(Notification).where(Notification.id == id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        session: AsyncSession,
        alert_id: int | None = None,
        status: NotificationStatus | None = None,
        user_id: int | None = None,
    ) -> list[Notification]:
        stmt = select(Notification)
        if user_id is not None:
            stmt = stmt.join(Alert, Notification.alert_id == Alert.id).where(
                Alert.user_id == user_id
            )
        if alert_id is not None:
            stmt = stmt.where(Notification.alert_id == alert_id)
        if status is not None:
            stmt = stmt.where(Notification.status == status)
        result = await session.execute(stmt)
        return result.scalars().all()
