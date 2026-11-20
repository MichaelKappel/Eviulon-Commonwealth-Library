# v3.14.9 source-grounded lexical topic directory

## Purpose and limits

The 20-topic source directory is a deterministic lexical navigation layer across the **14 official authored books** (primary) and 210 supplemental, unverified research reports (secondary). It does **not** assert independent corroboration, promotion to official doctrine, model training, or search-engine indexing. The research portion is consistently labeled unverified.

- Canonical static HTML: `/topics/` and 20 `/topics/{slug}/` pages.
- Bounded, text-containing source evidence: `/ai/concepts.json` **site-root only** (never in public GitHub). Each entry has a canonical source link, first-match code-point offsets in the published JSON record's `text` field, exact matched case, and SHA-256 of the public section/page JSON. Evidence snippets do not imply fact verification.
- The HTML topic pages, `ai/concepts.json` and the original print/research JSON data are excluded from the public GitHub source mirror. GitHub retains only source code, tests and documentation.
- Phrases are selected as fixed exact expressions and searched by Unicode Python regular expression `re.IGNORECASE`, with word-boundary guards. This is lexical matching, not a verified semantic taxonomy or independent citation network.
- All 3,478 source units are scanned to compute per-topic totals; up to 12 book samples and 7 supplemental samples per topic are published in bounded context. Full-text bulk dataset exports are not introduced.
- Static canonical GET/HEAD requires an empty query string. Query variants are handled by PHP. Direct `/topics-cache/` storage URLs are denied.

## Verification

`python3 tools/build_topics.py --write` rebuilds the JSON, sitemap and pages from the exact immutable source records; `--check` validates all source hashes, term offsets/snippets, 21 page digests, and dynamic render parity. `python3 tools/test_topics.py --http ...` tests canonical HTTP response, structured metadata, cache validators, first-match provenance, query fallbacks, and cache privacy.

This is partial restoration of **topic discovery capability** once lost with the historical v3.18 artifact. It is not a recovery or replacement of that original v3.18 release, whose exact code and measurements are unavailable. No live deployment is claimed.
