from __future__ import annotations

import logging
import re

from deep_translator import GoogleTranslator

from .models import Article, SelectedNews

LOGGER = logging.getLogger(__name__)

# Weighted editorial rules. Terms are intentionally in English and Portuguese
# because some feeds occasionally publish localized or mixed-language metadata.
KEYWORDS = {
    "3d print": 8, "3d-print": 8, "additive manufactur": 7,
    "printer": 5, "impressora": 5, "filament": 4, "resin": 4,
    "slicer": 4, "extruder": 4, "hotend": 4, "fdm": 4, "fff": 4,
    "sla": 4, "sls": 4, "metal printing": 5, "bioprint": 5,
    "ultimaker": 3, "bambu lab": 3, "prusa": 3, "creality": 3,
    "formlabs": 3, "elegoo": 3, "anycubic": 3, "makerbot": 3,
    "launch": 2, "new ": 2, "research": 2, "software": 2,
}

NEGATIVE_KEYWORDS = {
    "deal": -6, "discount": -6, "coupon": -6, "best price": -5,
    "black friday": -7, "prime day": -7, "sponsored": -8,
    "affiliate": -6, "giveaway": -5,
}


def relevance_score(article: Article) -> int:
    text = f"{article.title} {article.excerpt}".lower()
    score = sum(weight for term, weight in KEYWORDS.items() if term in text)
    score += sum(weight for term, weight in NEGATIVE_KEYWORDS.items() if term in text)
    # Title matches are stronger editorial signals than excerpt matches.
    title = article.title.lower()
    score += sum(max(1, weight // 2) for term, weight in KEYWORDS.items() if term in title)
    return score


def _translate(text: str, translator: GoogleTranslator) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "Leia a materia completa no link abaixo."
    try:
        # Google Translate's public web endpoint accepts texts below 5,000 chars.
        return translator.translate(text[:4500]).strip()
    except Exception as exc:
        LOGGER.warning("Falha na traducao; usando texto original: %s", exc)
        return text


def _why_it_matters(article: Article) -> str:
    text = f"{article.title} {article.excerpt}".lower()
    if any(term in text for term in ("filament", "resin", "material")):
        return "Pode influenciar a escolha de materiais, custos e qualidade das impressões."
    if any(term in text for term in ("slicer", "software", "firmware")):
        return "Pode melhorar o fluxo de preparação, controle e qualidade das impressões."
    if any(term in text for term in ("research", "study", "bioprint", "medical")):
        return "Mostra uma nova aplicação ou avanço técnico relevante para o setor."
    if any(term in text for term in ("launch", "printer", "impressora")):
        return "Ajuda a acompanhar novos equipamentos e mudanças no mercado de impressão 3D."
    return "É um desenvolvimento recente com possível impacto no ecossistema de impressão 3D."


def select_news(articles: list[Article], count: int) -> list[SelectedNews]:
    ranked = sorted(
        enumerate(articles),
        key=lambda pair: (relevance_score(pair[1]), -pair[0]),
        reverse=True,
    )
    # A feed/category match is already a useful signal, but exclude candidates
    # with no explicit 3D-printing vocabulary or with strongly promotional text.
    chosen = [article for _, article in ranked if relevance_score(article) > 0][:count]
    translator = GoogleTranslator(source="auto", target="pt")
    return [
        SelectedNews(
            article_id=article.id,
            headline_pt=_translate(article.title, translator)[:180],
            summary_pt=_translate(article.excerpt, translator)[:900],
            relevance=_why_it_matters(article),
        )
        for article in chosen
    ]
