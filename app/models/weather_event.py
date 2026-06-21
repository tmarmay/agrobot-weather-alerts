from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum as SAEnum, Float, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import WeatherEventType


class WeatherEvent(Base):
    __tablename__ = "weather_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(
        ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[WeatherEventType] = mapped_column(
        SAEnum(WeatherEventType), nullable=False
    )
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    field: Mapped["Field"] = relationship("Field", back_populates="weather_events")
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="weather_event"
    )

    __table_args__ = (
        UniqueConstraint("field_id", "event_type", "forecast_date"),
        Index("ix_weather_events_field_event_date", "field_id", "event_type", "forecast_date"),
    )
