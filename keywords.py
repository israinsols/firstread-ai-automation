"""Polite, rate-limited keyword discovery from Google Autosuggest."""

from __future__ import annotations

import re
import string
import time
import unicodedata
from typing import Any

import requests

from config import SiteConfig
from db import initialize, save_keyword

AUTOSUGGEST_URL = "https://suggestqueries.google.com/complete/search"
PREFIXES = ("how", "what", "best", "price", "vs", "which", "where")
BOOST_TERMS = ("uk", "united kingdom", "britain", "price", "in the uk")
QUESTION_TERMS = ("how", "what", "why", "when", "where", "?")


def normalize_keyword(value: str) -> str:
    folded = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(folded.split())


def dedupe_keywords(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = " ".join(value.split()).strip()
        normalized = normalize_keyword(cleaned)
        if cleaned and normalized not in seen:
            seen.add(normalized)
            result.append(cleaned)
    return result


def score_keyword(keyword: str) -> float:
    normalized = normalize_keyword(keyword)
    words = normalized.split()
    score = max(0.0, 30.0 - len(words) * 2.0)
    if any(term in normalized for term in QUESTION_TERMS):
        score += 12.0
    if any(re.search(rf"\b{re.escape(term)}\b", normalized) for term in BOOST_TERMS):
        score += 20.0
    if len(words) >= 3:
        score += 3.0
    return round(score, 2)


def query_variants(seed: str) -> list[str]:
    base = seed.strip()
    variants = [base]
    variants.extend(f"{base} {letter}" for letter in string.ascii_lowercase)
    variants.extend(f"{prefix} {base}" for prefix in PREFIXES)
    return dedupe_keywords(variants)


def fetch_suggestions(
    query: str, session: requests.Session, language: str = "en-GB"
) -> list[str]:
    lang = language.split("-")[0] or "en"
    response = session.get(
        AUTOSUGGEST_URL,
        params={"client": "firefox", "q": query, "hl": lang, "gl": "uk"},
        headers={"User-Agent": "Firstread.co.uk/1.0 (+https://firstread.co.uk/)"},
        timeout=15,
    )
    response.raise_for_status()
    payload: Any = response.json()
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise ValueError("Autosuggest returned an unexpected response.")
    return [item for item in payload[1] if isinstance(item, str)]


def research_keywords(
    config: SiteConfig,
    session: requests.Session | None = None,
    delay_seconds: float = 1.0,
) -> int:
    """Collect and persist suggestions. No search-result clicks or traffic simulation."""
    if delay_seconds < 0:
        raise ValueError("delay_seconds cannot be negative.")
    initialize(config.database_path)
    client = session or requests.Session()
    added: set[str] = set()
    first_request = True
    try:
        for seed in config.keyword_seeds:
            normalized_seed = normalize_keyword(seed)
            if normalized_seed not in added:
                added.add(normalized_seed)
                is_brand_seed = normalized_seed == normalize_keyword(config.domain)
                save_keyword(
                    config.database_path,
                    seed,
                    normalized_seed,
                    "site-seed" if is_brand_seed else "topic-seed",
                    score_keyword(seed),
                    priority=100 if is_brand_seed else 50,
                )
            for variant in query_variants(seed):
                if not first_request:
                    time.sleep(delay_seconds)
                first_request = False
                for suggestion in fetch_suggestions(variant, client, config.language):
                    for keyword in dedupe_keywords([suggestion]):
                        normalized = normalize_keyword(keyword)
                        if normalized in added:
                            continue
                        added.add(normalized)
                        save_keyword(
                            config.database_path,
                            keyword,
                            normalized,
                            "google-autosuggest",
                            score_keyword(keyword),
                        )
    finally:
        if session is None:
            client.close()
    return len(added)
