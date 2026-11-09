from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

ENV_FILE = ".env"


@dataclass(frozen=True)
class Config:
    bot_token: str

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv(ENV_FILE)
        token = (os.getenv("BOT_TOKEN") or "").strip()
        if not token:
            raise RuntimeError(
                "BOT_TOKEN is not set. Copy .env.example to .env and paste the token from @BotFather."
            )
        return cls(bot_token=token)
