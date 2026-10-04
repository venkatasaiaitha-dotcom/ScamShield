import json
import logging
from collections import defaultdict
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger("scamshield.websocket")

class SecureNotificationService:
    """
    Part 7: Secure, tenant-isolated WebSocket notification service.
    Only sends user-specific events to connections authenticated as that user.
    """
    def __init__(self):
        # Maps user_id -> Set of active WebSockets
        self.user_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        # Reverse map socket -> user_id for fast cleanup
        self.socket_users: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.user_connections[user_id].add(websocket)
        self.socket_users[websocket] = user_id
        logger.info(f"WebSocket connected for user {user_id} (active connections: {len(self.user_connections[user_id])})")

    def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None):
        target_user = user_id or self.socket_users.pop(websocket, None)
        self.socket_users.pop(websocket, None)
        if target_user and target_user in self.user_connections:
            self.user_connections[target_user].discard(websocket)
            if not self.user_connections[target_user]:
                del self.user_connections[target_user]
            logger.info(f"WebSocket disconnected for user {target_user}")

    async def send_to_user(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """Sends payload ONLY to the specific authenticated user's active WebSocket sessions."""
        connections = self.user_connections.get(user_id, set())
        if not connections:
            return

        payload = json.dumps({
            "event": event_type,
            "data": data
        })

        dead_connections = set()
        for ws in list(connections):
            try:
                await ws.send_text(payload)
            except Exception as e:
                logger.warning(f"Failed to send to user {user_id} socket: {e}")
                dead_connections.add(ws)

        for dead in dead_connections:
            self.disconnect(dead)

    async def dispatch_analysis_event(self, user_id: str, analysis_dict: Dict[str, Any], stats_dict: Dict[str, Any]):
        risk_level = analysis_dict["risk_level"]
        risk_score = analysis_dict["risk_score"]

        notification_tier = "NONE"
        if risk_level == "HIGH" or risk_score >= 70:
            notification_tier = "PROMINENT_ALERT"
        elif risk_level == "SUSPICIOUS" or risk_score >= 30:
            notification_tier = "SUBTLE_NOTICE"

        await self.send_to_user(user_id, "MESSAGE_PROCESSED", {
            "analysis": analysis_dict,
            "stats": stats_dict,
            "notification_tier": notification_tier
        })

    async def broadcast_system(self, event_type: str, data: Dict[str, Any]):
        """For rare system-wide notifications (e.g. maintenance); does not leak personal data."""
        payload = json.dumps({"event": event_type, "data": data})
        for user_id, conns in list(self.user_connections.items()):
            for ws in list(conns):
                try:
                    await ws.send_text(payload)
                except Exception:
                    pass

    broadcast = broadcast_system

notification_service = SecureNotificationService()
NotificationService = SecureNotificationService
