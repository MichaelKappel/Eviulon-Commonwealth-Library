# v3.14.4-STATIC-DELIVERY — static file continuity and web-server performance contract

- Retains and revalidates all 241 prebuilt API JSON catalog/toc/report metadata snapshots introduced in v3.13.
- Adds reproducible `ai/static-delivery.json` inventory of 280 public static files, each with SHA-256 hash and byte size. Includes 17 sitemaps, five discovery files and 17 assets; no book-page or report-section text export.
- Adds explicit fast-revalidation cache headers for existing public CSS, JS and cover assets; keeps web-server ETag and conditional `304` responses.
- QA now rejects missing/stale static files and exercises all 241 snapshot routes; a separate real Apache/LiteSpeed integration audit checks static delivery bypasses PHP.
- Preserves dynamic HTML, citation/evidence APIs, research section source text, search, AG-UI, and MCP unchanged except release/version identification.
- Full source and Runic memories remain private. This is recovery-line v3.14.4, **not** lost v3.18 and **not** a live deployment.

# v2026.11.19.3.14.3-LEARNING-SEEDING-MEMORY — private AI-learning and seeding continuity

- Website runtime and source corpus unchanged from v3.14.2 metadata-corrected staging; release ID/metadata updated only.
- Eight original owner research papers preserved under private `/docs`, byte-for-byte.
- Runic main totem and memory handoffs updated with authoritative research deep links, integrity manifests refreshed.
- Private docs/Runic files not copied into public release surfaces. A full private master, website root and GitHub project are synchronized.
- Site metadata, SEO, external AI ingestion and actual model training are not thereby proven.

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

# v3.14 — Site-wide Research Browsing (2026-11-19)

- Fixed missing Research link from primary header navigation across the public library.
- Added a small homepage research link and a deliberately secondary browse section below official books with separate Eviulon (90) and Evulgare (120) links.
- Improved `/research/` category counts, selected-category accessibility, and full 210-report browsing without search.
- Preserved books-first default and all 5,105 source-derived records, canonical book/report/section URLs, and API/static delivery optimizations.
- Added `tools/test_research_navigation.py`, validating all 210 report landing URLs via HTTP plus headers, categories, and authority messaging. Production not deployed.

---

# v3.13 — Fast static catalog and bot delivery (2026-11-19)

- Added deterministic deploy-time public API snapshots (241 metadata/discovery records, 384,538 bytes) with Apache/LiteSpeed `.htaccess` GET/HEAD rewrites at all original URLs. Requests no longer start PHP for book catalogs, book metadata, chapter TOCs, default research catalog, report metadata, and agent API discovery.
- Released robots.txt, llms.txt, OpenAPI, knowledge JSON, sitemaps and Atom from the forced PHP monitoring route. GET/HEAD now use native static web-server delivery and conditional caching. Unsupported methods remain rejected through the prior PHP error path.
- Monitoring is now opt-in (`EVIULON_MONITOR_ENABLED=1`) to avoid appends/locks on dynamic crawler and human requests by default. Local observability tests enable it in an isolated fixture; existing dashboard and private historical data remain protected.
- All static snapshots generated from exactly the same payload functions used by dynamic fallback. Added `tools/build_api_snapshots.php --check` (stale/missing snapshot detection) and `tools/test_static_delivery.py` (HTTP body/header/security checks).
- Apache 2.4 local all-snapshot test: 2,215/2,215 checks passed. Baseline `/api/v1/books/` 250-request concurrency-8 benchmark improved from 3,249.71 to 16,483.15 req/s locally (~5×; not a production measurement). Core source integrity: all 5,105 unchanged.
- No new bulk book download, no change to canonical URL, edition text, report authority, search filtering, REST/AG-UI/MCP contracts, or full-source publication rights.

---

# v3.12 — Research reference hyperlinks

- Added a pure-PHP HTML text-node linkification pass to the original research section reader and Research search-result excerpts. Keeps existing links; safely activates HTTP(S) URLs in normal report prose/tables/footnotes; no data rewrites.
- Handles HTML entities, encoded quotes, balanced URL parentheses, Unicode dashes and punctuation while leaving code samples and unsafe schemes untouched.
- Added corpus-wide `tools/test_research_links.php` and real server `tools/test_research_links_http.py` to the existing isolated QA runner; source integrity remains 5,105/5,105 unchanged.
- Current local corpus: 8,501 previously clickable reference anchors preserved, 253 newly activated URLs in 42 supplemental research sections. Books remain official and primary.
- Added `docs/RESEARCH_LINKS.md` and a production-only link verification/rollback checklist. No live website or external destination was independently verified.

---

# v3.11 — Search facets and query refinement (2026-11-19)

- Added official-book facet dropdown and one-click drill-down links for each book's full-query match counts.
- Added optional Eviulon/Evulgare research-collection facet with separate navigation and explicit opt-in preserved.
- API reports filtered totals and source-specific page windows alongside original unfiltered facet distributions, with source provenance and canonical citations unchanged.
- Invalid facets reject with HTTP 400 and no accidental fallback to broader unfiltered results. Legacy REST, AG-UI and MCP output remains backward compatible.
- Added 29 black-box HTTP regression checks and expanded existing release-runner stage six; documented exact counting units, rollback and production caveats.
- All 5,105 source-derived content files remain unchanged; no new private data or whole-book downloads included.

---

# v3.10 — Independent Search Pagination and Match Statistics (2026-11-19)

- Replaced the shared 30-hit search result budget with two independently paged panels: Books (official) and Research (supplemental).
- Default **50 hits per selected source**, with 25/50/100 choices. Changing Books pages preserves the Research position and vice versa.
- Query-level statistical panels show exact matching book pages, represented books, matching research sections, represented reports, Eviulon/Evulgare research breakdowns, and top-matched reports.
- Added accessible numeric pagination, source jump links and contextual ranges, and zero-hit and overlarge-page handling.
- Added opt-in independent pagination for the JSON API, documented with OpenAPI; legacy API and MCP/AG-UI behavior unchanged.
- Added 30-case HTTP regression suite to the disposable local release gate. All 5,105 source-derived files unchanged.
- No extra paid dependencies; no changes to manuscripts, reports, original print-page links, reader layout, research disclaimers or private data access.
- Live deployment and browser visual acceptance remain to be verified by the operator.

---

# Changes — Eviulon Library v3.9 (2026-11-18)

- Added **read-only stateless MCP 2026-07-28 Streamable HTTP** at `/mcp/`, with `server/discover`, `ping`, `tools/list` and `tools/call`; one JSON-RPC response per request. No legacy session protocol or hosted LLM.
- Six bounded read-only tools for official books, lexical search, exact evidence bundles, individual print pages, chapter landmarks and **explicit** supplemental research sections. Books remain default and primary.
- Security: strict version/method/name mirrored-header validation, 16-KiB request limit, no batches, origin validation, strong input contracts, no wildcard cross-origin browser access, no arbitrary file paths or writes.
- Added an independent dependency-free 59-case live-HTTP MCP protocol test in the isolated full QA release gate; CLI restricts smoke targets to canonical HTTPS or loopback.
- Updated public agent guide, API discovery directory, `llms.txt`, version and production documentation.
- **Unchanged:** all 14 official book records, 1,925 print pages, 210 research reports, 1,553 research sections, working-edition citations, book-first selection, privacy boundary and no-full-book-download policy.
- Local tests only; live domain access and real agent compatibility remain unverified. No extra paid services.

---

# Eviulon Commonwealth Library — v3.8 (2026-11-18)

## Added — Source evidence bundles, reproducible provenance

- `GET/HEAD /api/v1/context/` returns up to eight bounded (480 UTF-8 byte) **exact substrings** from source-verified canonical print pages or explicitly selected research sections. Each result includes start-byte position, digest, canonical permalink, precise citation and official/supplemental classification. No answer generation or full-book export.
- New AG-UI `state.action=context` streams those same short source excerpts and citations. Existing `search`, `research` and `page` behaviors retain their contracts.
- Added strict query, scope, match and limit validation, encoded-control-byte rejection, fail-closed HTTP 400 errors and bounded response sizes.
- New OpenAPI 3.1 components (`EvidenceQuote`, `EvidenceSource`, `EvidenceBundle`) and `getSourceEvidence` operation, plus discoverable documentation and agent guide.
- Added `tools/test_source_evidence_unit.php` (17 unit tests), `tools/test_source_evidence.py` (38 HTTP checks) and two new GET-only live-readiness conditions (22 total). Integrated into disposable `tools/run_local_qa.sh`.
- `docs/EVIDENCE_BUNDLE_API.md` describes exact-byte extraction, rights/copyright limits, citation verification, prompt-injection boundary, research disclaimer and no-training guarantees.

## Unchanged — Existing source and user experience

- Fourteen official authored books; 1,925 standalone print-page permalinks; original reading layout, section headings and chapter pages.
- 210 supplemental Eviulon/Evulgare research reports, 1,553 searchable sections and explicit opt-in.
- Original API routes, search filters, JSON citation semantics, monitoring, AG-UI SSE pagination, 3,707 canonical sitemap URLs, and existing 5,105-file source-content integrity baseline.
- No public private `.uai`, secrets, production logs, full-books PDF/EPUB or evaluation gold data.

## Verification boundary

Release passes reproducible **local** tests; production Apache/TLS and all external-agent/human evaluation results remain unverified. A quoted page is evidence of what the authored source contains, **not** proof that a model has been trained on it or that the source's claims are independently verified.
