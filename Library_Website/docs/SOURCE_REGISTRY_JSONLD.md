# v3.14.10 — Source registry and schema-aware machine discovery

This release adds `/ai/source-registry.jsonld`, a static JSON-LD `Collection` that catalogs exactly 14 official published working paperback books and 210 supplemental, unverified research reports. It is designed for agents and bibliographic harvesters, not as a full-text dataset.

## Sources and authority

- Official book identity, title, author, edition, page count, publication cautions, and original-source SHA-256 come directly from `data/books.json`. These are canonical authored works within a fictional setting, not externally verified political institutions.
- Supplemental report identity, title, report group, report-section count, source SHA-256 as recorded in published metadata, and canonical URL come directly from `data/research/reports.json`. Report content is not independently verified or official Eviulon doctrine. **164/210 original report files remain unmatched in the current private recovery**, though published section records are intact. Do not interpret a listed hash as proof that the lost original file exists.
- The registry only publishes descriptive metadata and canonical page/citation templates; it excludes `text`, `articleBody`, excerpts, PDFs, full manuscript data, private `.uai` memory, private research source files, and implied DOI/license/certification.
- No open license, permission to train, third-party indexing, parametric learning, or peer review is asserted.

## Build and checks

`python3 tools/build_source_registry.py --write` deterministically builds the JSON-LD from exactly the current immutable metadata records. `--check` verifies byte-level parity and source fingerprints. `python3 tools/test_source_registry.py --http HOST` verifies live JSON-LD shape, source consistency, canonical links, HTTP caching, HEAD and POST rejection.

`tools/run_local_qa.sh` includes both checks. `tools/build_static_delivery_manifest.py --check` validates the resource fingerprint and includes it in the public static inventory. The site uses direct Apache/LiteSpeed static delivery for GET/HEAD, no PHP rendering, with a PHP fallback for unsupported methods (405).

The registry is **safe for the public GitHub source mirror** because it carries no copyright-sensitive full-text fields or excerpts. It is also present in the root deployment and private master, byte-identical in all three where shared.

## Version and limits

This is the recovered **v3.14.10** branch, not the lost historical v3.18 artifact. Local QA is not proof of production deployment. Lexical topic discovery and citations remain independent features.
