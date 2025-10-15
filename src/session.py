"""Chat Session Management"""

from typing import Optional


class ChatSession:
    """Manages chat message history in memory"""

    def __init__(self):
        self._messages: list[dict] = []

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the session"""
        self._messages.append({"role": role, "content": content})

    def get_messages(self) -> list[dict]:
        """Get all messages in the session"""
        return self._messages.copy()

    def get_last_message(self) -> Optional[dict]:
        """Get the last message in the session"""
        return self._messages[-1] if self._messages else None

    def clear_messages(self) -> None:
        """Clear all messages from the session"""
        self._messages.clear()

    def get_message_count(self) -> int:
        """Get the number of messages in the session"""
        return len(self._messages)
