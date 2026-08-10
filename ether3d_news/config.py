from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    name: str
    feed_url: str


SOURCES = (
    Source("All3DP", "https://all3dp.com/feed/"),
    Source("Fabbaloo", "https://www.fabbaloo.com/feed"),
    Source("3D Printing Industry", "https://3dprintingindustry.com/feed/"),
    Source("Tom's Hardware 3D Printing", "https://www.tomshardware.com/feeds/tag/3d-printing"),
    Source("Creative Bloq 3D Printing", "https://www.creativebloq.com/feeds/tag/3d-printing"),
)


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_chat_id: str
    max_candidates: int = 35
    news_per_run: int = 4
    max_age_days: int = 10

    @classmethod
    def from_env(cls) -> "Settings":
        required = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise RuntimeError(f"Variaveis obrigatorias ausentes: {', '.join(missing)}")
        return cls(
            telegram_bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            telegram_chat_id=os.environ["TELEGRAM_CHAT_ID"],
        )
