from config import SiteConfig
from db import connect, initialize, next_keyword, save_keyword
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


def test_question_and_uk_terms_get_a_higher_score():
    plain = score_keyword("useful technology guide")
    specific = score_keyword("how to choose technology price UK")
    assert specific > plain
    assert score_keyword("a fluke") == score_keyword("a sample")


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
        niche="Celebrity, News, Tech, Sports, Lifestyle, Law and Food",
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
    assert next_keyword(config.database_path) is None


def test_researched_topic_seed_can_be_used_for_article_generation(tmp_path, monkeypatch):
    class MockResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return ["query", []]

    class MockSession:
        def get(self, *args, **kwargs):
            return MockResponse()

    config = SiteConfig(
        root=tmp_path,
        site_name="Firstread.co.uk",
        domain="firstread.co.uk",
        base_path="",
        niche="Celebrity, News, Tech, Sports, Lifestyle, Law and Food",
        posts_per_day=1,
        language="en-GB",
        author="Firstread Editorial",
        auto_publish=False,
        social_telegram=False,
        social_facebook=False,
        social_pinterest=False,
        keyword_seeds=("firstread.co.uk", "food date labels UK"),
        contact_email="hello@firstread.co.uk",
        gsc_site_url="sc-domain:firstread.co.uk",
    )
    monkeypatch.setattr("keywords.query_variants", lambda seed: [seed])

    research_keywords(config, session=MockSession(), delay_seconds=0)

    keyword = next_keyword(config.database_path)
    assert keyword["keyword"] == "food date labels UK"
    assert keyword["source"] == "topic-seed"


def test_domain_seed_is_not_selected_as_an_article_topic(tmp_path):
    database = tmp_path / "keywords.sqlite3"
    initialize(database)
    save_keyword(database, "firstread.co.uk", "firstread.co.uk", "google-autosuggest", 50)
    save_keyword(database, "firstread.co.uk", "firstread.co.uk", "site-seed", 100, 100)
    save_keyword(database, "UK food date labels", "uk food date labels", "google-autosuggest", 40)

    keyword = next_keyword(database)

    assert keyword["keyword"] == "UK food date labels"


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
