from typing import Dict, List

from fastapi import WebSocket

from app.utils.logging import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.debug(f"WebSocket connected for user {user_id}")

    async def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.debug(f"WebSocket disconnected for user {user_id}")

    async def send_to_user(self, user_id: int, payload: dict):
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(payload)
                except Exception as e:
                    logger.error(
                        f"Failed to send WebSocket message to user {user_id}: {e}"
                    )
                    disconnected.append(websocket)

            for ws in disconnected:
                await self.disconnect(user_id, ws)


ws_manager = WebSocketManager()
