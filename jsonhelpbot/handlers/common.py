from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from jsonhelpbot.serializers.message_to_json import message_to_dict
from jsonhelpbot.texts import HELP_TEXT, START_TEXT
from jsonhelpbot.utils.replies import reply_with_json

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(START_TEXT)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(Command("json"))
async def cmd_json(message: Message) -> None:
    target = message.reply_to_message
    if target is None:
        await message.reply(
            "Reply with /json to the message you want to convert to JSON."
        )
        return
    await reply_with_json(target, message_to_dict(target))
