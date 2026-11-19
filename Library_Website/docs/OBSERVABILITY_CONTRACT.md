# Private Observability Contract — v3.4

## System boundaries and threat assumptions

**System of record:** official Eviulon book text at permanent print-page URLs. Research remains **supplemental, non-doctrinal** and must never inflate the claim of officially approved books. The monitor is independent of the public search and AG-UI interface; it does not change results.

**v3.13 update:** monitoring is disabled by default to reduce response work for crawlers. To opt in, set the PHP environment variable `EVIULON_MONITOR_ENABLED=1` on the host; no new records are captured otherwise. Static JSON and discovery files bypass PHP monitoring entirely. The following legacy contract applies only while explicitly enabled. The monitor records a minimal server-side log event at the end of an HTTP request when enabled. User-agent labels are merely **claims**. A visitor may spoof any label. Without host network metadata and vendor verification, *no record is treated as an authenticated crawler.* A successful page response is not evidence of indexing, training data adoption, correct citation, or model learning.

## Endpoint

`GET /admin/crawlers/summary.json?days=7&filter=bots` (same admin credentials as the HTML dashboard):

- `days`: 7, 30, or 90; fallback 7.
- `filter`: `bots`, `others`, or `all`; fallback `bots`.
- `GET` / `HEAD` only; unsupported methods return HTTP `405` with `Allow: GET, HEAD`.
- Authentication missing/incorrect: `401` with Basic challenge; unconfigured: `503`. Both fail closed.
- Always `Cache-Control: no-store, private`, `X-Robots-Tag: noindex, nofollow, noarchive`, and `X-Content-Type-Options: nosniff`.
- **Not publicly documented in OpenAPI**. Browser and API access require HTTPS in production.

### JSON schema and metric semantics

The summary uses `schema_version: 1.0`, `evidence_scope: observed_http_requests_only`, `crawler_identity: self_reported_user_agent_unverified`, `window_days`, `visitor_filter`, `completeness`, `metrics`, `by_source`, `by_claimed_agent`, `by_request_kind`, `by_day_utc`, and `official_books`.

- `metrics.requests`: all PHP requests matching the visitor filter; not raw host logs or static Apache-served asset traffic.
- `metrics.success_2xx`: HTTP 200–299; `redirect_3xx`: 300–399; `not_modified_304`: subset of redirects; `errors_4xx` and `errors_5xx`: unsuccessful requests.
- `metrics.successful_book_pages`: number of HTTP 200 page/spread/API-page responses; repeated requests each count.
- `metrics.distinct_book_pages`: unique canonical official pages represented by HTTP 200 responses within the selected date/visitor window (at most 1,925). A two-page spread may represent two pages.
- `metrics.successful_research_sections`: HTTP 200 research part responses; **not official** content.
- `by_source.books`: public requests confidently associated with the official book routes and catalog feed.
- `by_source.research`: direct report and research API paths (supplemental).
- `by_source.unattributed-search-or-agent`: HTML search, JSON search and AG-UI. **Do not infer which source was read from endpoint access alone.**
- `by_source.site-or-service`: other website and discovery routes.
- `official_books`: exactly 14 records with source-page counts, request counts and unique served-page counts.
- `completeness.partial`: true when a log scan exceeds its bounded size/line limit; observed totals must not be interpreted as exhaustive.

### New JSONL event schema v2

New private files `data/monitor-logs/hits-YYYY-MM-DD.jsonl` contain only:

`schema_version`, UTC `time`, HTTP `method`, safe canonical `path`, `status`, `kind`, `source`, claimed `agent` category and `claimed_crawler` boolean, elapsed `ms`, and optionally parsed `book/from/to` for page coverage.

**Not stored:** IP address, raw user-agent, referrer, authorization, cookie, search query, POST body, or AI prompt. Unknown/unrecognized URL paths are replaced with `/[other]`. On-server files from v3.3 can still contain legacy `user_agent`/`referrer_host` fields; v3.4 parses them for compatibility but never exposes them through its aggregate endpoint. Existing monitoring data must not be uploaded to public GitHub.

### Limits and failure modes

- File append uses `LOCK_EX`. Logs rotate by UTC day, with opportunistic pruning after 90 days.
- The parser streams files and caps at 120,000 lines per day; partial scans are flagged.
- If the webserver cannot write monitoring logs, user-facing reading still works and the admin dashboard warns that data may be incomplete.
- Serving Apache static assets that bypass PHP will not appear in this monitor; use private hosting access logs for complete request analysis.
- Provider IP/DNS verification is a separate offline/operator task; this implementation cannot verify crawler ownership without retaining or processing origin IP metadata.
- If `.htaccess` is ignored, private logging and source JSON may be exposed. Production HTTP negative tests are mandatory.

## Evidence ladder and review

Use `docs/DISCOVERY_EVIDENCE.csv` only as a **blank schema template**. Actual observations belong in a private owner-controlled CSV and may be inspected offline with `tools/evidence_ledger.py`. Allowed labels are `reachable`, `crawled_verified`, `indexed`, `agent_retrieved`, `dataset_included`, and `model_trained`. The validator enforces headers, canonical domain, UTC timestamps and nonempty provenance fields but cannot substantiate a source or guarantee that a level has genuinely been reached. Human review is required. Never backfill hypothetical activity as actual evidence.
