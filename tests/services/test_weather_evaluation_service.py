from datetime import date, timedelta

from app.core.enums import WeatherEventType
from app.models.alert import Alert
from app.models.weather_event import WeatherEvent
from app.services.weather_evaluation_service import WeatherEvaluationService

service = WeatherEvaluationService()


async def test_creates_notification_when_threshold_met(session, alert, weather_event):
    notifications = await service.evaluate_pending_alerts(session)

    assert len(notifications) == 1
    assert notifications[0].alert_id == alert.id
    assert notifications[0].weather_event_id == weather_event.id


async def test_skips_when_below_threshold(session, user, field):
    a = Alert(user_id=user.id, field_id=field.id, event_type=WeatherEventType.FROST, threshold=80.0)
    we = WeatherEvent(field_id=field.id, event_type=WeatherEventType.FROST, probability=50.0, forecast_date=date.today())
    session.add_all([a, we])
    await session.flush()

    notifications = await service.evaluate_pending_alerts(session)

    assert len(notifications) == 0


async def test_is_idempotent(session, alert, weather_event):
    first = await service.evaluate_pending_alerts(session)
    second = await service.evaluate_pending_alerts(session)

    assert len(first) == 1
    assert len(second) == 0


async def test_skips_inactive_alert(session, user, field):
    a = Alert(user_id=user.id, field_id=field.id, event_type=WeatherEventType.HAIL, threshold=40.0, is_active=False)
    we = WeatherEvent(field_id=field.id, event_type=WeatherEventType.HAIL, probability=90.0, forecast_date=date.today())
    session.add_all([a, we])
    await session.flush()

    notifications = await service.evaluate_pending_alerts(session)

    assert len(notifications) == 0


async def test_skips_event_older_than_3_days(session, user, field):
    a = Alert(user_id=user.id, field_id=field.id, event_type=WeatherEventType.RAIN, threshold=50.0)
    we = WeatherEvent(
        field_id=field.id,
        event_type=WeatherEventType.RAIN,
        probability=90.0,
        forecast_date=date.today() - timedelta(days=4),
    )
    session.add_all([a, we])
    await session.flush()

    notifications = await service.evaluate_pending_alerts(session)

    assert len(notifications) == 0
