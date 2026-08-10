from __future__ import annotations

import hashlib
import html
import logging
import re
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import requests
from dateutil import parser as date_parser

from .config import Source
from .models import Article

LOGGER = logging.getLogger(__name__)
USER_AGENT = "Ether3D-News/1.0 (+https://github.com/)"


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [(k, v) for k, v in parse_qsl(parts.query) if not k.lower().startswith("utm_")]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), ""))


def article_id(url: str) -> str:
    return hashlib.sha256(canonical_url(url).encode("utf-8")).hexdigest()[:20]


def plain_text(value: str, limit: int = 1200) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = re.sub(r"\s+", " ", html.unescape(value)).strip()
    return value[:limit]


def _published(entry: dict) -> datetime | None:
    raw = entry.get("published") or entry.get("updated")
    if not raw:
        return None
    try:
        parsed = date_parser.parse(raw)
        return parsed.replace(tzinfo=parsed.tzinfo or timezone.utc).astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError):
        return None


def collect_source(source: Source, timeout: int = 25) -> list[Article]:
    response = requests.get(source.feed_url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"Feed invalido: {feed.bozo_exception}")
    articles = []
    for entry in feed.entries:
        url = canonical_url(entry.get("link", ""))
        title = plain_text(entry.get("title", ""), 300)
        if not url or not title:
            continue
        excerpt = entry.get("summary") or entry.get("description") or ""
        articles.append(Article(
            id=article_id(url), source=source.name, title=title, url=url,
            published_at=_published(entry), excerpt=plain_text(excerpt),
        ))
    return articles


def collect_all(sources: tuple[Source, ...]) -> list[Article]:
    articles: list[Article] = []
    for source in sources:
        try:
            found = collect_source(source)
            LOGGER.info("%s: %d itens coletados", source.name, len(found))
            articles.extend(found)
        except Exception as exc:  # one broken source must not stop the digest
            LOGGER.warning("Falha ao coletar %s: %s", source.name, exc)
    return articles

