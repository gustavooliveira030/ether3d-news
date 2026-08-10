from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import Article


class History:
    def __init__(self, path: Path):
        self.path = path
        self.data = {"version": 1, "sent": []}
        if path.exists():
            self.data = json.loads(path.read_text(encoding="utf-8"))

    @property
    def ids(self) -> set[str]:
        return {item["id"] for item in self.data.get("sent", [])}

    def add(self, article: Article) -> None:
        self.data.setdefault("sent", []).append({
            "id": article.id,
            "url": article.url,
            "source": article.source,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        })

    def save(self, keep: int = 1000) -> None:
        self.data["sent"] = self.data.get("sent", [])[-keep:]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

