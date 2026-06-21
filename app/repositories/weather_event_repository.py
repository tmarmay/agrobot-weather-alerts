from datetime import date, timedelta

from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import WeatherEventType
from app.models.alert import Alert
from app.models.notification import Notification
from app.models.weather_event import WeatherEvent


class WeatherEventRepository:

    async def create(self, session: AsyncSession, **kwargs) -> WeatherEvent:
        event = WeatherEvent(**kwargs)
        session.add(event)
        await session.flush()
        return event

    async def get_by_id(self, session: AsyncSession, id: int) -> WeatherEvent | None:
        result = await session.execute(
            select(WeatherEvent).where(WeatherEvent.id == id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        session: AsyncSession,
        field_id: int | None = None,
        event_type: WeatherEventType | None = None,
    ) -> list[WeatherEvent]:
        stmt = select(WeatherEvent)
        if field_id is not None:
            stmt = stmt.where(WeatherEvent.field_id == field_id)
        if event_type is not None:
            stmt = stmt.where(WeatherEvent.event_type == event_type)
        stmt = stmt.order_by(WeatherEvent.forecast_date.desc())
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_unevaluated_matches(
        self, session: AsyncSession
    ) -> list[tuple[WeatherEvent, Alert]]:
        cutoff = date.today() - timedelta(days=3)
        stmt = (
            select(WeatherEvent, Alert)
            .join(
                Alert,
                and_(
                    Alert.field_id == WeatherEvent.field_id,
                    Alert.event_type == WeatherEvent.event_type,
                ),
            )
            .where(
                Alert.is_active == True,
                WeatherEvent.probability >= Alert.threshold,
                WeatherEvent.forecast_date >= cutoff,
                ~exists().where(
                    and_(
                        Notification.alert_id == Alert.id,
                        Notification.weather_event_id == WeatherEvent.id,
                    )
                ),
            )
        )
        result = await session.execute(stmt)
        return result.all()
