# v3.14.12 — Discovery attestation release gate

A metadata-only static discovery receipt at `/ai/discovery-attestation.json` binds the release ID, source-registry JSON-LD bytes, original public metadata SHA-256 fingerprints, lexical topic catalog, robots/llms, 17 sitemap children, and the complete 3,729 canonical sitemap URL set. The offline validator proves 3,702 registry/HTML reading URLs plus 21 topic URLs plus 6 navigation URLs, with six adversarial missing/duplicate/altered URL rejection tests.

**15/15 local QA** passed: **98,315 semantic metadata checks over 3,729 canonical HTML URLs**; **3,664 development-server static checks**, **4,311 strict Apache static tests**, **711 canonical HTML**, **702 topic**, **11 registry**, **11 strict attestation**; **all 5,105 original published source files unchanged** and **260 protected Runic memory files preserved**. PHP bypass, ETag, `304` and HEAD checks passed for the static attestation, and unsupported POST returns 405. Live HTTP audit now verifies all 17 child sitemap SHA-256 hashes and the 3,729 URL-set fingerprint.

**Limits:** the tests are local, and the public hostname remained unreachable in the available external browsing check. No deployment, external search indexing, rights approval, factual corroboration or model training is established. **164/210 supplemental original report source hashes remain unmatched**; every published section record remains preserved.

## v3.14.11 — Registry/HTML structured entity identity parity

**All 3,702 canonical reading HTML pages** now carry registry-discoverability `<link rel="alternate" type="application/ld+json">`; 14 official Book entities, 210 supplemental Report entities and 3,478 individual print-page/section identities use the same schema.org `@id` in both the metadata-only registry and canonical page JSON-LD. Research stays explicitly unverified. The new corpus-wide validator verifies exact identity, parentage, entity type, and canonical links, preventing duplicate or orphaned identities.

**15/15 full local QA stages passed**, including **98,315** metadata assertions over **3,729** canonical URLs; **4,299** Apache static-delivery checks, **711** canonical reading checks, **702** topic checks, **11** source registry checks, and **4** sampled identity-link HTTP checks, in addition to the 3,702-page offline graph comparison. The original **5,105** content records, **260** protected Runic memory files and eight private learning/seeding studies are unchanged. **Production DNS was not resolvable from this environment; production deployment, external indexing and model training are NOT verified.**

See `docs/JSONLD_ENTITY_IDENTITY_ALIGNMENT.md` and `tools/test_jsonld_entity_alignment.py`.

## v3.14.10 — machine-readable, metadata-only source registry

Canonical public JSON-LD at `/ai/source-registry.jsonld` covers **14 official books, 210 supplemental unverified reports, and 3,478 original page/section URLs**. Exact source SHA-256 values from existing published metadata, working book editions, and stable individual citation-route templates. Never confuses fictional authored canon, unverified research and externally corroborated facts. No manuscript text, private `.uai` sources, training license, DOI or peer-review claims.

Full local regression **15/15**; **98,315** metadata assertions across **3,729** canonical HTML URLs, **4,299** Apache static HTTP checks, **711** canonical reading, **702** lexical topic and **11** registry checks. All **5,105** original content records unchanged; protected **260** Runic memory records intact. Live production not deployed. Read `docs/SOURCE_REGISTRY_JSONLD.md`.

## v3.14.9 — source-grounded lexical topic navigation

20 exact phrase topics; 21 canonical static topic pages, bounded source-verified evidence, sitemap and machine-readable `/ai/concepts.json`. Book-primary and explicitly unverified supplemental research. Query-bearing requests use PHP. See docs/SOURCE_GROUNDED_LEXICAL_TOPICS.md. Final local QA PASS: 15/15 stages; 98,315 semantic assertions; 4,287 Apache static checks; 711 Apache canonical HTML checks; 702 Apache topic checks. Still NOT live deployed.

## v3.14.8 — query-safe static metadata API

All prebuilt metadata API rewrites now require an empty query string; query-bearing requests reach the PHP handler. Direct canonical GET/HEAD remains static; 3,702 HTML and 3,719 JSON snapshots retained. See docs/STATIC_API_QUERY_GUARDS.md. Local 15/15 QA PASS; strict Apache 4,103 static JSON + 711 HTML checks PASS; 97,937 metadata checks PASS. Dropbox preservation is tracked independently. NOT live-deployed.

## v3.14.7 — hash-verified resumable HTML snapshot builder (local release)

Static canonical HTML build never trusts modification times. Every reused page must match an exact dependency digest plus its own recorded SHA-256 and route. Interrupted builds resume using atomic validated checkpoints; full tests now include adversarial stale-cache scenarios. See `docs/STATIC_SNAPSHOT_INTEGRITY.md`. The 3,702 canonical reading HTML pages and 3,719 static JSON snapshots remain unchanged in scope; live deployment/performance still unverified.

## v3.14.6 — static canonical reading HTML (staging; verify production separately)

Source-generated HTML snapshots for official print pages and supplemental research sections; no-query canonical GET/HEAD only; all source text records untouched, research unverified; re-render and verify via `tools/build_static_html.py`. HTML snapshots stay OUT of public GitHub.

# v3.14.5 — Static citation delivery (staged, not deployed)

**Release ID:** `v2026.11.19.3.14.5-STATIC-CITATIONS`. Rebuilt from recovered v3.14.4, **not** recovered historical v3.18.

- Preserves all **241** existing static catalog metadata JSON routes, and adds **3,478** prebuilt fixed citation-metadata JSON responses: **1,925 official-book page citations**, **1,553 independently labeled supplemental research-section citations**. Total **3,719** static JSON snapshots, approx **3,869,820** payload bytes.
- Uses the **exact pre-existing PHP citation objects** (same fields and values) with no original page/section body text, book exports or report exports. The generated JSON is deterministic and source-derived.
- On Apache/LiteSpeed, `GET` and `HEAD` to canonical citation URLs **without query strings** now use public static files with web-server ETag, Last-Modified, cache, and `304`, bypassing PHP. The PHP development router emulates this for QA. Unsupported methods, invalid references and query-string variants retain their dynamic routes, errors and behavior. Full-text APIs, search, report reading, MCP and AG-UI remain dynamic.
- `/ai/static-delivery.json` now inventories **3,758** static public resources (3,719 metadata snapshots, 22 discovery files, 17 assets) with exact SHA-256s. **No original corpus text was modified:** 5,105/5,105 original files remain unchanged.
- Validation: `php tools/build_api_snapshots.php --check`, `python3 tools/build_static_delivery_manifest.py --check`, `python3 tools/test_static_delivery.py --http ... --all --strict-web-server`, and the full `bash tools/run_local_qa.sh` regression (15/15). Local Apache: **4,079/4,079 HTTP assertions**; complete PHP QA suite **15/15** including **97,937** metadata assertions over **3,708** canonical HTML pages.
- Static JSON is not a new rights grant, endorsement, scholarly validation or proof of AI training or ingestion. Supplemental research remains unverified and always labeled. **No production LiteSpeed deployment was performed.**

Deployment: extract only the **ROOT_DEPLOY** archive's contents at the existing website document root, including hidden `.htaccess` and `api-cache/.htaccess`. Keep private `.uai` memory, PDF manuscripts, and original report sources **outside** the web root. Maintain previous live monitoring logs and credentials separately; verify `X-Eviulon-Delivery`, `ETag`, `304`, and `Content-Type` from representative live citation URLs and confirm invalid citations remain 404. Restore the prior working deployment if host routing/security fails.

All releases must have **three matching, byte-verified archives** (PRIVATE_MASTER, ROOT_DEPLOY, PUBLIC_GITHUB), matching release manifests and SHA-256 checksums, plus a verified permanent backup in the owner's **private Dropbox** release folder before being called delivered. The GitHub archive contains only approved public source and metadata, never private memory or full body-text JSON. See `docs/STATIC_CITATION_DELIVERY.md`.

---

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

# v3.14 — Research Browse Acceptance

**Build:** All **15/15 isolated local release gates PASSED** (`/mnt/data/v3_14_qa.log`, exit status 0); not independently deployed to LiteSpeed. **Test focus:** explicit ordinary HTML links from every main navigation, home to research directory, collection filters, canonical report landings, supplemental-source distinction and unchanged Books default.

- New HTTP navigation suite: **263 assertions passing**, including 210 HEAD requests to complete report landings, category inventories Eviulon=90/Evulgare=120, and source classification.
- PHP files syntax-checked. **5,105/5,105 source-derived records unchanged**; original 14 books, 1,925 canonical print pages and 1,553 research sections untouched. Existing static snapshots, REST/AG-UI/MCP, search, routing, privacy, and 87+7 HTTP route/security assertions passed.
- Browser screenshots could **not** be collected: localhost browser navigation is blocked by the execution environment; responsive layout still requires visual checking after deployment.
- Prior v3.13 static API and source validation retained; results of the full v3.14 suite are recorded in the final release gate output.

---

# v3.13 — Performance and source-preserving verification

**Status:** STAGING / LOCALLY TESTED. Not deployed or tested on production LiteSpeed for this specific release.

| Check | Result |
|---|---|
| Deterministic static API snapshot consistency | PASS 241/241, 384,538 bytes total |
| Real Apache 2.4 HTTP static delivery (all routes) | PASS 2,215/2,215 assertions, all 241 snapshots |
| Real Apache legacy route / security regression | PASS 87 public URLs + 7 blocked/404 checks |
| PHP local release suite | Stages 1–14 passed; last stage exceeded the execution limit and then **passed separately under Apache** |
| Original source corpus SHA-256 | 5,105/5,105 unchanged |
| Official print pages | 1,925/1,925 passed |
| MCP and evidence | 59/59 MCP; 38/38 evidence |
| Existing JSON/AG-UI | 26/26 passed |
| Search independent pagination and facets | 30/30 and 29/29 passed |
| Monitoring/auth/privacy (explicitly opt-in during test) | 36/36 passed |
| Research auto-link preservation | 6,249 assertions and 20 HTTP checks passed |
| Local Apache microbenchmark (catalog only) | 250 requests @ concurrency 8, v3.12: 3,249.71 req/s, v3.13: 16,483.15 req/s |
| Live LiteSpeed improvement | **Not measured or verified** |

Local Apache test used matching document roots for previous/new version, identical server configuration, no CDN, and ordinary HTTP (not the Internet). The 5× increase is not a guarantee of production speed, crawl volume, indexing, AI attribution, model training, or client support. Independent local REST/AG-UI/MCP tests verify implemented behavior, not conformance to a third-party client SDK. Source archives and private user logs are not included.

---

# v3.12 — Research linkification verification

**Status:** Locally tested staging release, not deployed. The new pure-PHP renderer preserves all 1,553 original report-section JSON records and all 8,501 previously rendered anchors; it activates **253 additional HTTP(S) links across 42 sections**. An exhaustive source-fidelity suite passed **6,249 assertions**. The HTTP integration suite passed **20 checks** on real local report pages. The unchanged original **5,105 source-derived files passed SHA-256 verification**. The complete 15-stage isolated QA runner finished successfully with exit code 0, covering the existing API/MCP/search/security suites and all 1,925 print pages. The source integrity baseline remains 5,105/5,105 unchanged. The report-link corpus scan ran in approximately 0.32 seconds using peak 13 MiB of memory.

New links are not assertions that destinations work or that the supplemental research is independently verified. Production TLS/Apache and browser compatibility remain unverified; a local Chromium screenshot attempt did not complete in the available environment.

---

# v3.11 Search Facet QA — 2026-11-19

**Status:** Staging, not deployed. **Evidence:** The new facet suite passed **29/29** and the v3.10 independent pagination suite passed **30/30** against an isolated PHP server. The first 12 of the 15 established release stages completed successfully; the full uninterrupted run was interrupted by the execution time limit during stage 13. Stage 13 observability passed **36/36** separately on a clean PHP fixture, stage 14 source integrity passed **5,105/5,105**, and stage 15 legacy route/static audit passed separately against a disposable server. Do not mistake this for a fully uninterrupted gate run.

Verified: per-book exact filtered page totals, per-collection exact research totals, independent source-pager links with retained filters, original-query facet availability, strict malformed/unknown parameter rejection, Books-only default, Research explicit opt-in, official book-first result ordering, unchanged legacy search behavior, the existing **1,925/1,925** page-route check, **59/59** MCP checks, the existing API/AG-UI and source-evidence checks, and normal private monitor behavior. No production browser rendering or real external-agent pilot was completed.

The HTML search form is server rendered and requires no JavaScript. The unfiltered and filtered match-count units are explicitly documented; no derived claim is made about model training, semantic search or authoritative status of research reports.

---

# v3.10 Search QA — 2026-11-19

**Result: PASS locally** (isolated 15-stage release gate). **Not deployed or browser-verified on the production host.**

| Check | Result |
|---|---|
| Independent Books/Research pagination and facet accuracy | **30 / 30 PASS** |
| Original book page HTTP routes | **1,925 / 1,925 PASS** |
| Original book/research/index source integrity | **5,105 / 5,105 unchanged** |
| Existing REST and AG-UI tests | **26 / 26 PASS** |
| Discovery and security checks | **38 / 38 PASS** |
| Source evidence tests | **38 / 38 PASS** |
| MCP protocol and security | **59 / 59 PASS** |
| Private observability and privacy | **36 / 36 PASS** |
| Local agent readiness checks | **22 / 22 PASS** |
| Other prior release gates | **PASS** |

**New regression coverage:** exact cross-page totals, all-book facet sums, both research collection sums, selected-scope authority, default checkbox state, 25/50/100 per-source windows, independent navigation state preservation, stable canonical citations, HTML-escaped queries, final-page clamping, zero hits, and legacy API compatibility. Combined search for `machine` on this local corpus yielded 1,074 matching official book pages and 937 matching supplemental research sections; these are term-index matches, not judgments of semantic relevance.

**Operational limitation:** Headless Chromium requests to the local fixture were blocked by this environment (`ERR_BLOCKED_BY_ADMINISTRATOR`); therefore responsive browser visual QA was **not** completed. The functional HTTP validation and PHP syntax checks passed. No verified live-domain deployment, search engine indexing, or external-agent comprehension is claimed.

---

# Eviulon Library v3.9 — Local Quality Assurance Report

**Date:** 2026-11-18. **Status:** PASS for isolated local release tests; **production not deployed or verified**. **Scope:** v3.8 source evidence plus additive MCP 2026-07-28 stateless tools-only transport. **Paid service requirement:** $0.

## Exit criteria met

| Contract | Result | Evidence |
|---|---:|---|
| MCP JSON-RPC HTTP, protocol and security contract | **59/59 PASS** | `tools/test_mcp.py` against disposable PHP site, including six read-only tools, 2026-07-28 discovery, header/body mismatch, malformed input, origin spoofing and explicit research opt-in |
| Modern MCP tool catalog | **6/6 exposed** | Book catalog; book-first search; short exact evidence; one print page; verified contents; one supplemental report section |
| Canonical original paperback pages | **1,925/1,925 PASS** | `validate_discovery.py --full-pages` |
| Source content SHA-256 integrity | **5,105/5,105 unchanged** | `verify_content_integrity.py` |
| Existing REST/AG-UI contract | **26/26 PASS** | `validate_agent_api.py` |
| Discovery/security regression | **38/38 PASS** | `validate_discovery.py` |
| Source Evidence HTTP contract | **38/38 PASS** | `test_source_evidence.py` |
| Source Evidence input/UTF-8 unit tests | **17/17 PASS** | `test_source_evidence_unit.php` |
| Production readiness HTTP probe (local only) | **22/22 PASS** | `live_agent_readiness.py` against local PHP server |
| Observability/auth/privacy contract | **36/36 PASS** | `validate_observability.py` |
| IndexNow no-network behavior | **6 tests PASS** | `test_indexnow.py` |
| Evidence ledger structure | **7 tests PASS** | `test_evidence_ledger.py` |
| Synthetic agent-answer evaluation | **23 unit tests PASS** | `test_agent_answer_benchmark.py` |
| Agent pilot helper | **11 unit tests PASS** | `test_agent_pilot.py` |
| Legacy static audit and access controls | **PASS** | `validate_release.py`, `validate_discovery.py` |
| Source-derived chapter retrieval / quote tests | **PASS** | Unmodified historical v3.5-v3.8 tests in isolated QA gate |
| PHP syntax and package-private boundaries | **PASS** | All source PHP parsed; no full-book download assets or private UAI memory |

## Test methodology

`bash tools/run_local_qa.sh` makes a disposable working copy, serves it using PHP built-in development server, executes tests with standard Python 3 and PHP CLI, then destroys the server copy including any generated monitoring records and private gold fixtures. The deployment folder is not used as the test web root. The full gate's terminal line must read **`PASS: All local release gates passed. No HTTP test logs were written to release root.`**

The independent `tools/test_mcp.py` suite sends actual JSON-RPC POSTs to the PHP server; it does not use mock server responses. It tests positive read operations, books-only default, research-only explicit opt-in, byte-hashed evidence, report disclaimer, tool schemas, error codes, header parity and request limits. Additional negative cases include malformed base64 header encodings and spoofed loopback Host+Origin combinations.

## Remaining production work / non-claims

- **No live verification:** This assistant's web checker could not reach `https://library.eviulon.com/`. Production hosting might still be running an older release; no live-site readiness results are claimed.
- **No official third-party MCP SDK certification:** The release implements the documented modern 2026-07-28 stateless tools-only profile; test it with the intended external MCP client after deploying. Older 2025-era `initialize` clients are intentionally unsupported. REST and AG-UI remain available.
- **No verified Apache security or TLS:** Confirm `.htaccess` actually blocks `data/`, `src/`, and `tools/` on the live host. Confirm admin authentication, monitoring, redirects and page rendering there.
- **No genuine independently reviewed agent answers:** Previous private 50-question material remains unapproved; no external 10-question agent score, two human reviewers, or model-training record is fabricated.
- **No inferred SEO outcome:** MCP availability is not itself proof that Google/Bing indexed book pages or foundation models ingested the content.
- **Host abuse controls:** Production may require hosting-level rate limiting; this build adds input bounds but does not claim to prevent full-book reconstruction from public HTML.

## Unchanged source authority

All fourteen authored books and their 1,925 canonical print pages remain primary. Supplemental 210 research reports / 1,553 sections remain separately disclaimed and require explicit opt-in. No private `.uai`, full PDF/EPUB/manuscript download, credentials or private evaluation gold is included in the release.

**Acceptance/rollback:** Follow `README_DEPLOY.md` and `docs/MCP_TOOLS.md`; immediately roll back if live source URLs expose protected files, official book defaults change, or MCP breaks existing REST/AG-UI routes.
