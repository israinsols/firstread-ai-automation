from config import SiteConfig
from db import connect
from keywords import (
    dedupe_keywords,
    fetch_suggestions,
    normalize_keyword,
    research_keywords,
    score_keyword,
)


def test_keyword_deduplication_is_case_and_whitespace_insensitive():
    assert dedupe_keywords([" Firstread.co.uk ", "firstread.co.uk", "Firstread   co.uk", ""]) == [
        "Firstread.co.uk",
        "Firstread co.uk",
    ]
    assert normalize_keyword("  Firstread   CO.UK ") == "firstread co.uk"


def test_question_and_pakistan_terms_get_a_higher_score():
    plain = score_keyword("useful technology guide")
    specific = score_keyword("how to choose technology price UK")
    assert specific > plain


def test_research_always_saves_exact_domain_seed_before_suggestions(tmp_path, monkeypatch):
    class MockResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return ["firstread.co.uk", []]

    class MockSession:
        def get(self, *args, **kwargs):
            return MockResponse()

    config = SiteConfig(
        root=tmp_path,
        site_name="Firstread.co.uk",
        domain="firstread.co.uk",
        base_path="",
        niche="news and practical guides",
        posts_per_day=1,
        language="en-GB",
        author="Firstread Editorial",
        auto_publish=False,
        social_telegram=False,
        social_facebook=False,
        social_pinterest=False,
        keyword_seeds=("firstread.co.uk",),
        contact_email="hello@firstread.co.uk",
        gsc_site_url="sc-domain:firstread.co.uk",
    )
    monkeypatch.setattr("keywords.query_variants", lambda seed: [seed])

    assert research_keywords(config, session=MockSession(), delay_seconds=0) == 1
    with connect(config.database_path) as connection:
        rows = connection.execute(
            "SELECT keyword, source, priority FROM keywords"
        ).fetchall()
    assert [(row["keyword"], row["source"], row["priority"]) for row in rows] == [
        ("firstread.co.uk", "site-seed", 100)
    ]


def test_autosuggest_uses_uk_language_and_region():
    class MockResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return ["firstread.co.uk", []]

    class MockSession:
        params = None

        def get(self, url, **kwargs):
            self.params = kwargs
            return MockResponse()

    session = MockSession()

    assert fetch_suggestions("firstread.co.uk", session, "en-GB") == []
    assert session.params["params"]["hl"] == "en"
    assert session.params["params"]["gl"] == "uk"
    assert session.params["headers"]["User-Agent"].startswith("Firstread.co.uk/")
