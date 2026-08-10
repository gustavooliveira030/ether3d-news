from __future__ import annotations

from datetime import datetime

from dataclasses import dataclass


@dataclass
class Article:
    id: str
    source: str
    title: str
    url: str
    published_at: datetime | None = None
    excerpt: str = ""


@dataclass
class SelectedNews:
    article_id: str
    headline_pt: str
    summary_pt: str
    relevance: str
