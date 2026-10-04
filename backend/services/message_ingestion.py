import uuid
from datetime import datetime
from typing import Dict, Any

class MessageIngestionService:
    @staticmethod
    def ingest(raw_data: Dict[str, Any], default_source: str = "DEMO") -> Dict[str, Any]:
        """Normalizes and preprocesses incoming messages from diverse sources"""
        msg_id = raw_data.get("id") or f"msg-{uuid.uuid4().hex[:8]}"
        content = raw_data.get("content", "").strip()
        sender = raw_data.get("sender", "Unknown Sender").strip()
        source = raw_data.get("source", default_source).upper()
        timestamp = raw_data.get("timestamp") or datetime.now().strftime("%I:%M %p")
        recipient = raw_data.get("recipient", "User")
        metadata = raw_data.get("metadata", {})

        return {
            "id": msg_id,
            "source": source,
            "sender": sender,
            "recipient": recipient,
            "content": content,
            "timestamp": timestamp,
            "metadata": metadata
        }
