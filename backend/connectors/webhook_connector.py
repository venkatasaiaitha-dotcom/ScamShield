import uuid
from datetime import datetime
from typing import Dict, Any
from .base_connector import BaseMessageConnector

class WebhookConnector(BaseMessageConnector):
    def __init__(self):
        super().__init__(source_id="src-webhook", name="Security Ingestion Webhook", source_type="WEBHOOK")
        self._connected = True

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def requires_permission(self) -> bool:
        return False

    def permission_status(self) -> str:
        return "GRANTED"

    def receive_message(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": raw_data.get("id", f"whk-{uuid.uuid4().hex[:8]}"),
            "source": "WEBHOOK",
            "sender": raw_data.get("sender", "Webhook Client"),
            "recipient": raw_data.get("recipient", "ScamShield Agent"),
            "content": raw_data.get("content", ""),
            "timestamp": raw_data.get("timestamp", datetime.now().strftime("%I:%M %p")),
            "metadata": raw_data.get("metadata", {})
        }
