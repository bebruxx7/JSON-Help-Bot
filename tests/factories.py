from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from aiogram.types import Chat, Message, User

CHAT = Chat(id=100, type="private", first_name="Tester")
USER = User(id=100, is_bot=False, first_name="Tester", username="tester")
DATE = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)


def make_message(**overrides: Any) -> Message:
    payload: dict[str, Any] = {
        "message_id": 1,
        "date": DATE,
        "chat": CHAT,
        "from": USER,
    }
    payload.update(overrides)
    return Message.model_validate(payload)
