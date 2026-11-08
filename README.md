# Firstread.co.uk

A Python static-site project branded for `firstread.co.uk`, with Celebrity, News, Tech, Sports, Lifestyle, Law and Food sections. It writes HTML, images, RSS, robots.txt, and a sitemap to `public/`; content drafts are **not published by default**.

Keyword research uses `firstread.co.uk` as its exact, highest-priority seed and requests UK-localized suggestions. Organic clicks and rankings cannot be guaranteed; the project does not simulate clicks, create fake visitors, or manipulate search results.

## What is included

- Python 3.11+, Jinja2, Markdown-it (raw HTML disabled), frontmatter, SQLite, Requests, Pillow, python-dotenv, Google Auth, and pytest.
- Google Autosuggest research with one-second request spacing, deduplication, and keyword scoring.
- Gemini article drafts with three attempts and checks for length, keyword, FAQ, headings, placeholders, repeated paragraphs, and similarity. Every draft carries three fact-check notes.
- Original, locally generated topic-themed editorial artwork for article covers and lightweight WebP story cards.
- A static, responsive, accessible site with clean URLs, categories/tags, pagination, internal links, table of contents, reading time, related posts, JSON-LD, canonical/Open Graph tags, XML sitemap, robots.txt, and RSS.
- Sitemap, robots.txt, canonical URLs, and structured metadata for `https://firstread.co.uk`; optional IndexNow, Search Console, and Telegram/Facebook/Pinterest integrations.
- `AUTO_PUBLISH=False` by default. Review every claim, source, link, and generated image before publication.

## 1. Set up Python and the project

This is a standalone repository. Open a terminal in its root folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and verify the site name, UK English language, contact mailbox, and publication details. The exact domain `firstread.co.uk` stays in the keyword database as a branded seed; article generation skips that navigational seed and uses related UK topic seeds instead. Put credentials only in `.env` locally and your host's secret manager in production. Never commit `.env`, API keys, or the Search Console private key.

For Gemini, create an API key in Google AI Studio and set `GEMINI_API_KEY`. The default model is `gemini-3.8-flash`; override it locally with `GEMINI_MODEL`. Gemini free-tier access, model availability, and quotas can change; a failed generation leaves existing published content unchanged.

## 2. Research, generate, and review

```powershell
python main.py --research
python main.py --generate
python main.py --build
python main.py --all --dry-run
```

Research uses the public Autosuggest endpoint with a one-second pause between requests. Each seed expands into alphabet and question variants, so one research run may take several minutes. The keyword database is `data/firstread.sqlite3`. Research stores the exact domain seed before querying Google's UK-localized Autosuggest service.

`--generate` writes a Markdown article to `content/posts/` with `status: draft`, unless you explicitly change `AUTO_PUBLISH`. Generation requires available keywords and `GEMINI_API_KEY`. Verify each `verify_before_publish` note against reliable, current sources; edit the article and metadata yourself. Generated copy, factual accuracy, originality, and SEO results are not guaranteed.

Publish one reviewed draft by its filename slug:

```powershell
python main.py publish your-article-slug
```

For bulk publishing, first edit each reviewed draft's frontmatter to include `reviewed: true`, then run:

```powershell
python main.py publish --all-reviewed
python main.py --build
```

The explicit `publish <slug>` command is itself the editor's approval. `publish --all-reviewed` only selects drafts you have marked `reviewed: true`. `--build` includes **only** `status: published` articles. Unpublished titles are listed in `build/drafts-report.html`, which is not copied into the deployable site.

`--dry-run` prints intended actions without making network calls or changing files or the database. `--all` runs research, generation, and build; deployment, social sharing, indexing, and reporting are separate opt-in flags.

## 3. Preview the static site

```powershell
python main.py --build
python -m http.server 8000 --directory public
```

Open `http://127.0.0.1:8000`. The source templates and styling are in `templates/` and `static/`. Static pages live in `content/pages/`. Review the About, Contact, Privacy, and Disclaimer pages and replace the example contact email if needed.

## 4. Deployment and production safety

The GitHub Pages workflow builds and deploys a preview at `https://israinsols.github.io/firstread-ai-automation/` when site files change, and after each successful daily article workflow. GitHub Pages must be enabled for this repository with **Settings → Pages → Build and deployment → Source: GitHub Actions**. The domain `firstread.co.uk` already serves a separate site; the preview workflow does not change DNS, hosting, or that live site.

The build defaults to `SITE_DOMAIN=firstread.co.uk`, `SITE_NAME=Firstread.co.uk`, and `SITE_BASE_PATH=`. Before connecting any host, confirm you control the domain and that its current site can safely be replaced. The example contact address `hello@firstread.co.uk` must be configured and verified before publishing.

If you add an automation workflow, configure `GEMINI_API_KEY` in your host's secret manager. Add `INDEXNOW_KEY` and `GSC_SERVICE_ACCOUNT_JSON` only if you enable those integrations. Keep local `.env` files and the SQLite database out of Git; the database stores local keyword and automation state.

Google AI Studio quotas and API policies can change. This project does not purchase a plan or create simulated search traffic.

The GitHub Pages preview workflow sets `SITE_DOMAIN=israinsols.github.io` and `SITE_BASE_PATH=/firstread-ai-automation` so preview canonicals and asset links use the project-site URL. For a future custom-domain build, use `SITE_DOMAIN=firstread.co.uk` and `SITE_BASE_PATH=`; the build then emits a `CNAME` file. Only attach `firstread.co.uk` to Pages after planning and explicitly approving a production migration.

### Railway preview

The `Dockerfile` builds the published static pages and serves them with Nginx. `.dockerignore` excludes local environment files so `.env` secrets are not uploaded. From this directory, create a separate Railway project and deploy:

```powershell
railway init --name firstread-site
railway up
railway domain
```

Open the generated Railway URL to check the site. Do not point `firstread.co.uk` at Railway unless you intend to move the existing live site and have verified the migration plan. Keep `SITE_DOMAIN=firstread.co.uk` for canonical and sitemap URLs; do not set a GitHub Pages base path for Railway.

This repository does not include a Railway deployment workflow. A manual Railway upload does not automatically receive later content changes; run `railway up` again after rebuilding, or connect this repository to Railway and deploy from its root directory.

### Cloudflare Pages preview

To deploy on Cloudflare Pages, connect the repository under **Cloudflare → Workers & Pages → Create → Pages → Connect to Git**, and set:

- Build command: `python -m pip install -r requirements.txt && python main.py --build`
- Build output directory: `public`
- Environment variable: `SITE_DOMAIN=firstread.co.uk` (plus any site name/niche settings you changed)
- Optional environment variable: `INDEXNOW_KEY` if you want the public key file included in the Cloudflare build.

Cloudflare's Git integration rebuilds the published static output from each commit. Add your configured domain under the Pages project's **Custom domains** and follow Cloudflare's DNS prompts. Run `python main.py --index` and `python main.py --share` locally after deployment if those features are enabled. Cloudflare's free-plan limits and included capabilities can change; no paid integration is required by this code.

## 5. Search Console and IndexNow

1. Add `firstread.co.uk` as a **Domain property** in Google Search Console and verify it by adding Google's TXT record at your DNS provider, if it is not already verified.
2. After deployment, open `https://firstread.co.uk/sitemap.xml` and submit that URL under **Sitemaps** in Search Console. Check the URL Inspection tool for the homepage and first published post.
3. For automatic sitemap submission and reports, create a Google Cloud service account, enable the Search Console API, and grant the account access to the verified Search Console property. Store the complete service-account JSON in the `GSC_SERVICE_ACCOUNT_JSON` secret (or local `.env`) and set `GSC_SITE_URL=sc-domain:firstread.co.uk`.
4. Optionally create a random IndexNow key (for example, `python -c "import secrets; print(secrets.token_hex(16))"`), save it as `INDEXNOW_KEY` in GitHub secrets and `.env`, and run a deploy. The site publishes `<key>.txt` and after deployment submits its sitemap URLs to IndexNow. IndexNow is a notification, not a promise of indexing or ranking.
5. To run Search Console reporting weekly, set `ENABLE_GSC_REPORT=true` as a repository variable and configure `GSC_SERVICE_ACCOUNT_JSON`. The report creates `reports/search-console-weekly.csv` and prioritizes queries averaging positions 8-20 in the keyword database. The report is local/CI output and is not committed.

Google's old unauthenticated sitemap-ping URL is deprecated; this project uses the Search Console API when configured and otherwise tells you to submit the sitemap in Search Console.

## 6. Optional social distribution

Sharing is disabled by default, uses official APIs, and only shares published articles once per platform. Configure credentials in your local `.env` or the deployment host's secret manager, then set the matching `SOCIAL_*` setting to `true`. Caption generation uses the Gemini key.

- **Telegram:** create a bot with BotFather, add it as an administrator to your channel, then set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID`.
- **Facebook Page:** create a Meta app with the Page publishing permission, obtain a valid Page access token, and set `FACEBOOK_PAGE_ID` and `FACEBOOK_PAGE_ACCESS_TOKEN`. Review Meta's current permission/app-review rules and token expiry.
- **Pinterest:** create an app with permission to publish Pins, then set `PINTEREST_ACCESS_TOKEN` and the destination `PINTEREST_BOARD_ID`.

Never put personal account passwords or API tokens in source files. Disable any platform flag until its credential and permission setup is complete. Sharing is not paid promotion and does not guarantee referral visits.

## 7. Local scheduling and maintenance

The GitHub Actions workflow at `.github/workflows/daily.yml` runs every day at **2:00 pm Pakistan time** (09:00 UTC), and can also be started manually from the repository's **Actions** tab. It researches UK keyword suggestions, generates one article with Gemini, marks it published, builds the site, and commits the article Markdown to `content/posts/`. The workflow caches the keyword database between runs so it can avoid reusing researched topics.

Before the first run, add a repository Actions secret named `GEMINI_API_KEY` under **Settings → Secrets and variables → Actions**. The workflow needs repository **Contents: read and write** permission to commit its generated article. Check the Actions run log after setup; missing credentials, API quota limits, or generation/build errors will fail the run rather than publish an empty article.

This workflow commits published content to GitHub; **it does not configure hosting or deploy to `firstread.co.uk`**. The domain currently serves a separate WordPress site. A host connected to this repository may deploy on the generated commit if its Git integration is configured, but do not change DNS or replace the live site without an approved migration plan. Automatic AI-published articles are not human-reviewed; verify facts and sources regularly.

Useful commands:

```powershell
python main.py --research
python main.py --generate
python main.py --build
python main.py --share
python main.py --report
python main.py --index
pytest -q
```

The daily workflow is for article generation and publishing to this repository, not production deployment. Only use `--deploy` after adding and verifying a separate deployment workflow for the intended host.

## Day 1 launch checklist

- [ ] Confirm the homepage title and logo show **Firstread.co.uk** and verify all publication details.
- [ ] Review the About, Contact, Privacy, and Disclaimer pages and contact email.
- [ ] Review the existing live site and approve a migration plan before changing hosting or DNS.
- [ ] Verify the domain property in Search Console.
- [ ] Deploy to the intended host and submit `https://firstread.co.uk/sitemap.xml`.
- [ ] Add an IndexNow key, deploy, and confirm `https://firstread.co.uk/<key>.txt` is reachable.
- [ ] Research keywords and create five draft posts across separate `--generate` runs.
- [ ] Verify facts, sources, originality, links, titles, and descriptions; publish the first five posts only after human review.
- [ ] Check the homepage, mobile layout, canonical URLs, RSS, robots.txt, and Search Console coverage after deployment.

## Test and example output

From this directory, run `pytest -q`. A dry-run example:

```text
DRY RUN — no network calls or files/database changes.
- Would research 1 seed(s) with polite Autosuggest requests.
- Would generate up to 1 Gemini draft(s) (AUTO_PUBLISH=False).
- Would build static pages from published content only.
- Published markdown files available: 0.
```

Example build output:

```text
public/
  index.html
  404.html
  about/index.html
  contact/index.html
  privacy/index.html
  disclaimer/index.html
  robots.txt
  sitemap.xml
  rss.xml
  CNAME
  static/site.css
  static/logo.svg
  static/favicon.svg
  static/og-default.png
  images/<published-slug>.png
  images/<published-slug>-thumb.webp
  <published-slug>/index.html
  category/<category>/index.html
  tag/<tag>/index.html
build/drafts-report.html  # local only; never deployed
```
