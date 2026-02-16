"""
Unit tests for the WebSocket module.

Tests:
- WebSocket connection management
- User notifications via WebSocket
- Admin dashboard WebSocket connections
- Broadcasting to users
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.websocket.manager import WebSocketManager
from fastapi import WebSocket


@pytest.fixture
def ws_manager():
    """Create a fresh WebSocketManager instance."""
    return WebSocketManager()


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket."""
    websocket = AsyncMock(spec=WebSocket)
    websocket.send_json = AsyncMock()
    return websocket


@pytest.mark.unit
@pytest.mark.asyncio
class TestWebSocketManager:
    """Test cases for WebSocketManager."""

    async def test_connect_user(self, ws_manager, mock_websocket):
        """Test connecting a user WebSocket."""
        user_id = 1

        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(user_id, mock_websocket)

        assert user_id in ws_manager.active_connections
        assert mock_websocket in ws_manager.active_connections[user_id]

    async def test_connect_multiple_sockets_same_user(self, ws_manager, mock_websocket):
        """Test connecting multiple WebSockets for same user."""
        user_id = 1
        websocket2 = AsyncMock(spec=WebSocket)

        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(user_id, mock_websocket)
            await ws_manager.connect(user_id, websocket2)

        assert len(ws_manager.active_connections[user_id]) == 2

    async def test_connect_different_users(self, ws_manager, mock_websocket):
        """Test connecting WebSockets for different users."""
        user1_id = 1
        user2_id = 2
        websocket2 = AsyncMock(spec=WebSocket)

        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(user1_id, mock_websocket)
            await ws_manager.connect(user2_id, websocket2)

        assert user1_id in ws_manager.active_connections
        assert user2_id in ws_manager.active_connections

    async def test_disconnect_user(self, ws_manager, mock_websocket):
        """Test disconnecting a user WebSocket."""
        user_id = 1

        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(user_id, mock_websocket)
            await ws_manager.disconnect(user_id, mock_websocket)

        assert user_id not in ws_manager.active_connections

    async def test_disconnect_one_of_multiple_sockets(self, ws_manager, mock_websocket):
        """Test disconnecting one WebSocket when user has multiple."""
        user_id = 1
        websocket2 = AsyncMock(spec=WebSocket)

        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(user_id, mock_websocket)
            await ws_manager.connect(user_id, websocket2)
            await ws_manager.disconnect(user_id, mock_websocket)

        assert user_id in ws_manager.active_connections
        assert len(ws_manager.active_connections[user_id]) == 1
        assert websocket2 in ws_manager.active_connections[user_id]

    async def test_disconnect_nonexistent_user(self, ws_manager, mock_websocket):
        """Test disconnecting a user that was never connected."""
        user_id = 999

        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.disconnect(user_id, mock_websocket)

        # Should not raise an error
        assert user_id not in ws_manager.active_connections

    async def test_send_to_user_success(self, ws_manager, mock_websocket):
        """Test sending message to connected user."""
        user_id = 1
        payload = {"type": "notification", "message": "Test"}

        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(user_id, mock_websocket)
            await ws_manager.send_to_user(user_id, payload)

        mock_websocket.send_json.assert_called_once_with(payload)

    async def test_send_to_user_not_connected(self, ws_manager):
        """Test sending message to non-connected user."""
        user_id = 999
        payload = {"type": "notification", "message": "Test"}

        # Should not raise an error
        await ws_manager.send_to_user(user_id, payload)

    async def test_send_to_user_multiple_connections(self, ws_manager):
        """Test sending message to user with multiple connections."""
        user_id = 1
        websocket1 = AsyncMock(spec=WebSocket)
        websocket2 = AsyncMock(spec=WebSocket)
        payload = {"type": "notification", "message": "Test"}

        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(user_id, websocket1)
            await ws_manager.connect(user_id, websocket2)
            await ws_manager.send_to_user(user_id, payload)

        websocket1.send_json.assert_called_once_with(payload)
        websocket2.send_json.assert_called_once_with(payload)

    async def test_send_to_user_failure_cleanup(self, ws_manager):
        """Test cleanup when sending message fails."""
        user_id = 1
        websocket = AsyncMock(spec=WebSocket)
        websocket.send_json.side_effect = Exception("Connection closed")
        payload = {"type": "notification", "message": "Test"}

        with (
            patch.object(
                ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
            ),
            patch.object(
                ws_manager, "disconnect", new_callable=AsyncMock
            ) as mock_disconnect,
        ):
            await ws_manager.connect(user_id, websocket)
            await ws_manager.send_to_user(user_id, payload)

            mock_disconnect.assert_called_once_with(user_id, websocket)

    async def test_connect_admin_dashboard(self, ws_manager, mock_websocket):
        """Test connecting admin dashboard WebSocket."""
        admin_id = 1

        await ws_manager.connect_admin_dashboard(admin_id, mock_websocket)

        assert admin_id in ws_manager.admin_connections
        assert mock_websocket in ws_manager.admin_connections[admin_id]
        # Should send initial active user count
        mock_websocket.send_json.assert_called_once()

    async def test_disconnect_admin_dashboard(self, ws_manager, mock_websocket):
        """Test disconnecting admin dashboard WebSocket."""
        admin_id = 1

        await ws_manager.connect_admin_dashboard(admin_id, mock_websocket)
        await ws_manager.disconnect_admin_dashboard(admin_id, mock_websocket)

        assert admin_id not in ws_manager.admin_connections

    async def test_broadcast_active_users_to_admins(self, ws_manager):
        """Test broadcasting active user count to admins."""
        admin_id = 1
        user_id = 2
        admin_ws = AsyncMock(spec=WebSocket)
        user_ws = AsyncMock(spec=WebSocket)

        # Connect admin dashboard and regular user
        await ws_manager.connect_admin_dashboard(admin_id, admin_ws)

        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(user_id, user_ws)

        # Manually trigger broadcast
        await ws_manager.broadcast_active_users_to_admins()

        # Admin should receive update (at least twice: once on connect, once on broadcast)
        assert admin_ws.send_json.call_count >= 2

    async def test_broadcast_active_users_failure_cleanup(self, ws_manager):
        """Test cleanup when broadcasting to admin fails."""
        admin_id = 1
        admin_ws = AsyncMock(spec=WebSocket)
        admin_ws.send_json.side_effect = Exception("Connection closed")

        ws_manager.admin_connections[admin_id] = [admin_ws]

        with patch.object(
            ws_manager, "disconnect_admin_dashboard", new_callable=AsyncMock
        ) as mock_disconnect:
            await ws_manager.broadcast_active_users_to_admins()

            mock_disconnect.assert_called_once_with(admin_id, admin_ws)

    async def test_multiple_admin_connections(self, ws_manager):
        """Test multiple admin dashboard connections."""
        admin1_id = 1
        admin2_id = 2
        admin1_ws = AsyncMock(spec=WebSocket)
        admin2_ws = AsyncMock(spec=WebSocket)

        await ws_manager.connect_admin_dashboard(admin1_id, admin1_ws)
        await ws_manager.connect_admin_dashboard(admin2_id, admin2_ws)

        assert len(ws_manager.admin_connections) == 2

    async def test_active_connections_count(self, ws_manager):
        """Test counting active connections."""
        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(1, AsyncMock(spec=WebSocket))
            await ws_manager.connect(2, AsyncMock(spec=WebSocket))
            await ws_manager.connect(3, AsyncMock(spec=WebSocket))

        assert len(ws_manager.active_connections) == 3

    async def test_admin_receives_initial_count(self, ws_manager, mock_websocket):
        """Test that admin receives initial active user count on connect."""
        admin_id = 1
        user_id = 2
        user_ws = AsyncMock(spec=WebSocket)

        # Connect a regular user first
        with patch.object(
            ws_manager, "broadcast_active_users_to_admins", new_callable=AsyncMock
        ):
            await ws_manager.connect(user_id, user_ws)

        # Connect admin and verify they receive initial count
        await ws_manager.connect_admin_dashboard(admin_id, mock_websocket)

        # Should send initial active user count
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "active_users_update"
        assert call_args["count"] == 1
