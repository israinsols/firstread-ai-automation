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
    assert config.language == "en-GB"
    assert config.keyword_seeds == (
        "firstread.co.uk",
        "how to verify celebrity concert dates and tickets in the UK",
        "how to report scam emails and texts in the UK",
        "android phone security and backup",
        "NHS physical activity guidelines for adults in the UK",
        "when do clocks change in the UK",
        "UK consumer rights for faulty goods and refunds",
        "best before vs use by dates in the UK",
    )
    assert config.niche == "Celebrity, News, Tech, Sports, Lifestyle, Law and Food"
    assert config.contact_email == "hello@firstread.co.uk"
    assert config.gsc_site_url == "sc-domain:firstread.co.uk"
    assert config.database_path.name == "firstread.sqlite3"
