from app.services.weather_evaluation_service import WeatherEvaluationService

service = WeatherEvaluationService()


async def test_list_notifications_empty(client, user):
    response = await client.get(f"/api/v1/notifications?user_id={user.id}")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_notifications_after_evaluation(client, session, alert, weather_event):
    await service.evaluate_pending_alerts(session)

    response = await client.get(f"/api/v1/notifications?alert_id={alert.id}")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "pending"


async def test_list_notifications_filter_by_status(client, session, user, alert, weather_event):
    await service.evaluate_pending_alerts(session)

    pending = await client.get(f"/api/v1/notifications?status=pending&user_id={user.id}")
    sent = await client.get(f"/api/v1/notifications?status=sent&user_id={user.id}")

    assert len(pending.json()) == 1
    assert sent.json() == []


async def test_list_notifications_filter_by_user(client, session, user, alert, weather_event):
    await service.evaluate_pending_alerts(session)

    response = await client.get(f"/api/v1/notifications?user_id={user.id}")

    assert response.status_code == 200
    assert len(response.json()) == 1
