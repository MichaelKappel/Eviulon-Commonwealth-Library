# Public GitHub release QA report — 2026-11-18

- Root README includes canonical book landing and page-1 deep links for **all 14** book records.
- Bibliographic counts validated: **14** book records, **1,925** prepared print-page identities.
- The public web copy contains server-rendered PHP, CSS, cover assets, sitemaps, public metadata and agent entry points only; no `data/pages/` or `data/search/` directories.
- Original private `.uai` memory, full source production manuscripts, PDF/EPUB files, internal documentation, and crawler histories are **not included**.
- Scope-specific agent records in `.uai/` and subdirectory `AGENTS.md` contain **new public-safe information** encoded in reversible Elder Futhark nibbles. Top-level `AGENTS.md` remains plain text for machine discovery.
- Decoder integrity checks pass on all public rune records.
- PHP syntax checks pass on all included PHP files.
- Public privacy/package audit passes.
- ZIP archive integrity passes.
- **Current live site (rechecked 2026-11-18):** homepage shows **14** books and 1,925 print pages; Books 13/14 each have verified landing, first and last page URLs. The XML sitemap was linked from the site but its contents were not independently validated through the inspection tool.
- A full crawler/WAF, Google/Bing indexation, and model training verification requires live server/system access and is NOT claimed by this package.

Root-source presence alone does not make a working website: use the private local hydration/deployment procedure in `Library_Website/README_DEPLOY.md`.
