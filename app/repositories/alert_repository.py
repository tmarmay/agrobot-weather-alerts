from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert


class AlertRepository:

    async def create(self, session: AsyncSession, **kwargs) -> Alert:
        alert = Alert(**kwargs)
        session.add(alert)
        await session.flush()
        return alert

    async def delete(self, session: AsyncSession, alert: Alert) -> None:
        await session.delete(alert)
        await session.flush()

    async def get_by_id(self, session: AsyncSession, id: int) -> Alert | None:
        result = await session.execute(
            select(Alert).where(Alert.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, session: AsyncSession, user_id: int) -> list[Alert]:
        result = await session.execute(
            select(Alert).where(Alert.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_field(self, session: AsyncSession, field_id: int) -> list[Alert]:
        result = await session.execute(
            select(Alert).where(Alert.field_id == field_id)
        )
        return result.scalars().all()

    async def list_all(self, session: AsyncSession) -> list[Alert]:
        result = await session.execute(select(Alert))
        return result.scalars().all()
