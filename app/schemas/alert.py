from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enums import WeatherEventType


class AlertCreate(BaseModel):
    user_id: int
    field_id: int
    event_type: WeatherEventType
    threshold: float = Field(ge=0.0, le=100.0)


class AlertResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    field_id: int
    event_type: WeatherEventType
    threshold: float
    is_active: bool
    created_at: datetime
