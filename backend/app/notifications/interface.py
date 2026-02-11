from abc import ABC, abstractmethod
from typing import List, Optional

from app.notifications.model import Notification


class NotificationRepositoryInterface(ABC):
    @abstractmethod
    async def create_notification(
        self,
        receiver_id: int,
        actor_id: int,
        type: str,
        post_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> Notification:
        pass

    @abstractmethod
    async def get_user_notifications(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[Notification]:
        pass

    @abstractmethod
    async def mark_as_read(
        self, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        pass

    @abstractmethod
    async def mark_all_as_read(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def get_unread_count(self, user_id: int) -> int:
        pass
