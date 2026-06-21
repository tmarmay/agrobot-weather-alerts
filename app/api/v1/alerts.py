from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertCreate, AlertResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])

_repo = AlertRepository()


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(
    body: AlertCreate,
    session: AsyncSession = Depends(get_db),
):
    async with session.begin():
        return await _repo.create(session, **body.model_dump())


@router.get("/", response_model=list[AlertResponse])
async def list_alerts(
    user_id: int | None = None,
    field_id: int | None = None,
    session: AsyncSession = Depends(get_db),
):
    if field_id is not None:
        return await _repo.get_by_field(session, field_id=field_id)
    if user_id is not None:
        return await _repo.get_by_user(session, user_id=user_id)
    return await _repo.list_all(session)


@router.get("/{id}", response_model=AlertResponse)
async def get_alert(id: int, session: AsyncSession = Depends(get_db)):
    alert = await _repo.get_by_id(session, id=id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.delete("/{id}", status_code=204)
async def delete_alert(id: int, session: AsyncSession = Depends(get_db)):
    async with session.begin():
        alert = await _repo.get_by_id(session, id=id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        await _repo.delete(session, alert)
