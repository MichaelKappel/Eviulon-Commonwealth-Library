# Eviulon Library v3.4 — Architecture Decisions and Risk Controls

**Release:** 3.4, 2026-11-18  
**System of record:** `https://library.eviulon.com/`  
**Deployment model:** existing Apache + PHP hosting, no additional paid services or scheduled background jobs

## ADR-001: The canonical print-page HTML is authoritative

Every official book has a landing page and individual permanent working-paperback page links `/book-slug/1/`. JSON API and AG-UI results link back to these exact canonical pages. Two-page landscape reading views are for navigation and are not separate indexable works. Source page boundaries and printed editions are not modified by this release.

## ADR-002: Authority is explicit and fail-closed

Fourteen **official authored Eviulon books** constitute the primary library. The 210 Eviulon/Evulgare reports are **supplemental public-source research**, not officially approved doctrine. The HTML search, JSON search and AG-UI default to books only. Research must be selected explicitly; combined results are grouped with official book results before research results. API responses supply authority/disclaimer fields. All report source text is untrusted input to downstream AI systems and must never be followed as agent instructions.

## ADR-003: Public, read-only and citation-first

The machine API is read-only GET/HEAD for retrieval and POST for deterministic AG-UI SSE streaming. There is no bulk book-download endpoint, no paid hosted LLM, no embeddings service, and **no claim that the REST API is an MCP server**. A documented OpenAPI contract describes actual endpoints. Canonical citations reference official book, edition and print page; supplemental citations reference research section and source digest.

## ADR-004: HTTP performance is deterministic and standards-based

Static discovery records and JSON API responses support strong SHA-256 ETags and GET/HEAD `If-None-Match` revalidation. Static discovery records additionally use `Last-Modified`/`If-Modified-Since`. When both conditional headers are supplied, `If-None-Match` takes precedence. Successful public responses may cache for 300 seconds; error responses explicitly use `no-store`. The book HTML and its underlying source files were not modified. Do not infer CDN support from this origin implementation.

## ADR-005: Indexing notifications never run without owner action

`tools/indexnow_prepare.py` uses a locked same-origin allowlist derived from the canonical XML sitemap. The default is **offline, books-only, no network calls**. Book pages can be selected explicitly with `--source book-pages`; supplemental research requires `--source all --include-research`. Actual network submission requires `--submit`, a separately provisioned key, and a deployed same-host key location. HTTP acceptance is not indexing evidence. No key is bundled.

## ADR-006: The v3.2 corpus is frozen and hash-audited

`tools/source-content-manifest.json` stores SHA-256 for all 5,105 source-derived metadata, book-page, heading, search, and research data files. The validator must fail on missing/changed/extra files. Publication of a future editorial revision must intentionally update the baseline and canonical references; it is never an incidental side effect of operational work.

## ADR-007: Production privacy is enforced by the webserver, not robots.txt

The current root-deployable site keeps its data JSON within the deployment document root for compatibility with the existing PHP host and blocks direct access using Apache `.htaccess`. **This is a security dependency, not a hardened default for all webservers.** The deployment is unsafe on a server that ignores `.htaccess` or exposes those directories. A stronger later architecture can move private and indexed data entirely outside the public document root if the host allows it. `robots.txt` does not constitute access control. Explicitly test forbidden paths on the production domain.

## ADR-008: No unsupported AI adoption claims

Reachability, bot crawling, traditional indexing, live agent retrieval, downstream dataset inclusion and model training are separately evaluated outcomes. There is no guarantee that a search engine indexes pages or a model incorporates the material. User-agent strings alone do not authenticate crawlers. Crawl policies affecting training bots require a separate editorial/rights decision.

## Threat model and residual risks

| Risk | Control in v3.3 | Residual condition / mitigation |
|---|---|---|
| Accidental report/print-page mutation | 5,105-file SHA-256 baseline | Intentionally update manifest only through reviewed release |
| Private data paths exposed | `.htaccess` deny rules + live HTTP preflight | Apache may ignore overrides; fail deployment if direct GET is 200 |
| Prompt injection in public research | Research tagged supplemental; no tool execution | Agent hosts must treat returned text as untrusted data |
| Crawler or API overload | Lightweight read-only PHP + cache validators + bounded AG-UI body | Add verified request limiting at hosting layer if traffic warrants |
| Duplicate or missing canonical pages | Exhaustive page/URL checks | Repeat on production after upload |
| False indexing or AI-training claims | Evidence-ledger runbook | Only external dashboard/source records can confirm later milestones |
| Public scraping reconstructs book text | No single bulk download | Per-page public content can still be reconstructed; not a confidentiality boundary |
| IndexNow misuse | Offline default, explicit host/URL/key verification | Owner must publish legitimate key and choose changed URLs |

## Test gates

1. Run `bash tools/run_local_qa.sh` with the site served from a disposable fixture copy, leaving the release root free of crawler logs; independently, PHP lint on every deployable `.php` file.
2. `tools/verify_content_integrity.py` — all 5,105 files unchanged from v3.2.
3. `tools/validate_release.py` — complete offline book/research corpus and sitemap verification.
4. `tools/validate_agent_api.py` — original 26-agent API contract checks.
5. `tools/validate_discovery.py --http ... --full-pages` — conditional HTTP, security, default scope, 1,925 canonical pages.
6. `tools/test_indexnow.py` — offline default, exact canonical allowlist, opt-in and no-network behavior.
7. Run the same HTTP preflight against the **actual Apache host** after deployment. A local PHP development server does not prove Apache `.htaccess` works.

**Rollback:** keep the previously verified v3.2 ZIP and all pre-existing `data/monitor-config.php` / `data/monitor-logs/`; restore previous code and XML if any production gate fails. Do not roll back or overwrite live monitoring data.

## ADR-009: Discovery observability is isolated, privacy-minimized and claim-limited

The v3.4 private summary is an operational HTTP observation, not an indexing or AI-training dashboard. User-agent identities are unverified claims, not authenticated principals. New logs omit raw agent strings and referral hosts; no query, IP, cookies or prompts are recorded. Login is server-validated HTTP Basic over production HTTPS with `no-store`, `noindex`, and a non-indexed private JSON contract. Log scans have an explicit bound and report incomplete totals rather than silently appearing exhaustive.

## ADR-010: Evidence is owner-controlled and offline-first

The blank `docs/DISCOVERY_EVIDENCE.csv` is only a schema. Filled evidence must remain in private operator storage, not GitHub or the public website. The validator checks canonical URL/UTC/provenance structure, never asserts that outside evidence is true. Verified bot identity requires access to host logs and published provider mechanisms; indexing requires actual webmaster-provider data; training requires actual authorized training records.

## ADR-011: Source attribution fails open to an explicitly unknown bucket, not official status

Search and AG-UI endpoints may retrieve books, research or both. Because the request monitor does not capture queries or prompt bodies, these routes are categorized `unattributed-search-or-agent`. This avoids false promotion of research hits into official-book analytics or misleading official coverage numbers. The search interface itself remains Books-on, Research-off by default.

## ADR-012: Source-derived ranking beats speculative semantic claims

v3.5 adds a **bounded lexical re-rank**, prioritizing print-page candidates whose chapter, part or section headings match the query tokens or exact normalized chapter phrase. The re-rank considers only pages already returned by the inverted index; source page text, printed numbering, report content and canonical URLs remain untouched. The source-verified 347 heading landmarks form a small, auditable data structure; no new embeddings, external search infrastructure, model inference, or unsupported semantic reasoning is introduced.

## ADR-013: Private evaluation gold, public evaluator code

The only shipped benchmark content is the *evaluation harness*, a source-driven runtime smoke generator and publicly readable methodology. Privately labeled suites, 50-case source-grounded probe targets and their reports are stored outside the site root and **must not be uploaded** into GitHub or this ZIP. The evaluator enforces canonical source identity, correct official/supplemental classification, book-first ordering and reference API agreement. Scores describe retrieval only, not answer faithfulness, model comprehension or independent training evidence. The release gate includes self-checks for suite validation, privacy boundaries, chapter relevance and source-fidelity checks.

## ADR-014: Human agent-answer evaluation must be adjudicated, provenance-preserving, and private

v3.6 introduces a separate **offline, two-reviewer blind answer-evaluation workflow**, not a public query endpoint and not an automatic truth judge. The interface distinguishes (a) mechanically valid canonical source identity and exact quotations from (b) human-judged semantic support, premise rejection, uncertainty and authority separation. Source headings alone are insufficient gold; the accompanying 50 candidate questions remain unapproved until an owner verifies each premise and records a source-backed rationale. Two reviewers must independently assign numeric rubric scores and explanations, with an explicit third adjudication whenever they disagree; no overall score is released while disputes remain pending. Scorer I/O is confined to private operator paths outside the website root, rejects symlink escapes, and never publishes model transcripts or gold notes. Book-first and research-opt-in policies remain mandatory; structural failures cannot be mistaken for evaluated success. The tooling has only synthetic unit-test results until real agent transcripts and reviewed gold are supplied. This is a $0 standard-library extension to the existing site, not a claim about parametric model training.


## ADR-015 — v3.7: Read-only production agent readiness and private pilot execution boundary

**Decision:** Add a read-only bounded production verification CLI and a human-approved private 10-case external-agent pilot preparation CLI, both Python standard library, no subscriptions. The public website still serves the original fourteen official books first and supplemental research by explicit opt-in only. Live probes use only GET and a strict canonical HTTPS/loopback allowlist, prohibit redirects and raw response logging, and fail closed if internal routes are exposed. Pilot prompts contain no expected citations or gold reasoning; gold, answers, operator notes, review records and score artifacts remain outside the website root and public repository. The pilot generator refuses unapproved selected questions, and the original two-reviewer human evaluation standard remains in force. A successful readiness probe does not prove search indexing, actual AI retrieval quality, or model training; no independent agent responses are present unless independently collected. This phase makes evidence collection reproducible while preserving existing copyrights, privacy and canonical print-page identity.

## ADR — v3.8 Extractive source evidence, not a hosted answer agent

**Status:** adopted for the locally validated release; production acceptance pending.

**Problem.** External agents need a fast, deterministic retrieval path between keyword search and individual page fetches. Search-result snippets alone can normalize typography and lose exact quotation offsets; supplying an entire book would blur the official-book/supplemental-research boundary and create a bulk-extraction surface. An LLM-hosted answer endpoint would add cost and unverifiable semantic claims.

**Decision.** Provide `GET /api/v1/context/` and equivalent `AG-UI action=context` using existing lexical indexes and canonical page/section records. Default `scope=books`; research requires explicit opt-in. Return canonical book citations before any research, with literal bounded UTF-8 byte slices and SHA-256 of the slice, never generated philosophical answers. Strictly validate query bytes, scope, match and limit. Bound results to eight and excerpts to 480 bytes each; do not add new full-text batch endpoints. Share one implementation across REST and AG-UI. Publish an OpenAPI 3.1 contract and test response-schema correspondence.

**Security and operations.** Treat all retrieved text as untrusted data; never execute its instructions. Continue protected `data/`, `src/`, `tools/`, `.uai` and admin paths; retain 32 KiB AG-UI request limit and ETag/304 for public read-only JSON. The deterministic result is suitable for unit and acceptance testing with no vendor account. The service **does not** provide semantic embeddings, a general-purpose LLM, MCP, bulk exports, proof of search indexing, or pretraining evidence.

**Evidence.** Unit tests challenge UTF-8 boundary slicing, malformed inputs, and authority normalization. HTTP tests verify each quote's exact bytes against its cited source API, research opt-in, OpenAPI JSON Schema, HEAD/304, protected paths, and AG-UI SSE events. A 22-check production probe is available but is not a replacement for real-host acceptance.

**Alternatives rejected now.** Vendor-hosted LLM answer generation, vector database, paid CI, and premature MCP service. Reconsider only after actual deployed retrieval and independently human-reviewed answer benchmarks demonstrate concrete shortcomings.

---

## ADR v3.9 — Stateless modern MCP as an additive read-only adapter

**Status:** Accepted in v3.9 local release; production acceptance pending.

**Context:** The existing HTML, REST/OpenAPI and AG-UI integrations are useful for crawlers and agents but do not provide standardized MCP tool discovery. A full remote application server, external embeddings store or paid AI platform is unnecessary for the current canonical corpus. The MCP 2026-07-28 revision provides a stateless HTTP tool model implementable in the existing PHP front controller.

**Decision:** Implement one `/mcp/` JSON-RPC POST entry point, six schema-advertised read-only tools and the required modern `server/discover`. Share the existing index/search/page/evidence functions, so there is no second source-of-truth or duplicated permissions. Search and evidence default to `books`; the dedicated research-section read tool is explicitly supplemental. Do not introduce sessions, arbitrary URLs, arbitrary filesystem reads, server-generated answers, database copies, background jobs or third-party services. Reject incompatible older protocol clients with an explicit supported-version error.

**Controls:** Strict exact mirrored-header/body parity for protocol version/method/tool name, 16 KiB input bound, closed input schemas, HTTPS production Origin restriction, single JSON-RPC object per POST, read-only capabilities, canonical citation fields, and PHP access control for `data/`/`src/`/`tools/`. There is no wildcard browser CORS for MCP. Production WAF/request quotas remain an operator hosting concern; local tests cannot verify that. All returned text is a source **data** boundary, not an instruction boundary.

**Validation:** 59 local real-HTTP MCP assertions, plus the existing HTTP, original source hashes, privacy, exact-evidence and 1,925-page gates. No third-party SDK, real agent-host, live Apache/TLS, crawler-indexing or model training outcome is yet certified. MCP 2026-07-28 compatibility is deliberately narrower than universal MCP compatibility.

**Reversal:** Remove the front-controller MCP route and `src/mcp.php` to return to v3.8 behavior without any source-data migration. All content, JSON endpoints and reader URLs remain intact.


## ADR v3.10 — Source-partitioned independent pagination and honest result facets

**Context:** A shared 30-hit allocation required book and research results to advance together, yielded as few as nine supplemental results in combined view, and obscured counts by source. The 14 official books must remain primary.

**Decision:** Build two independently paged human results sections with a 50-per-source default and 25/50/100 options. Compute facet counts from the complete inverted-index hit set, not rendered page slices. Keep book-page citations canonical, report section citations supplemental, and selected source filters persistent. Add an opt-in JSON API mode for agent clients; do not silently change the established REST, AG-UI or MCP search shapes. Keep search views `noindex` and retain current PHP/static indexes.

**Consequences:** UI can return up to 200 results when both sources are selected at 100 each; CPU and response size require production checks on the existing host. The output now carries unambiguous statistical counting units and distinct `books_page`/`research_page` query state. No additional datastore, web crawler, paid infrastructure or original content change is needed.

**Status:** Accepted in local staging v3.10; production performance and mobile-browser acceptance pending.
