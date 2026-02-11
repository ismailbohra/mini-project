from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.notifications.repository import NotificationRepository
from app.notifications.service import NotificationService


async def get_notification_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NotificationService:
    repository = NotificationRepository(session)
    return NotificationService(repository)
