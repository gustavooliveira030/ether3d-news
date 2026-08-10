from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .collector import canonical_url, collect_all
from .config import SOURCES, Settings
from .history import History
from .selector import select_news
from .telegram import send_message

LOGGER = logging.getLogger(__name__)


def prepare_candidates(articles, sent_ids: set[str], max_age_days: int, limit: int):
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    seen_urls = set()
    candidates = []
    for article in sorted(articles, key=lambda a: a.published_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True):
        url = canonical_url(article.url)
        if article.id in sent_ids or url in seen_urls:
            continue
        if article.published_at and article.published_at < cutoff:
            continue
        seen_urls.add(url)
        candidates.append(article)
    return candidates[:limit]


def run() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = Settings.from_env()
    history = History(Path(os.getenv("HISTORY_PATH", "data/history.json")))
    candidates = prepare_candidates(
        collect_all(SOURCES), history.ids, settings.max_age_days, settings.max_candidates
    )
    if not candidates:
        LOGGER.info("Nenhuma noticia nova encontrada")
        return 0

    selected = select_news(candidates, settings.news_per_run)
    by_id = {article.id: article for article in candidates}
    if not selected:
        LOGGER.info("Nenhuma noticia relevante selecionada")
        return 0

    # Save after each successful send: a partial Telegram failure never marks unsent items.
    total = len(selected)
    for index, item in enumerate(selected, 1):
        article = by_id[item.article_id]
        from .telegram import format_message
        send_message(settings.telegram_bot_token, settings.telegram_chat_id, format_message(index, total, article, item))
        history.add(article)
        history.save()
        LOGGER.info("Enviada: %s", article.title)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
