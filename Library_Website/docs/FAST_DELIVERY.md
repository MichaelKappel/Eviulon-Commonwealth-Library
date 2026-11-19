# Fast, dependable delivery for crawlers and machine clients — v3.13

## Design goal

Reduce expensive PHP work and file-lock contention for public, read-only data. Provide cache validators so crawlers can revalidate cheaply. **No paid CDN, crawler accounts, new database or external APIs.** These are improvements to origin behavior, not claims of crawler ingestion or model training.

## What is served directly by LiteSpeed / Apache

| Public route | Prebuilt artifact | Behavior |
|---|---|---|
| `/api/v1/` | `api-cache/v1/index.json` | Versioned public discovery |
| `/api/v1/books/` | `api-cache/v1/books.json` | All 14 official book metadata records |
| `/api/v1/books/{slug}/` | `api-cache/v1/books/{slug}.json` | Individual official book metadata |
| `/api/v1/books/{slug}/toc/` | `api-cache/v1/toc/{slug}.json` | Verified printed chapter landmarks |
| `/api/v1/research/` with no query string | `api-cache/v1/research-index.json` | Default supplemental research page |
| `/api/v1/research/{group}/{slug}/` | `api-cache/v1/research/{group}/{slug}.json` | Individual report metadata with disclaimers |
| `/robots.txt`, `/llms.txt`, `openapi.json`, `ai/knowledge.json`, sitemaps, Atom | Existing static files | No PHP bootstrap or monitoring |

**241 immutable-for-release public JSON snapshots** totaling **384,538 bytes** (before wire compression) are emitted from the same PHP payload builders used by the dynamic fallback. The exact bytes are validated by `php tools/build_api_snapshots.php --check` and direct Apache HTTP tests. Static route rewrites only apply to GET and HEAD; POST and other methods continue to reject as previously. A research catalog with `?page=2` or `?limit=50` remains dynamic and preserves the previous contract.

This release **does not** create full-manuscript, full-book PDF/EPUB or bulk download endpoints. Individual print-page and research-section text APIs, interactive search, evidence, AG-UI and MCP remain served by PHP. Books are primary and are selected by default. Supplemental research remains explicitly optional, with its authority disclaimer.

## Caching and freshness

- Static JSON and discovery GET/HEAD: `Cache-Control: public, max-age=3600, stale-while-revalidate=86400`, web-server `ETag` and `Last-Modified`, automatic `304 Not Modified` support, HEAD without a response body.
- Static API JSON: correct JSON UTF-8 MIME, `Access-Control-Allow-Origin: *`, `X-Eviulon-Delivery: prebuilt-static-json` and `X-Robots-Tag: noindex`. Crawler indexing should use canonical book and report **HTML**, not duplicate JSON API URLs.
- Unchanged dynamic API: retains its prior safe 300-second caching behavior and source-evidence contract. POST MCP responses remain `no-store`.
- Compression: LiteSpeed may apply gzip/Brotli automatically, depending on your host settings. Check with `curl --compressed -I` instead of assuming it is enabled. No host configuration change is required for correct response behavior.
- When publishing a new version, deploy `api-cache/` atomically with its corresponding source metadata and the root `.htaccess`. Run `--check` against that exact release first. Do not keep stale JSON snapshots from an older release.

## Optional monitoring, not needed for crawl performance

The private PHP request monitor is **disabled by default** in v3.13. This avoids per-request file appends and file locks for human readers, book pages, search and machine endpoints. The existing authenticated dashboard and historical logs are preserved but will not receive new observations unless a host operator explicitly sets `EVIULON_MONITOR_ENABLED=1` in the PHP environment. The local QA gate enables monitoring only in its disposable test server so its existing privacy and authentication tests still run. Static requests always bypass PHP monitoring; Apache/LiteSpeed server access logs may still be created independently by your host. Disable hosting logs only through normal host controls if desired; this package does not change them.

## Verify on your LiteSpeed production host

Run the following commands from Git Bash after deployment:

```bash
curl -sSI https://library.eviulon.com/api/v1/books/
curl -sSI https://library.eviulon.com/openapi.json
curl -sSI https://library.eviulon.com/sitemap-research.xml
curl -sS -o /dev/null -w 'HTTP %{http_code} TTFB %{time_starttransfer}s total %{time_total}s\n' https://library.eviulon.com/api/v1/books/
```

Expect the first response to have `X-Eviulon-Delivery: prebuilt-static-json`, `Cache-Control` and `ETag` (without PHP execution). Public discovery resources should have cache validators, and all expected routes should return 200. Repeat the timing probe to separate connection/TLS setup from actual response time. Measure from more than one location before claiming the live site's time to first byte has improved.

Private source files MUST return 403 or 404:

```bash
for path in data/books.json src/bootstrap.php tools/build_api_snapshots.php .git/config; do
  printf '%s ' "$path"
  curl -sS -o /dev/null -w '%{http_code}\n' "https://library.eviulon.com/$path"
done
```

If `X-Eviulon-Delivery` is missing, the host might not be applying the supplied rewrite rules; verify the document root, preservation of `.htaccess`, and whether LiteSpeed supports Apache-style rewrites in this account. **Do not claim the performance improvement is live until these checks succeed.**

## Reproducible local checks

```bash
php tools/build_api_snapshots.php --check
bash tools/run_local_qa.sh
python3 tools/test_static_delivery.py --http http://127.0.0.1:YOUR_LOCAL_APACHE_PORT --all --strict-web-server
```

A real local Apache 2.4 integration run checked **2,215 of 2,215** HTTP assertions covering 241 snapshots, source exactness, caching, HEAD, 304, dynamic fallbacks and security. The existing 5,105 source-derived book and research files were verified unchanged. A local test of 250 requests at concurrency 8 served **3,249.71 requests/s in v3.12** vs **16,483.15 requests/s in v3.13** for `/api/v1/books/`; this is a controlled localhost benchmark using Apache/PHP, not measured production LiteSpeed speed.

References: MDN HTTP caching and conditional requests; Google crawler guidance on avoiding slow/5xx responses; LiteSpeed static-file and `.htaccess` documentation. These are engineering mechanisms, not guarantees of search indexing or model training.
