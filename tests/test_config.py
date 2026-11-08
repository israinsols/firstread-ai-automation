from config import load_config


def test_defaults_target_firstread_domain_and_exact_keyword_seed(tmp_path, monkeypatch):
    for name in (
        "SITE_NAME",
        "SITE_DOMAIN",
        "SITE_NICHE",
        "SITE_LANGUAGE",
        "SITE_AUTHOR",
        "SITE_BASE_PATH",
        "KEYWORD_SEEDS",
        "CONTACT_EMAIL",
        "GSC_SITE_URL",
        "POSTS_PER_DAY",
    ):
        monkeypatch.delenv(name, raising=False)

    config = load_config(tmp_path)

    assert config.site_name == "Firstread.co.uk"
    assert config.domain == "firstread.co.uk"
    assert config.base_url == "https://firstread.co.uk"
    assert config.niche == "news and practical guides"
    assert config.language == "en-GB"
    assert config.keyword_seeds == ("firstread.co.uk",)
    assert config.contact_email == "hello@firstread.co.uk"
    assert config.gsc_site_url == "sc-domain:firstread.co.uk"
    assert config.database_path.name == "firstread.sqlite3"
