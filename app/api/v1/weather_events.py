from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.enums import WeatherEventType
from app.repositories.weather_event_repository import WeatherEventRepository
from app.schemas.weather_event import WeatherEventCreate, WeatherEventResponse

router = APIRouter(prefix="/weather-events", tags=["weather-events"])

_repo = WeatherEventRepository()


@router.post("/", response_model=WeatherEventResponse, status_code=201)
async def create_weather_event(
    body: WeatherEventCreate,
    session: AsyncSession = Depends(get_db),
):
    return await _repo.create(session, **body.model_dump())


@router.get("/", response_model=list[WeatherEventResponse])
async def list_weather_events(
    field_id: int | None = None,
    event_type: WeatherEventType | None = None,
    session: AsyncSession = Depends(get_db),
):
    return await _repo.list_all(session, field_id=field_id, event_type=event_type)
