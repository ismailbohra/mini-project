from typing import Dict, List

from fastapi import WebSocket

from app.utils.logging import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.admin_connections: Dict[
            int, List[WebSocket]
        ] = {}  # Separate connections for admin dashboard

    async def connect(self, user_id: int, websocket: WebSocket):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.debug(f"WebSocket connected for user {user_id}")

        # Broadcast active user count to admins
        await self.broadcast_active_users_to_admins()

    async def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.debug(f"WebSocket disconnected for user {user_id}")

        # Broadcast active user count to admins
        await self.broadcast_active_users_to_admins()

    async def connect_admin_dashboard(self, user_id: int, websocket: WebSocket):
        """Connect admin dashboard websocket for real-time analytics updates."""
        if user_id not in self.admin_connections:
            self.admin_connections[user_id] = []
        self.admin_connections[user_id].append(websocket)
        logger.debug(f"Admin dashboard WebSocket connected for user {user_id}")

        # Send initial active user count
        await websocket.send_json(
            {"type": "active_users_update", "count": len(self.active_connections)}
        )

    async def disconnect_admin_dashboard(self, user_id: int, websocket: WebSocket):
        """Disconnect admin dashboard websocket."""
        if user_id in self.admin_connections:
            if websocket in self.admin_connections[user_id]:
                self.admin_connections[user_id].remove(websocket)
            if not self.admin_connections[user_id]:
                del self.admin_connections[user_id]
        logger.debug(f"Admin dashboard WebSocket disconnected for user {user_id}")

    async def broadcast_active_users_to_admins(self):
        """Broadcast active user count to all connected admin dashboards."""
        active_count = len(self.active_connections)
        payload = {"type": "active_users_update", "count": active_count}

        disconnected = []
        for user_id, connections in self.admin_connections.items():
            for websocket in connections:
                try:
                    await websocket.send_json(payload)
                except Exception as e:
                    logger.error(
                        f"Failed to send active users update to admin {user_id}: {e}"
                    )
                    disconnected.append((user_id, websocket))

        # Clean up disconnected websockets
        for user_id, ws in disconnected:
            await self.disconnect_admin_dashboard(user_id, ws)

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
