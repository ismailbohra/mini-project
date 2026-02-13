from typing import List

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)

import app.utils.redis as redis_utils
from app.auth.dependency import get_current_user_id
from app.notifications.dependency import get_notification_service
from app.notifications.schema import NotificationResponse
from app.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get(
    "/",
    response_model=List[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service),
):
    return await service.get_user_notifications(user_id, skip, limit)


@router.get(
    "/unread/count",
    response_model=int,
    status_code=status.HTTP_200_OK,
)
async def get_unread_count(
    user_id: int = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service),
    response: Response = None,
):
    cache_key = f"notifications:unread:{user_id}"
    cached = await redis_utils.get_cache(cache_key)
    if cached is not None:
        if response is not None:
            response.headers["X-Cache"] = "HIT"
        return cached

    if response is not None:
        response.headers["X-Cache"] = "MISS"

    return await service.get_unread_count(user_id)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_as_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service),
):
    return await service.mark_as_read(notification_id, user_id)


@router.patch(
    "/read-all",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def mark_all_as_read(
    user_id: int = Depends(get_current_user_id),
    service: NotificationService = Depends(get_notification_service),
):
    await service.mark_all_as_read(user_id)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    from app.websocket.manager import ws_manager

    await websocket.accept()

    try:
        data = await websocket.receive_json()
        user_id = data.get("user_id")

        if not user_id:
            await websocket.close(code=1008)
            return

        await ws_manager.connect(user_id, websocket)

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await ws_manager.disconnect(user_id, websocket)
    except Exception:
        await websocket.close()
