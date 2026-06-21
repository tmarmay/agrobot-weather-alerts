from datetime import date, datetime

from pydantic import BaseModel, Field

from app.core.enums import WeatherEventType


class WeatherEventCreate(BaseModel):
    field_id: int
    event_type: WeatherEventType
    probability: float = Field(ge=0.0, le=100.0)
    forecast_date: date


class WeatherEventResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    field_id: int
    event_type: WeatherEventType
    probability: float
    forecast_date: date
    created_at: datetime
