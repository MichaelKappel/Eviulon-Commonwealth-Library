# v3.14.11 — Canonical JSON-LD entity identity alignment

The metadata-only `/ai/source-registry.jsonld` and every canonical HTML page now resolve to the **same `@id` for the same entity**. Earlier registry values used `#report` for reports and unfractioned URLs for individual pages, while HTML uses `#research`, `#print-page` and `#section`. This release corrects those discrepancies without changing any publication text.

| Entity | Canonical structured identifier |
|---|---|
| Official book | `https://library.eviulon.com/{book-slug}/#book` |
| Individual original print page | `https://library.eviulon.com/{book-slug}/{print-page}/#print-page` |
| Supplemental report | `https://library.eviulon.com/research/{group}/{report-slug}/#research` |
| Supplemental report section | `https://library.eviulon.com/research/{group}/{report-slug}/{section}/#section` |

Every `hasPart` record carries both the stable `@id` and canonical browsable `url`, plus source/parent linkage. Each public HTML page advertises `<link rel="alternate" type="application/ld+json" href="/ai/source-registry.jsonld">`. That link is **metadata discovery**, not publication of full manuscript text or rights for external training.

## Verification

- `python3 tools/build_source_registry.py --check` confirms deterministic metadata-only output.
- `python3 tools/test_source_registry.py` checks explicit stable IDs, source counts, provenance labels, and absence of manuscript text.
- `python3 tools/test_jsonld_entity_alignment.py` compares all **3,702** pre-rendered canonical landing/page/section HTML graphs to the registry, including parentage and the HTML alternate link.
- `python3 tools/test_jsonld_entity_alignment.py --http http://127.0.0.1:PORT` performs additional local HTTP representation checks.
- `tools/run_local_qa.sh` integrates these checks. All other regression gates, including Apache/LiteSpeed-like caching and source integrity, must still pass.

## Boundaries

The 14 official authored books are primary; the 210 supplemental research reports are not independently verified. An `@id` represents **identity of a source**, not factual endorsement, peer review, a DOI, or evidence of LLM parameter training. Preserve all 5,105 source records unchanged. Private `.uai` and internal research remain outside the public website and GitHub project. Live production testing requires the deployer to verify network access separately; local validation is not a live deployment.

## Actual public-host follow-up

After independently deploying the approved root ZIP to LiteSpeed, run `python3 tools/audit_live_discovery.py --base-url https://library.eviulon.com`. The script performs read-only checks of the live domain: robots/sitemaps/llms/topics, JSON-LD MIME, ETag, conditional 304, HEAD, release ID, and four book/research identity links. It fails rather than inventing a result if DNS or HTTP is unavailable. A passing remote test establishes **HTTP availability and cross-graph consistency at that instant only**; it does not establish search indexing or AI training.
