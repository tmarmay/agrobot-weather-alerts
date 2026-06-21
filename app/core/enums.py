import enum


class WeatherEventType(str, enum.Enum):
    RAIN = "rain"
    FROST = "frost"
    HAIL = "hail"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
