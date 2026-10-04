import uuid
from datetime import datetime
from typing import Dict, Any
from .base_connector import BaseMessageConnector

class SMSConnector(BaseMessageConnector):
    def __init__(self):
        super().__init__(source_id="src-sms", name="Android SMS Service", source_type="SMS")
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
            "id": raw_data.get("id", f"sms-{uuid.uuid4().hex[:8]}"),
            "source": "SMS",
            "sender": raw_data.get("sender", "Unknown SMS Sender"),
            "recipient": raw_data.get("recipient", "Device Primary SIM"),
            "content": raw_data.get("content", ""),
            "timestamp": raw_data.get("timestamp", datetime.now().strftime("%I:%M %p")),
            "metadata": {
                "telephony_sub_id": raw_data.get("sub_id", 1),
                "sms_center": raw_data.get("smsc", "+919800000001")
            }
        }
