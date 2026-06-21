from datetime import datetime

from pydantic import BaseModel

from app.core.enums import NotificationStatus


class NotificationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    alert_id: int
    weather_event_id: int
    status: NotificationStatus
    retry_count: int
    last_attempted_at: datetime | None
    sent_at: datetime | None
    error_message: str | None
    created_at: datetime
