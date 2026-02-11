from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    receiver_id: int
    actor_id: int
    actor_username: str
    type: str
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
