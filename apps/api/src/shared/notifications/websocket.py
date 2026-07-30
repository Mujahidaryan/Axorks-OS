"""
Axorks OS — WebSocket Notifications

Real-time notification delivery via WebSocket.
Clients connect to /ws/notifications with a valid JWT token.
"""

import json
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError

from src.core.security import verify_access_token

router = APIRouter(tags=["WebSocket"])

# In-memory connection manager (Redis pub/sub for multi-instance in production)
_active_connections: dict[str, list[WebSocket]] = {}


class ConnectionManager:
    """Manages active WebSocket connections per user."""

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        """Accept a WebSocket connection and register it."""
        await websocket.accept()
        key = str(user_id)
        if key not in _active_connections:
            _active_connections[key] = []
        _active_connections[key].append(websocket)

    def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        key = str(user_id)
        if key in _active_connections:
            _active_connections[key] = [
                ws for ws in _active_connections[key] if ws != websocket
            ]
            if not _active_connections[key]:
                del _active_connections[key]

    async def send_to_user(self, user_id: UUID, data: dict) -> None:
        """Send a message to all WebSocket connections for a user."""
        key = str(user_id)
        if key in _active_connections:
            message = json.dumps(data)
            dead_connections = []
            for ws in _active_connections[key]:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead_connections.append(ws)
            # Clean up dead connections
            for ws in dead_connections:
                self.disconnect(user_id, ws)


manager = ConnectionManager()


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time notifications.

    Client connects with: ws://host/ws/notifications?token=<jwt>
    Server sends JSON messages when new notifications arrive.
    """
    # Extract token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Token required")
        return

    # Validate token
    try:
        payload = verify_access_token(token)
        user_id = UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        await websocket.close(code=4001, reason="Invalid token")
        return

    # Register connection
    await manager.connect(user_id, websocket)

    try:
        # Keep connection alive — listen for client messages (heartbeat/ping)
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
