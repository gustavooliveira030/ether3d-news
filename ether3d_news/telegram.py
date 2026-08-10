from __future__ import annotations

import html
import time

import requests

from .models import Article, SelectedNews


def format_message(position: int, total: int, article: Article, selected: SelectedNews) -> str:
    return (
        f"<b>Ether3D News · {position}/{total}</b>\n\n"
        f"<b>{html.escape(selected.headline_pt)}</b>\n\n"
        f"{html.escape(selected.summary_pt)}\n\n"
        f"<b>Por que importa:</b> {html.escape(selected.relevance)}\n\n"
        f"Fonte: {html.escape(article.source)}\n"
        f'<a href="{html.escape(article.url, quote=True)}">Ler a noticia completa</a>'
    )


def send_message(token: str, chat_id: str, text: str, timeout: int = 25) -> None:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False},
        timeout=timeout,
    )
    response.raise_for_status()
    body = response.json()
    if not body.get("ok"):
        raise RuntimeError(f"Telegram recusou a mensagem: {body.get('description', 'erro desconhecido')}")


def send_digest(token: str, chat_id: str, pairs: list[tuple[Article, SelectedNews]]) -> None:
    total = len(pairs)
    for index, (article, selected) in enumerate(pairs, 1):
        send_message(token, chat_id, format_message(index, total, article, selected))
        if index < total:
            time.sleep(1)

