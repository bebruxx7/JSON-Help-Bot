from __future__ import annotations

import io
import logging

from aiogram import Bot, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from jsonhelpbot.serializers.json_to_message import PayloadError, send_from_json
from jsonhelpbot.serializers.message_to_json import content_type_of, message_to_dict
from jsonhelpbot.serializers.schema import SUPPORTED_TYPES
from jsonhelpbot.utils.json_tools import loads_payload
from jsonhelpbot.utils.replies import reply_with_json

logger = logging.getLogger(__name__)
router = Router(name="convert")

MAX_JSON_FILE_BYTES = 5 * 1024 * 1024


@router.message()
async def convert_message(message: Message, bot: Bot) -> None:
    if message.text is not None:
        payload = loads_payload(message.text)
        if payload is not None:
            await _render(message, payload, bot)
            return
        if message.text.lstrip().startswith("{"):
            await message.reply(
                "Could not parse JSON: expected an object with a string 'type' field."
            )
            return
    if message.document is not None and _is_json_document(message):
        payload = await _payload_from_document(message, bot)
        if payload is not None:
            await _render(message, payload, bot)
        return
    if content_type_of(message) not in SUPPORTED_TYPES:
        return
    await reply_with_json(message, message_to_dict(message))


async def _render(message: Message, payload: dict, bot: Bot) -> None:
    try:
        await send_from_json(
            bot,
            message.chat.id,
            payload,
            reply_to_message_id=message.message_id,
        )
    except PayloadError as exc:
        await message.reply(f"Invalid JSON: {exc}")
    except TelegramAPIError as exc:
        await message.reply(f"Telegram rejected the message: {exc.message or exc}")


async def _payload_from_document(message: Message, bot: Bot) -> dict | None:
    document = message.document
    if document.file_size is not None and document.file_size > MAX_JSON_FILE_BYTES:
        await message.reply("The JSON file is too large (5 MB max).")
        return None
    buffer = io.BytesIO()
    try:
        await bot.download(document, destination=buffer)
    except TelegramAPIError as exc:
        logger.warning("Failed to download JSON document: %s", exc)
        await message.reply("Could not download the file from Telegram.")
        return None
    try:
        raw = buffer.getvalue().decode("utf-8-sig")
    except UnicodeDecodeError:
        await message.reply("The file must be UTF-8 encoded.")
        return None
    payload = loads_payload(raw)
    if payload is None:
        await message.reply(
            "The file does not contain a valid JSON object with a string 'type' field."
        )
        return None
    return payload


def _is_json_document(message: Message) -> bool:
    document = message.document
    if document is None:
        return False
    name = (document.file_name or "").lower()
    mime_type = (document.mime_type or "").lower()
    return name.endswith(".json") or mime_type in {"application/json", "text/json"}
