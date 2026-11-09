from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher

from jsonhelpbot.config import Config
from jsonhelpbot.handlers import common, convert


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    config = Config.from_env()
    bot = Bot(token=config.bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(common.router)
    dispatcher.include_router(convert.router)
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()
