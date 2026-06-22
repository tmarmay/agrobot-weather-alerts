from datetime import date


async def test_create_alert(client, user, field):
    response = await client.post("/api/v1/alerts", json={
        "user_id": user.id,
        "field_id": field.id,
        "event_type": "rain",
        "threshold": 60.0,
    })

    assert response.status_code == 201
    data = response.json()
    assert data["event_type"] == "rain"
    assert data["threshold"] == 60.0
    assert data["is_active"] is True


async def test_create_duplicate_alert(client, user, field, alert):
    response = await client.post("/api/v1/alerts", json={
        "user_id": user.id,
        "field_id": field.id,
        "event_type": "rain",
        "threshold": 70.0,
    })

    assert response.status_code == 409


async def test_get_alert_by_id(client, alert):
    response = await client.get(f"/api/v1/alerts/{alert.id}")

    assert response.status_code == 200
    assert response.json()["id"] == alert.id


async def test_get_alert_not_found(client):
    response = await client.get("/api/v1/alerts/99999")

    assert response.status_code == 404


async def test_delete_alert(client, alert):
    response = await client.delete(f"/api/v1/alerts/{alert.id}")

    assert response.status_code == 204


async def test_delete_alert_not_found(client):
    response = await client.delete("/api/v1/alerts/99999")

    assert response.status_code == 404
