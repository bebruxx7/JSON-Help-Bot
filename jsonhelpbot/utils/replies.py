from __future__ import annotations

import html

from aiogram.types import BufferedInputFile, Message

from jsonhelpbot.utils.json_tools import MAX_JSON_TEXT, dumps


async def reply_with_json(
    message: Message,
    payload: dict,
    caption: str = "JSON is too long, sending it as a file.",
) -> None:
    text = dumps(payload)
    if len(text) <= MAX_JSON_TEXT:
        await message.reply(f"<pre>{html.escape(text)}</pre>", parse_mode="HTML")
        return
    document = BufferedInputFile(
        text.encode("utf-8"),
        filename=f"message_{message.message_id}.json",
    )
    await message.reply_document(document, caption=caption)
