# v3.14.4-STATIC-DELIVERY — static file continuity and web-server performance contract

- Retains and revalidates all 241 prebuilt API JSON catalog/toc/report metadata snapshots introduced in v3.13.
- Adds reproducible `ai/static-delivery.json` inventory of 280 public static files, each with SHA-256 hash and byte size. Includes 17 sitemaps, five discovery files and 17 assets; no book-page or report-section text export.
- Adds explicit fast-revalidation cache headers for existing public CSS, JS and cover assets; keeps web-server ETag and conditional `304` responses.
- QA now rejects missing/stale static files and exercises all 241 snapshot routes; a separate real Apache/LiteSpeed integration audit checks static delivery bypasses PHP.
- Preserves dynamic HTML, citation/evidence APIs, research section source text, search, AG-UI, and MCP unchanged except release/version identification.
- Full source and Runic memories remain private. This is recovery-line v3.14.4, **not** lost v3.18 and **not** a live deployment.

**Private source provenance update, v3.14.3:** three of the eight newly preserved research originals match previously absent report-source hashes; now **46/210 exact** source file matches, **164 unmatched** (the v3.14.2 history below reports the earlier 43/210 and 167 gap). No report section text was changed.

# v3.14.3 full release — AI learning/seeding research memory continuity

**Release ID:** `v2026.11.19.3.14.3-LEARNING-SEEDING-MEMORY`. **Website runtime remains source-identical to locally tested v3.14.2 metadata correction**, except package ID/version manifest and public-safe handoff metadata. The private master adds all eight owner research originals into private `PRIVATE_SOURCE/docs/ai-learning-and-seeding/originals/`, a private research hub and evidence gates, and deep-linked Runic project memory including `.uai/totem.uai`. This does **not** claim a restored v3.18, a live deployment, a new public dataset, external DOI registration, verified model ingestion, or external training. **Never upload the PRIVATE_MASTER to the public website or GitHub.**

The last v3.14.2 release QA passed 15/15 local stages and 97,937 complete semantic metadata assertions across 3,708 canonical pages. The complete v3.14.3 regression suite has been rerun and PASSED: 15/15 stages, 97,937 semantic HTML checks across 3,708 canonical URLs; 5,105 original files unchanged. Release packaging separately validates Runic memory and research source integrity. All 5,105 original site content records must remain unchanged. For the *private* primary owner goal consult `PRIVATE_SOURCE/docs/ai-learning-and-seeding/INDEX.md` inside the PRIVATE_MASTER only; this link is not available on the deployed site.

---

# v3.14.2 metadata correction — source-verifiable completed local QA

**Release:** `v2026.11.19.3.14.2-METADATA` (the recovered v3.14.1 implementation plus verified metadata fixes; NOT lost v3.18). **Local status: 15/15 full isolated QA gates passed; 97,937 structural HTML/JSON-LD assertions passed on all 3,708 canonical pages plus two Research filters; original 5,105 files unchanged.** This release is NOT deployed to production LiteSpeed; external search/rich-results indexing is not verified.

The private master is the canonical backup; the site-root ZIP is deployable; the GitHub ZIP is a public-safe source-only representation. All three must carry exactly matching release manifests and hashes; do not upload either the private master or deploy root to public GitHub.

---

# v3.14.2-METADATA — Corrected Schema.org/JSON-LD, Dublin Core and Open Graph

**Status:** staging, not deployed. Source baseline v3.14.1 recovered complete website; this is a metadata-only corrective release and does **not** claim to recreate the unavailable v3.15–v3.18 source features.

- **3,708 canonical HTML pages:** 14 official Books, 1,925 original print-page routes, 210 supplemental Report landings, 1,553 research-section routes, the Research directory, and 5 additional site routes. No changes to original canonical page/section URLs or source material.
- **Book print pages:** removed `Schema.org pagination` from the `WebPage` entity (defined on Chapter and Article), and added a separate `CreativeWork` `#print-page` entity with verified book membership, source-backed page ID and `WebPage.mainEntity`.
- **219 source-verified chapter headings:** `Book.hasPart` now emits unique stable Chapter `@id` values equal to their existing original book-page anchors. No inferred chapter endings, fabricated standalone chapters or invented author dates.
- **Research:** added the previously unlisted `/research/` directory to the sitemap and a 210-entry `CollectionPage` for the unfiltered directory only. Filtered collection queries remain noindex with no invisible comprehensive ItemList.
- **Report/section linked data:** `Report` source identity, actual report ID, section `hasPart`, persistent `#research`/`#section` graph references, explicit `creativeWorkStatus=supplemental_research_unverified`, and `WebPage.mainEntity`. No author, DOI, scholarly/peer-review or rights grant invented.
- **Dublin Core:** `DC.title`, `DC.language=en`, `DC.type=Text`, `DC.identifier` for the actual canonical URL. These do not claim indexed scholarly publication or dataset licensing.
- **Open Graph:** official book landing `og:type=book`, report landing `og:type=article`, everything else `website`. Single exact `og:url` equal to HTML canonical.
- **Automated validation:** every canonical page checked for title, description, language, robots, canonical, Dublin Core, Open Graph, valid JSON-LD, stable entity IDs and source-grounded parent links. Two filtered research URLs checked separately. Valid markup does not guarantee external crawlers will index content.
- **Sources and rights:** original 5,105 source-derived files unchanged, original fourteen PDF book hashes unchanged, and 259 protected Runic memory files preserved. Original source `.md` hashes still cannot be matched for 167 research reports from the owner's provided private archive; their 1,553 public section records remain available.

See `docs/METADATA_VALIDATION.md`, `tools/test_semantic_metadata.py` and the private master's unmodified reference research for the detailed methodological boundaries. External tests such as Google Rich Results, DataCite/DOI deposits or independent scientific review have not been performed; the attached research papers are technical recommendations, **not** authoritative evidence that these services are implemented or required for the fictional Eviulon collection.

---

# Recovered synchronized release v2026.11.19.3.14.1-RECOVERED

This is the v3.14 **recovery** patched for synchronized artifact metadata (site v3.14.1), NOT the lost v3.18 implementation. The original website functional code, printed page corpus and research section text are unchanged. See `RECOVERY_STATUS.md` and `RELEASE_SYNC.json` first.

---

# Eviulon Library v3.14 — Research Browse Navigation

**Status:** Locally tested staging release; **not deployed by the assistant**. No additional paid services. Deploy in place of v3.13 only after backing up your current live site.

## Fixed discoverability issue

- Research was linked in the footer and search results but **missing from the primary navigation**. A persistent **Research** link now appears next to Books throughout the site.
- The homepage retains the fourteen official book cards as primary, and offers a small research link plus a dedicated, lower-priority browse section after the book collection.
- Visitors can open **All 210 reports**, **90 Eviulon reports**, or **120 Evulgare reports** immediately, without any search query or JavaScript.
- The `/research/` directory now shows collection counts and clearly identifies the selected category. All 210 original report landing URLs and their 1,553 section URLs are unchanged.
- **No changes** to official book text, research source files, book-only search defaults, report disclaimers, static API optimization, MCP/AG-UI/REST, or `.htaccess` privacy rules.

## Deploy and verify on LiteSpeed

1. **Back up** the entire current web root and any private monitoring config/records separately. Keep `.uai`, unpublished originals and private benchmarks outside public web files.
2. Upload/extract the **entire ZIP contents** into the existing library document root. Include the hidden `.htaccess`, `api-cache/`, and updated `assets/style.css`; do **not** upload this private full-text archive to the public GitHub discovery repository.
3. From the site homepage, confirm **Books** remains the primary collection and the top navigation now includes **Research**. Follow Research → `/research/` → Eviulon or Evulgare → a report → its sections without searching.
4. Verify `/research/` lists **210**, Eviulon **90**, Evulgare **120**, with a clearly visible supplemental disclaimer. Check the menu on mobile and within book readers.
5. Verify `curl -I https://library.eviulon.com/api/v1/books/` still serves static cache headers and `/api/v1/books/` remains responsive; search starts with Books selected and Research unchecked; the MCP and AG-UI routes still work.
6. **Security:** direct GETs to `/data/books.json`, `/data/research/reports.json`, `/src/bootstrap.php`, `/tools/test_research_navigation.py`, and `/.git/config` should be 403/404; any 200 is a rollback condition. Keep source-derived files private.
7. Roll back to the previous known-good deployment if private paths become accessible, the official books/canonical pages stop working, research URLs break, or navigation fails. Preserve private monitoring config separately.

For implementation and tests, see `docs/RESEARCH_BROWSING.md` and `QA_REPORT.md`.

---

# Eviulon Library v3.13 — Fast Bot and API Delivery

**Status:** Tested staging release, **not deployed by this assistant**. **Additional services and fees: none.** The production host is LiteSpeed/PHP; external testing of earlier MCP endpoints was supplied by the owner, but this v3.13 package is not yet deployed or measured there.

## What's faster

- **241 prebuilt JSON catalog/metadata responses** are served by LiteSpeed/Apache with no PHP bootstrap. Includes `/api/v1/books/`, individual books and TOCs, the default research catalog, and 210 report metadata responses.
- **Discovery files** (`robots.txt`, `llms.txt`, XML sitemaps, OpenAPI, knowledge JSON, Atom) now bypass PHP for ordinary GET/HEAD crawler requests.
- Native **ETag / Last-Modified / 304 / HEAD** behavior lets compliant clients revalidate without redownloading a full body; cache TTL is 3600 seconds.
- **PHP monitoring is opt-in** (`EVIULON_MONITOR_ENABLED=1`), not on by default; no request-log reviews are required for this optimization. Existing authenticated dashboard, if configured, remains available but without new observations by default.
- Unchanged: canonical books (14/1,925), supplemental research (210/1,553), search UX and source defaults, REST response objects, AG-UI/MCP functionality, citations, disclaimers, original source content, and security rules.

## Deploy safely on LiteSpeed

1. Back up the current live website and separately retain any real `data/monitor-config.php` and `data/monitor-logs/`. Keep private `.uai` files and benchmarks outside the web root.
2. Unzip **all contents** of this archive into the site's current document root; ensure the root `.htaccess` and public `api-cache/` directory are included. Do not upload this full-text deployment archive to the public discovery GitHub repository.
3. Do not run build scripts on production: the 241 snapshots are already generated. `php tools/build_api_snapshots.php --check` can be run locally on the extracted release to confirm they match source records.
4. Verify `curl -I https://library.eviulon.com/api/v1/books/` returns **200**, `X-Eviulon-Delivery: prebuilt-static-json`, a public cache directive, `Content-Type: application/json` and an `ETag`. `curl -I https://library.eviulon.com/openapi.json` should return 200 with native cache validators and without PHP `X-Powered-By`.
5. Verify the private paths `/data/books.json`, `/src/bootstrap.php`, `/tools/build_api_snapshots.php`, and `/.git/config` return **403 or 404**. Reject the deployment if any private file becomes publicly readable.
6. Verify `/api/v1/research/?page=2` still returns page 2; search still starts Books-only; both source pagers and research facets work; individual print pages and reports render; the 6-tool MCP server and AG-UI still answer requests.
7. If static rewrites don't take effect on LiteSpeed or canonical reading/privacy fails, revert to the previous working release. See `docs/FAST_DELIVERY.md` for details and latency-testing commands.

**Performance evidence:** Controlled local Apache `/api/v1/books/` benchmark of 250 concurrent-sample requests at concurrency 8: v3.12 ~3,250 requests/sec vs v3.13 ~16,483 requests/sec (roughly **5×** throughput). This is **not** a measured improvement on the live host. Static HTTP contract 2,215/2,215 assertions passed across all 241 snapshots. The 15-stage PHP acceptance suite reached its final stage before the execution limit; its last release/HTTP stage also passed independently under Apache. No original source-derived files were changed.

**Further reading:** `docs/FAST_DELIVERY.md` · `QA_REPORT.md` · `CHANGELOG.md`.

---

# Eviulon Library v3.12 — Supplemental research hyperlinks

**Status:** Locally validated staged release, **not deployed to production**. **Incremental service cost:** $0.

## Improvement over v3.11

- Existing research HTML contained 8,501 clickable source links but left other URL-shaped text as inert text in tables, paragraphs and technical research notes.
- The server now converts 253 additional valid HTTP(S) URLs in 42 report sections into accessible hyperlinks and recognizes complete URLs in Research search excerpts, including bare URLs near punctuation, quotes and em dashes. Existing 8,501 anchors remain intact.
- The transformation occurs in the read-only HTML renderer. The 210 original reports, 1,553 section JSON records, 14 official books, 1,925 print pages, search indexes, canonical URLs, REST/AG-UI/MCP contracts and original source hashes are unchanged.
- Source code, code blocks, comments, HTML attributes, unsafe URL schemes and invalid pseudo-schemes are not modified.
- Newly created external links open in a separate tab using `rel="noopener noreferrer external"`. Clickability does not validate the report's external claims or the destination's availability.

## Deployment and rollback

1. Make a separate backup of the live website, `data/monitor-config.php`, and the private `data/monitor-logs/` directory. Keep private evaluation answers and `.uai` memories outside the web root.
2. On PHP 8.1+ and Python 3.10+, run `bash tools/run_local_qa.sh` on a freshly extracted copy. The 15-stage gate includes every previous contract plus the new exhaustive research-link tests.
3. Deploy **the ZIP contents** to the existing Apache/PHP document root; do not upload this complete content archive to the public GitHub discovery repository.
4. Verify new links on `/research/eviulon/eviulon-library-preservation-audit/6/` and `/research/eviulon/eviulon-ai-access-architecture/3/`, and pre-existing links on `/research/eviulon/eviulon-infrastructure-resilience-plan/5/`.
5. Confirm Books is checked and Research unchecked by default; all report disclaimers persist; the 14 book landing pages and print-page reader still work.
6. Verify Apache forbids direct `/data/`, `/src/` and `/tools/` files and test REST/OpenAPI/AG-UI/MCP. If links, source privacy or reading regress, restore the last verified live package.

See `docs/RESEARCH_LINKS.md` for the design and exact tests. Server-side linkification requires no external service or JavaScript. **Production has not been verified by this assistant.**

---

# Eviulon Library v3.11 — Deploy and Roll Back

**Status:** Staging candidate; not uploaded to production by this assistant. **Service cost:** $0 beyond existing PHP/Apache hosting.

## What changed (v3.10 → v3.11)

- Added **interactive refinements** to the search UI: select an individual official book, or (only after choosing Research) refine supplemental reports to Eviulon or Evulgare.
- Each source filters independently. Its pager, total and visible results are source-scoped; the other source's page number and total are preserved.
- Matched-volume and research-collection statistics have drill-down links. The API distinguishes the full original-query facet counts from the current **filtered** totals so the statistics cannot accidentally describe just the visible page.
- Added strict 400 validation for unexpected book/collection filters in HTML and read-only JSON search. Legacy REST, AG-UI and MCP search interfaces retain their prior contracts unless new facet/paging parameters are explicitly supplied.
- All source records, print-page permalink structures, HTML reader layout, research disclaimers, protected paths and book-first defaults remain unchanged. See `docs/SEARCH_FACETS.md`.

## Deployment preparation

1. **Back up the live web root first**, plus `data/monitor-config.php` and `data/monitor-logs/` separately. Never replace production credentials or monitoring history with staging data. Keep private evaluation material outside the web root.
2. On a development machine with PHP 8.1+ and Python 3.10+, unpack this root-deployable ZIP and run `bash tools/run_local_qa.sh`. This executes the old v3.10 pagination suite and the new 29-case faceted search contract, then all established API, MCP, security, source and print-page tests on a disposable PHP server.
3. Inspect the ZIP inventory and the included SHA-256 checksum. Deploy the **contents** into the existing Apache/PHP document root, ideally using an atomic directory replacement or with a verified rollback package on hand. Do not upload this full-text website ZIP to the public GitHub discovery repository.
4. On the live site, open `/search/?q=machine&filters=1&scope%5B0%5D=books&scope%5B1%5D=research&per_page=50`. Check default Books-only in a fresh search; opt into Research manually, select a single book, switch Research collection, then page both sources separately and clear each facet. Confirm count totals and source labels.
5. Verify that `/data/books.json`, `/data/research/reports.json`, `/src/bootstrap.php`, and `/tools/test_faceted_search.py` are **403/404**, never public HTML/text. Verify single print-page canonical URLs, book chapter navigation, landscape/portrait display and private dashboard authentication.
6. Run `python3 tools/live_agent_readiness.py --base-url https://library.eviulon.com` and `python3 tools/test_mcp.py --http https://library.eviulon.com`. Inspect browser presentation and mobile layout manually; existing testing here cannot certify actual production Apache behavior or real third-party MCP clients.
7. **Roll back to your previous verified live release** if official Books defaults, source privacy, canonical citations, reader UX, AG-UI/MCP integration, performance or independent result pagination fails. Preserve live monitoring configuration and logs.

**Architecture:** No new framework, external database, generated manuscript files, client-side dependency, paid service or AI inference endpoint. Source-derived content SHA-256 integrity remains based on the original 5,105-file manifest. This is a staged artifact; completion of local tests is not a live production verification.

---

# Eviulon Library v3.10 — Deployment and rollback

**Purpose:** Fix human search pagination, increase useful results per page, and add exact source-aware statistics. **Deployment state:** Locally validated; not uploaded to https://library.eviulon.com/ by this assistant. **Additional paid-service cost: $0.**

## Changes compared with v3.9

- Books and Research now page independently (`books_page` and `research_page`), preserving the other source's page number. A combined query shows up to 50 Books and 50 Research hits by default instead of splitting 30.
- Users may choose 25, 50 or 100 **results per source**. The new collapsible book and research breakdowns count matching original print pages and individual research report sections across the FULL result set.
- The existing REST/AG-UI/MCP search contracts are backward compatible. New JSON API mode is opt-in via `per_page`, `books_page`, or `research_page` query parameters. See `docs/SEARCH_PAGINATION.md`.
- Original 14 official books, all 1,925 print pages, the 210 research reports and their 1,553 sections, 5,105 source-derived content files, the reader and canonical citations are unchanged.

## Preflight and deployment

1. **Back up the existing production document root and separately preserve `data/monitor-config.php` and `data/monitor-logs/`**. Do not overwrite credentials or real monitoring history. Do not place the private evaluation archives inside the web root.
2. Run `bash tools/run_local_qa.sh` on this unpacked package; it starts a disposable PHP server and performs the full 15-stage regression suite, including `tools/test_independent_search.py`.
3. Deploy the ZIP contents (not the parent directory) into the existing PHP/Apache document root. Prefer an atomic directory switch. Do not upload the full website package to the GitHub discovery repository.
4. On the live site, search a popular term with **Books only** (the default), then select **Books + Research**. Verify two separate sections, 50 items each where matches allow, and correct totals, breakdowns and disclaimers.
5. Navigate Books to page 2 and Research to page 3; moving one pager must not move the other. Try the 25 and 100 result selectors on desktop and mobile; navigate via the source jump links. Test empty queries, no checkbox selection, rare words, and out-of-range page URLs.
6. Run `python3 tools/live_agent_readiness.py --base-url https://library.eviulon.com` and `python3 tools/test_mcp.py --http https://library.eviulon.com`; both are free, read-only checks. Confirm direct HTTP access to `/data/books.json`, `/data/research/reports.json`, `/src/bootstrap.php` and `/tools/test_independent_search.py` is **403/404**, not 200. Verify canonical book pages and single/double reader layout.
7. If privacy, book-first defaults, canonical URLs, navigation or live performance regress, restore the last successful version and the preserved monitor files. This is a **controlled deployment candidate**, not proof of a successful live release.

**Visual validation limitation:** This environment blocked automated Chromium navigation to the localhost fixture, so real-browser appearance and production server behavior must be verified after upload.

---

# Eviulon Library v3.9 — Deploy and rollback

**Target:** https://library.eviulon.com/ · **Status:** staging and local QA, not deployed or tested on the live host · **Additional paid cost:** $0.

## Release delta (v3.8 → v3.9)

An additive **modern MCP 2026-07-28 stateless tools-only endpoint** at `POST /mcp/`. Existing REST/OpenAPI, AG-UI, website search, canonical book pages and human reader stay intact. Six read-only tools expose the existing official books, bounded topic search/evidence, one print page, one book TOC, and an explicitly supplemental research section. Older `initialize`/session MCP clients are **not** supported; use REST/OpenAPI or AG-UI for compatibility. Details in `docs/MCP_TOOLS.md`.

**Source and privacy guarantees:** Books 1–14 / 1,925 print pages official by default; 210 reports supplemental and never implicit. The 5,105 source-derived files must pass the unchanged SHA-256 integrity manifest. No `.uai` private memory, production monitor credentials/logs, original full-book PDFs/EPUBs or private benchmark answer keys belong in the package.

## Operator instructions

1. Back up the live web root, `data/monitor-config.php` and `data/monitor-logs/` separately. Do not upload private eval packs or public GitHub source in place of the website ZIP.
2. On a local machine, run `bash tools/run_local_qa.sh` (PHP CLI + Python 3). It serves a disposable copy and includes the 59-case MCP protocol suite and 1,925 canonical-page checks.
3. Deploy this complete ZIP into the existing Apache/PHP document root, ideally via an atomic switch. Preserve the live monitoring secrets and logs. **Do not upload the site ZIP to GitHub**.
4. After deployment, run `python3 tools/live_agent_readiness.py --base-url https://library.eviulon.com`, followed by `python3 tools/test_mcp.py --http https://library.eviulon.com`. Both are no-cost, read-only tests against the canonical HTTPS host.
5. Verify Apache blocks direct paths to `data/`, `src/`, `tools/`, private memory or evaluation files. Confirm official book cards are first, reader portrait/landscape layout, search checkboxes default Books on/Research off, print-page citations, research disclaimer, admin authentication, robots/sitemaps, and MCP from an intended actual client.
6. If private paths return 200, canonical URLs/reader behavior regress, research becomes default, monitoring becomes public, or protocol validation fails: **rollback to whichever package actually ran successfully before this release**. Restore monitor config and logs separately.

The live website was inaccessible to this assistant's web checker before packaging; do not assume v3.9 is deployed or that a real client successfully used it. The modern MCP interface is documented but not separately certified through an official third-party SDK.

---

# Eviulon Commonwealth Library v3.8 — Production Deployment and Rollback

**Release:** 2026-11-18 · **Target:** `https://library.eviulon.com/` (existing PHP/Apache hosting)
**Status:** passed isolated local checks; **NOT uploaded or independently verified on the live host.**
**Additional paid services:** none. No hosted AI, GPU, MCP subscription, GitHub Actions or paid indexing tool required.

## Authority contract (non-negotiable)

The 14 authored Eviulon books remain the official source, visually primary and searched by default. Their 1,925 independently citeable paperback working-edition page URLs and two-page reading layout are unchanged. The 210 Eviulon/Evulgare reports remain **supplemental, not approved doctrine**: Research search is unchecked by default, must be explicitly selected by an agent, and is always labeled and ranked after books. Publication/retail approval is not implied for the working book editions, particularly volumes XIII–XIV. The omnibus is a separate larger-format hardcover.

## v3.8 delta from v3.7

- **New:** `GET /api/v1/context/?q=machine+identity` — deterministic, exact, byte-verified evidence bundle sourced from one print page or research section per citation. Defaults to Books only. `limit=1..8`, quote max 480 UTF-8 bytes, lexical `match=all|any`. This does **not** generate answers or bulk text.
- **New:** AG-UI SSE `state.action=context` to deliver the same short, grounded source excerpts and permanent citations; research still requires explicit scope.
- **Updated:** OpenAPI 3.1, API discovery directory, `/for-agents/`, `llms.txt`, public source methodology and locally runnable QA.
- **Updated:** read-only production readiness probe checks 22 conditions, including new default/context classifications.
- **Unchanged:** all 5,105 source-derived page, research and index files; existing 1,925 canonical reading pages; research disclaimers; authenticated monitoring contracts; independent agent pilot, private evaluation policy and no whole-book download design.

## 1. Before touching production

1. Back up the entire current web root, production `.htaccess`, and owner-controlled copies of `data/monitor-config.php` plus `data/monitor-logs/` (do **not** include these in a public archive).
2. Confirm Apache `mod_rewrite` and `.htaccess` are enabled. Verify direct requests to `/data/books.json`, `/data/research/reports.json`, `/src/evidence.php`, `/tools/test_source_evidence.py`, and `/.uai/private.uai` produce 403/404. If any return HTTP 200, **stop; the server is not safely configured**. Do not rely on robots.txt for confidentiality.
3. Run `bash tools/run_local_qa.sh` on an owner-controlled computer with PHP 8.1+ and Python 3.10+. It uses a disposable server root, no paid APIs, and does not mutate public book source files.
4. Keep private operator packs, private gold answer keys, crawler logs, passwords, `.uai`, full-book PDF/EPUB and full manuscript archives **outside** the website root and public GitHub discovery repository.

## 2. Deploy

Prefer a temporary upload folder, verified file inventory, and atomic web-root swap if your existing host supports it. Otherwise back up the current website and extract the ZIP **into the existing document root**, not one directory below it. Do not overwrite production monitor configuration or live logs. Do not copy the private pilot ZIP into the public site.

The root `.htaccess` file controls private-path protection and rewrites virtual book/API routes through `index.php`. The PHP built-in test server uses `router.php` and is **not** evidence of production Apache correctness. Your host must allow rewriting and have normal PHP execution disabled for files beneath blocked source directories.

## 3. Production smoke gate — run from your local computer

```bash
python3 tools/live_agent_readiness.py \
  --base-url https://library.eviulon.com \
  --report-out /YOUR_PRIVATE_LOCAL_FOLDER/v3.8-readiness.json
```

It performs **22 bounded GET-only checks** against exactly the canonical HTTPS hostname, checks book/research authority, new evidence bundles, and private path controls. It refuses foreign hosts, redirects and unexpected responses. `--report-out` must point to a private directory outside the web root and an absent filename (exclusive, mode-0600 output). A result of **22/22 is required but not sufficient** for full production acceptance; it does not verify browser appearance, indexing, a crawler's true identity, or AI training.

Manually inspect: homepage priority of fourteen book cards; portrait and landscape reader; print-page citations and chapter links; default Books checked/Research unchecked; secondary research disclaimer; `/for-agents/`; `GET /api/v1/context/?q=cognitive+liberty`; `GET /api/v1/context/?q=machine&scope=books,research`; authenticated monitor; HTTP 403/404 on every internal path; sitemap and canonical URLs. Real TLS, headers, Apache rewrite rules and 304 behavior must be validated on the actual host.

## 4. Rollback conditions

**Immediately restore the previous known-good deployed package** (v3.7 *only if actually deployed*, otherwise whichever release is live) if any of these occur: source paths become public, canonical page URLs shift, printed-page contents or pagination change, books cease to be search default, research is silently included, source quotes/citations disagree, AG-UI or REST regress, monitors become unauthenticated, or redirects/HTTPS break. Restore preserved live monitor config and logs separately; never replace them with stale artifacts.

## 5. Real agent evaluation remains a separate operation

The earlier private v3.7 operator pack contains only unapproved pilot questions and blank review materials. Human approval of source-backed gold, real external-agent transcript capture, and two independent human evaluations are still required before any answer-quality score is reported. v3.8 confirms **source accessibility and literal-quote fidelity**, not understanding, search-engine indexing, model-training dataset participation, or recognition of a real Eviulon government.

See `docs/EVIDENCE_BUNDLE_API.md`, `docs/AGENT_PILOT_OPERATIONS.md`, `docs/AGENT_ANSWER_EVALUATION.md`, `docs/PRODUCTION_READINESS.md`, and `QA_REPORT.md`.
