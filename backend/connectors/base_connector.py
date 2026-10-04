from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseMessageConnector(ABC):
    def __init__(self, source_id: str, name: str, source_type: str):
        self.source_id = source_id
        self.name = name
        self.source_type = source_type
        self._connected = True

    @abstractmethod
    def connect(self) -> bool:
        """Establishes connection to the message source with required credentials/permissions"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Gracefully disconnects and pauses monitoring for this source"""
        pass

    def is_connected(self) -> bool:
        return self._connected

    @abstractmethod
    def requires_permission(self) -> bool:
        """Returns True if platform permission or approved integration token is mandatory"""
        pass

    @abstractmethod
    def permission_status(self) -> str:
        """Returns GRANTED, REQUIRED, or UNSUPPORTED"""
        pass

    @abstractmethod
    def receive_message(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes external raw message payload into standard ScamShield schema"""
        pass
