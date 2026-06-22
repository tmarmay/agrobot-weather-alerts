from datetime import date

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.core.database import get_db
from app.core.enums import WeatherEventType
from app.main import app
from app.models.alert import Alert
from app.models.field import Field
from app.models.user import User
from app.models.weather_event import WeatherEvent


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(settings.database_url)
    async with AsyncSession(engine, expire_on_commit=False) as _session:
        await _session.begin()
        yield _session
        await _session.rollback()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session):
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session):
    u = User(name="Test User", phone_number="+5491100000001")
    session.add(u)
    await session.flush()
    return u


@pytest_asyncio.fixture
async def field(session, user):
    f = Field(user_id=user.id, name="Test Field")
    session.add(f)
    await session.flush()
    return f


@pytest_asyncio.fixture
async def alert(session, user, field):
    a = Alert(
        user_id=user.id,
        field_id=field.id,
        event_type=WeatherEventType.RAIN,
        threshold=50.0,
    )
    session.add(a)
    await session.flush()
    return a


@pytest_asyncio.fixture
async def weather_event(session, field):
    we = WeatherEvent(
        field_id=field.id,
        event_type=WeatherEventType.RAIN,
        probability=75.0,
        forecast_date=date.today(),
    )
    session.add(we)
    await session.flush()
    return we
