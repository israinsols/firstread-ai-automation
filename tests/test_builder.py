import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import frontmatter

from builder import build_site
from config import SiteConfig


def config_at(root: Path, base_path: str = "") -> SiteConfig:
    return SiteConfig(
        root=root,
        site_name="Firstread.co.uk",
        domain="firstread.co.uk",
        base_path=base_path,
        niche="lifestyle, culture and practical guides",
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


def test_build_contains_only_published_posts_and_valid_seo(tmp_path):
    config = config_at(tmp_path)
    project_root = Path(__file__).resolve().parents[1]
    shutil.copytree(project_root / "templates", config.root / "templates")
    shutil.copytree(project_root / "static", config.root / "static")
    config.posts_dir.mkdir(parents=True)
    config.pages_dir.mkdir(parents=True)
    article = frontmatter.Post(
        "## A useful guide\n\nSome clear, helpful information for readers.\n\n"
        "![remote tracker](https://tracker.example/pixel.png)",
        title="Firstread.co.uk sample guide",
        slug="firstread-co-uk-sample-guide",
        keyword="firstread.co.uk",
        meta_description="A helpful Firstread.co.uk guide.",
        category="Technology",
        tags=["Guides"],
        author="Firstread.co.uk",
        date="2026-11-07",
        status="published",
    )
    (config.posts_dir / "firstread-co-uk-sample-guide.md").write_text(
        frontmatter.dumps(article), encoding="utf-8"
    )
    for number in range(10):
        extra = frontmatter.Post(
            f"## Guide {number}\n\nA short technology guide for the test site.",
            title=f"Technology guide {number}",
            slug=f"technology-guide-{number}",
            meta_description=f"Technology guide number {number}.",
            category="Technology",
            tags=["Guides"],
            author="Firstread.co.uk",
            date=f"2026-10-{number + 1:02d}",
            status="published",
        )
        (config.posts_dir / f"technology-guide-{number}.md").write_text(
            frontmatter.dumps(extra), encoding="utf-8"
        )
    draft = frontmatter.Post(
        "This draft is not public.",
        title="Unpublished secret draft",
        slug="unpublished-secret",
        status="draft",
    )
    (config.posts_dir / "unpublished-secret.md").write_text(
        frontmatter.dumps(draft), encoding="utf-8"
    )

    result = build_site(config)
    public = config.public_dir
    post_html = (public / "firstread-co-uk-sample-guide" / "index.html").read_text(
        encoding="utf-8"
    )
    home_html = (public / "index.html").read_text(encoding="utf-8")
    sitemap = ET.fromstring((public / "sitemap.xml").read_bytes())
    ET.fromstring((public / "rss.xml").read_bytes())
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [
        item.text
        for item in sitemap.findall("sm:url/sm:loc", namespace)
    ]
    canonical = "https://firstread.co.uk/firstread-co-uk-sample-guide/"
    assert canonical in locations
    assert not any("unpublished-secret" in item for item in locations)
    assert f'<link rel="canonical" href="{canonical}">' in post_html
    assert '<img class="cover" src="/images/firstread-co-uk-sample-guide.png"' in post_html
    assert (public / "images" / "firstread-co-uk-sample-guide.png").is_file()
    assert (
        '<meta property="og:image" content="https://firstread.co.uk/images/firstread-co-uk-sample-guide.png">'
        in post_html
    )
    assert "tracker.example" not in post_html
    assert "<title>Firstread.co.uk | News, stories and practical guides</title>" in home_html
    assert "<h1>Firstread.co.uk: news, stories and practical guides</h1>" in home_html
    assert '<img src="/static/logo.svg" alt="" width="40" height="40">' in home_html
    assert (public / "static" / "logo.svg").is_file()
    assert "firstread.co.uk" in (public / "CNAME").read_text(encoding="utf-8")
    assert (public / "category" / "technology" / "page" / "2" / "index.html").is_file()
    assert (public / "tag" / "guides" / "page" / "2" / "index.html").is_file()

    json_ld = re.search(
        r'<script type="application/ld\+json">(.*?)</script>', post_html, re.DOTALL
    )
    assert json_ld
    structured = json.loads(json_ld.group(1))
    assert structured["@type"] == "BlogPosting"
    assert structured["headline"] == "Firstread.co.uk sample guide"
    assert "unpublished-secret" not in home_html
    assert not (public / "unpublished-secret" / "index.html").exists()
    assert "Unpublished secret draft" in result["draft_report"].read_text(encoding="utf-8")
    assert (public / "robots.txt").is_file()
    assert (public / "rss.xml").is_file()


def test_build_cleans_files_from_previous_brand_manifest(tmp_path):
    config = config_at(tmp_path)
    project_root = Path(__file__).resolve().parents[1]
    shutil.copytree(project_root / "templates", config.root / "templates")
    shutil.copytree(project_root / "static", config.root / "static")
    public = config.public_dir
    public.mkdir(parents=True)
    (public / "old-home.html").write_text("stale branding", encoding="utf-8")
    (public / ".bilalbill-generated-files.json").write_text(
        json.dumps(["old-home.html"]), encoding="utf-8"
    )

    build_site(config)

    assert not (public / "old-home.html").exists()
    assert not (public / ".bilalbill-generated-files.json").exists()
    assert (public / ".firstread-generated-files.json").is_file()


def test_real_editorial_article_has_publishable_length_and_four_faqs():
    project_root = Path(__file__).resolve().parents[1]
    article = frontmatter.load(
        project_root / "content" / "posts" / "android-phone-security-backup-guide.md"
    )
    text = article.content
    faq = text.split("## Frequently Asked Questions", 1)[1]
    questions = re.findall(r"^### .+\?\s*$", faq, re.MULTILINE)

    assert article["status"] == "published"
    assert "firstread.co.uk" in article["title"].casefold()
    assert 900 <= len(re.findall(r"\b[\w'-]+\b", text)) <= 1300
    assert len(questions) == 4
    assert len(article["verify_before_publish"]) == 3


def test_new_uk_guides_match_their_keywords_and_link_to_official_sources():
    project_root = Path(__file__).resolve().parents[1]
    guides = (
        ("best-before-vs-use-by-dates-uk.md", "https://www.gov.uk/"),
        ("report-scam-emails-and-texts-uk.md", "https://www.gov.uk/"),
    )
    for filename, official_source in guides:
        article = frontmatter.load(project_root / "content" / "posts" / filename)
        word_count = len(re.findall(r"\b[\w'-]+\b", article.content))

        assert article["status"] == "published"
        assert article["keyword"].casefold() in article["title"].casefold()
        assert 900 <= word_count <= 1300
        assert len(article["meta_description"]) <= 155
        assert official_source in article.content
        assert len(article["verify_before_publish"]) == 3


def test_github_pages_project_path_prefixes_local_links(tmp_path):
    config = config_at(tmp_path, "/firstread-ai-automation")
    shutil.copytree(Path(__file__).resolve().parents[1] / "templates", config.root / "templates")
    shutil.copytree(Path(__file__).resolve().parents[1] / "static", config.root / "static")
    config.posts_dir.mkdir(parents=True)
    config.pages_dir.mkdir(parents=True)
    article = frontmatter.Post(
        "A guide for this test.",
        title="Pages image test",
        slug="pages-image-test",
        meta_description="A test cover image.",
        category="Technology",
        tags=[],
        author="Firstread.co.uk",
        date="2026-11-07",
        status="published",
    )
    (config.posts_dir / "pages-image-test.md").write_text(
        frontmatter.dumps(article), encoding="utf-8"
    )

    build_site(config)
    home_html = (config.public_dir / "index.html").read_text(encoding="utf-8")
    post_html = (
        config.public_dir / "pages-image-test" / "index.html"
    ).read_text(encoding="utf-8")

    assert 'href="/firstread-ai-automation/about/"' in home_html
    assert 'href="/firstread-ai-automation/static/site.css"' in home_html
    assert 'src="/firstread-ai-automation/images/pages-image-test.png"' in post_html
    assert (config.public_dir / "images" / "pages-image-test.png").is_file()
    assert not (config.public_dir / "CNAME").exists()
