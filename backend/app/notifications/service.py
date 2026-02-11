from typing import List

from app.notifications.interface import NotificationRepositoryInterface
from app.notifications.model import Notification
from app.notifications.schema import NotificationResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)


class NotificationService:
    def __init__(self, repository: NotificationRepositoryInterface):
        self.repository = repository

    async def get_user_notifications(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[NotificationResponse]:
        notifications = await self.repository.get_user_notifications(
            user_id, skip, limit
        )
        return [self._to_response(n) for n in notifications]

    async def mark_as_read(
        self, notification_id: int, user_id: int
    ) -> NotificationResponse:
        notification = await self.repository.mark_as_read(notification_id, user_id)
        if not notification:
            from app.utils.exceptions import NotFoundException

            raise NotFoundException("Notification not found")
        return self._to_response(notification)

    async def mark_all_as_read(self, user_id: int) -> None:
        await self.repository.mark_all_as_read(user_id)

    async def get_unread_count(self, user_id: int) -> int:
        return await self.repository.get_unread_count(user_id)

    def _to_response(self, notification: Notification) -> NotificationResponse:
        return NotificationResponse(
            id=notification.id,
            receiver_id=notification.receiver_id,
            actor_id=notification.actor_id,
            actor_username=notification.actor.username
            if notification.actor
            else "Unknown",
            type=notification.type,
            post_id=notification.post_id,
            comment_id=notification.comment_id,
            is_read=notification.is_read,
            created_at=notification.created_at,
        )
