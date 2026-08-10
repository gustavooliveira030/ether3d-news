from datetime import datetime, timedelta, timezone

from ether3d_news.collector import article_id, canonical_url, plain_text
from ether3d_news.main import prepare_candidates
from ether3d_news.models import Article, SelectedNews
from ether3d_news.selector import relevance_score
from ether3d_news.telegram import format_message


def article(url="https://Example.com/story/?utm_source=x", days=0):
    return Article(id=article_id(url), source="Fonte", title="Titulo", url=url,
                   published_at=datetime.now(timezone.utc) - timedelta(days=days), excerpt="Resumo")


def test_canonical_url_removes_tracking_and_fragment():
    assert canonical_url("https://Example.com/a/?utm_source=x&x=1#top") == "https://example.com/a?x=1"


def test_plain_text_removes_html():
    assert plain_text("<p>A &amp; B</p>") == "A & B"


def test_candidates_remove_sent_duplicates_and_old():
    fresh = article()
    duplicate = article()
    old = article("https://example.com/old", days=30)
    assert prepare_candidates([fresh, duplicate, old], set(), 10, 10) == [fresh]
    assert prepare_candidates([fresh], {fresh.id}, 10, 10) == []


def test_telegram_message_escapes_content():
    item = SelectedNews(article_id="x", headline_pt="A < B", summary_pt="S & R", relevance="Uso")
    message = format_message(1, 1, article(), item)
    assert "A &lt; B" in message and "S &amp; R" in message


def test_relevance_rules_reward_printing_and_penalize_deals():
    relevant = article()
    relevant.title = "New 3D printer and filament research"
    deal = article("https://example.com/deal")
    deal.title = "Deal and discount coupon"
    assert relevance_score(relevant) > 0
    assert relevance_score(deal) < 0
