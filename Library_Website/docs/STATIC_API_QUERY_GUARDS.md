# Query-safe static API metadata delivery — v3.14.8

## Why

The older v3.13 route rules for top-level API metadata, book lists, book metadata, table of contents, and individual research report metadata still served static JSON even when the URL contained query parameters. Query-sensitive research listing and v3.14.5 citation metadata already had empty-query guards. A future API parameter could silently return the query-free default snapshot, even though the PHP endpoint should process that parameter. This release prevents that regression.

## Server behavior

- A canonical, query-free `GET` or `HEAD` of any of the existing 3,719 metadata JSON endpoints is still a prebuilt static file, with web-server ETag and conditional `304` support.
- If the URL has *any* nonempty query string, or if the method is not `GET` or `HEAD`, `.htaccess` does not rewrite metadata to `api-cache/`; `index.php` handles it.
- PHP built-in development routing (`router.php`) implements the identical rule, so the complete suite tests the same compatibility contract.
- Canonical reading HTML remains pre-rendered for query-free GET/HEAD. Citation JSON remains text-free metadata; page-text APIs, search, MCP and AG-UI remain dynamic.
- Source edition, rights, author attribution, book-primary and supplemental-research status, manuscript text, and protected private Runic files are unchanged.

## Validation

`python3 tools/test_static_delivery.py --http http://127.0.0.1:PORT --all` now checks two query variants for each of six historical route families, in addition to exhaustive canonical static catalog delivery and citation samples. Run the same test with `--strict-web-server` against real Apache or LiteSpeed to validate the actual rewrite behavior and PHP bypass. Keep the v3.14.7 HTML hash-integrity safeguards and validate the static inventory before deployment.

This is local verification, not evidence of a deployed LiteSpeed release, search indexing, or parametric AI model training.
