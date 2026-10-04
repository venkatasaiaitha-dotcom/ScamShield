import uuid
from datetime import datetime
from typing import Dict, Any
from .base_connector import BaseMessageConnector

class EmailConnector(BaseMessageConnector):
    def __init__(self):
        super().__init__(source_id="src-email", name="Email Inbox Monitor", source_type="EMAIL")
        self._connected = True
        self._permission_granted = True

    def connect(self) -> bool:
        self._connected = True
        self._permission_granted = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def requires_permission(self) -> bool:
        return True

    def permission_status(self) -> str:
        return "GRANTED" if self._permission_granted else "REQUIRED"

    def receive_message(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": raw_data.get("id", f"eml-{uuid.uuid4().hex[:8]}"),
            "source": "EMAIL",
            "sender": raw_data.get("sender", "service@notification.com"),
            "recipient": raw_data.get("recipient", "user@myinbox.com"),
            "content": raw_data.get("content", ""),
            "timestamp": raw_data.get("timestamp", datetime.now().strftime("%I:%M %p")),
            "metadata": {
                "subject": raw_data.get("subject", "Inbound Notification"),
                "spf_dkim_pass": raw_data.get("spf_pass", False)
            }
        }
