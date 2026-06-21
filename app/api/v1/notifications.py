from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.enums import NotificationStatus
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])

_repo = NotificationRepository()


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    alert_id: int | None = None,
    status: NotificationStatus | None = None,
    user_id: int | None = None,
    session: AsyncSession = Depends(get_db),
):
    return await _repo.list_all(
        session, alert_id=alert_id, status=status, user_id=user_id
    )
