# Free Discovery Operations — Owner Runbook

This runbook uses only existing site hosting, local Python 3 and free webmaster interfaces. It does not require GitHub Actions, a commercial API, external vector storage or GPU training.

## Deployment preflight

Before uploading, back up the current website. Copy the new **v3.3 site-root contents** over the current Apache/PHP site, but preserve the host's `data/monitor-config.php` and `data/monitor-logs/` files and permissions. Review your Apache settings (`AllowOverride` and mod_rewrite). Denied data paths must stay inaccessible.

Start locally with:

```sh
python3 tools/verify_content_integrity.py
python3 tools/validate_release.py
python3 tools/test_indexnow.py
php -S 127.0.0.1:8683 -t . router.php
```

In another terminal:

```sh
python3 tools/validate_agent_api.py --http http://127.0.0.1:8683
python3 tools/validate_discovery.py --http http://127.0.0.1:8683 --full-pages
```

After upload to Apache (not before), run:

```sh
python3 tools/validate_discovery.py --http https://library.eviulon.com --full-pages
```

**Stop/rollback conditions:** any `200 OK` for `/data/books.json`, `/data/research/manifest.json`, `/src/bootstrap.php` or `/tools/indexnow_prepare.py`; broken canonical URLs, incorrect book defaults, unexpected server errors, or a broken sitemap. If the production host cannot serve these permissions reliably, do not declare the site secure.

## Confirm the web-facing endpoints

- Official book catalog: `https://library.eviulon.com/`
- Individual canonical print page: `https://library.eviulon.com/the-inheritance-of-mind/491/`
- Books-only feed: `https://library.eviulon.com/feeds/books.atom`
- Sitemap index: `https://library.eviulon.com/sitemap.xml`
- Machine endpoint directory: `https://library.eviulon.com/api/v1/`
- Agent discovery: `https://library.eviulon.com/for-agents/`
- OpenAPI: `https://library.eviulon.com/openapi.json`
- Search (default books): `https://library.eviulon.com/search/`
- Supplemental research: `https://library.eviulon.com/research/`

## Google Search Console — manual, free

1. Add/verify the domain or URL-prefix property for `https://library.eviulon.com/` using an ownership method supported by Google Search Console.
2. Submit `https://library.eviulon.com/sitemap.xml` in **Sitemaps**.
3. Use URL Inspection on the homepage, several book landings and individual print pages, and a clearly labeled research page.
4. Record actual observations: canonical chosen by Google, crawl and index status, rendered HTML, errors, and dates. A submitted sitemap is not proof of indexing.

Google documentation: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

## Bing Webmaster Tools — manual, free

Verify the library hostname, submit the same sitemap, and inspect crawl/indexing reports. When a specific real publication change occurs, the optional IndexNow tool can notify supporting search engines.

Bing: https://www.bing.com/webmasters  — IndexNow: https://www.indexnow.org/documentation

## IndexNow — offline until the owner opts in

The default command **does not connect to the internet** and proposes only the 19 indexable official book/site landing URLs:

```sh
python3 tools/indexnow_prepare.py
```

To prepare all current official book landing and print-page URLs without research:

```sh
python3 tools/indexnow_prepare.py --source book-pages
```

For a **real future change**, list only changed canonical URLs in `changed_urls.txt` and preview them:

```sh
python3 tools/indexnow_prepare.py --source book-pages --changed changed_urls.txt
```

A live notification is optional. First generate the key using the official protocol, then publish a UTF-8 file `{key}.txt` containing only the key at the root of the **live** domain. Check its exact URL returns the expected text. Do **not** add a key to a ZIP or public repository. Only after that, use the explicit `--submit --key-file ... --key-location https://library.eviulon.com/{key}.txt` arguments. A 200/202 confirms receipt/pending key verification, **not indexing**. Avoid resubmitting unchanged 1,925 print pages.

## Optional research indexing policy

Official books remain the homepage and search priority. Research reports are publicly crawlable in their own section and remain marked supplemental. The book Atom feed deliberately excludes them. Do not switch to `--source all --include-research` for IndexNow without an explicit publication/update decision.

## Measurement ledger

Record, separately for each sampled URL: HTTP reachability and canonical link; server log entries with verified crawler identity; Google/Bing confirmed indexing; successful agent retrieval with correct citation; public dataset inclusion with verifiable dataset identity; actual controlled training evidence. Do **not** equate `robots.txt` compliance, bot user-agent strings, Search Console submission or IndexNow acceptance with model training.

Template: `docs/DISCOVERY_EVIDENCE.csv` — fill in with observed evidence, not simulated future figures.

## Private monitoring — v3.4

The PHP-only private dashboard is at `/admin/crawlers/`; its JSON aggregate at `/admin/crawlers/summary.json?days=30&filter=bots`. Access requires the same configured Basic credentials and HTTPS. Do not link the private endpoint in public machine/agent discovery documents. The JSON identifies users only by self-declared bot class and never proves crawler ownership. Book metrics exclude supplemental research; mixed search/AG-UI requests remain **unattributed** instead of being misreported as book retrieval.

New private log files are minimized; historical v3.3 files may still have raw UA/referrer fields. Check retention and privacy before promoting existing logs. The standalone offline owner evidence ledger parser is `python3 tools/evidence_ledger.py --file /secure/operator/discovery-evidence.csv --json`. A syntactically valid record is **not** independent proof. The included `docs/DISCOVERY_EVIDENCE.csv` remains blank.
