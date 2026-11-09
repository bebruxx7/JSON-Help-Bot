from __future__ import annotations

from typing import Any

from aiogram.types import Message, Update


def update_to_dict(update: Update) -> dict[str, Any]:
    return update.model_dump(by_alias=True, exclude_none=True, warnings=False)


def message_to_dict(message: Message) -> dict[str, Any]:
    return message.model_dump(by_alias=True, exclude_none=True, warnings=False)
