from datetime import date


async def test_create_weather_event(client, field):
    response = await client.post("/api/v1/weather-events", json={
        "field_id": field.id,
        "event_type": "rain",
        "probability": 75.0,
        "forecast_date": str(date.today()),
    })

    assert response.status_code == 201
    data = response.json()
    assert data["probability"] == 75.0
    assert data["field_id"] == field.id


async def test_create_duplicate_weather_event(client, field, weather_event):
    response = await client.post("/api/v1/weather-events", json={
        "field_id": field.id,
        "event_type": "rain",
        "probability": 80.0,
        "forecast_date": str(date.today()),
    })

    assert response.status_code == 409


async def test_list_weather_events(client, field, weather_event):
    response = await client.get(f"/api/v1/weather-events?field_id={field.id}")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == weather_event.id
