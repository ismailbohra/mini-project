from typing import List, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.notifications.interface import NotificationRepositoryInterface
from app.notifications.model import Notification


class NotificationRepository(NotificationRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification(
        self,
        receiver_id: int,
        actor_id: int,
        type: str,
        post_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> Notification:
        notification = Notification(
            receiver_id=receiver_id,
            actor_id=actor_id,
            type=type,
            post_id=post_id,
            comment_id=comment_id,
        )
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)

        query = (
            select(Notification)
            .where(Notification.id == notification.id)
            .options(selectinload(Notification.actor))
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_user_notifications(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[Notification]:
        query = (
            select(Notification)
            .where(Notification.receiver_id == user_id)
            .options(selectinload(Notification.actor))
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def mark_as_read(
        self, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        # Perform the update, then query the notification with relationship
        # loaded inside the same session to avoid lazy-loading outside a
        # running async session (which causes MissingGreenlet).
        query = (
            update(Notification)
            .where(
                Notification.id == notification_id, Notification.receiver_id == user_id
            )
            .values(is_read=True)
        )
        await self.session.execute(query)
        await self.session.commit()

        # Select the notification with actor relationship eagerly loaded
        sel = (
            select(Notification)
            .where(
                Notification.id == notification_id, Notification.receiver_id == user_id
            )
            .options(selectinload(Notification.actor))
        )
        result = await self.session.execute(sel)
        return result.scalar_one_or_none()

    async def mark_all_as_read(self, user_id: int) -> None:
        query = (
            update(Notification)
            .where(Notification.receiver_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        await self.session.execute(query)
        await self.session.commit()

    async def get_unread_count(self, user_id: int) -> int:
        query = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.receiver_id == user_id, Notification.is_read.is_(False))
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
