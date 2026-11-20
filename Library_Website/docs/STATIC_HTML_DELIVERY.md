> **v3.14.7 update:** The static HTML builder now rejects timestamp-only reuse and requires a matching full dependency SHA-256 plus per-page hash verification; interruption recovery uses atomic checkpoints. See [Static snapshot build integrity](STATIC_SNAPSHOT_INTEGRITY.md).

# Static canonical reading HTML — v3.14.6

## Why this release exists

Prior v3.14.5 served 3,719 fixed metadata-only JSON responses without invoking PHP, but **all 1,925 official paperback pages, all 1,553 research sections and their 224 landing pages still invoked PHP** on every visit. These public canonical HTML documents do not depend on a viewer's identity or query parameters. This release pre-renders **3,702 byte-identical HTML responses** from the existing production PHP template and immutable source records:

| Public canonical category | Count | Read-through source |
| --- | ---: | --- |
| Official book landing pages | 14 | `data/books.json`, section indexes |
| Official printed paperback pages | 1,925 | Existing immutable `data/pages/*.json` |
| Supplemental research report landings | 210 | `data/research/reports.json` |
| Supplemental research sections | 1,553 | Existing immutable `data/research/parts/*.json` |
| **Total** | **3,702** | Identical `index.php` output from build time |

The individually addressable canonical public pages still contain their **original published text** and Schema.org JSON-LD, Dublin Core and Open Graph metadata. This is not an approval of supplemental research as official doctrine. Static delivery is not proof of external indexing, AI-model training, peer review, or production deployment.

## Routing, privacy and fallback

- `.htaccess` sends only **GET/HEAD with empty query string and exact canonical URL shapes** to existing prebuilt `html-cache/` files. Direct requests to `/html-cache` are rejected with 403. The **original request URL remains canonical** and must not be replaced with the storage path. No `noindex` header applies to canonical HTML.
- PHP `router.php` supplies a development-test equivalent, also blocking direct storage URLs. A real Apache integration proves direct server delivery without `X-Powered-By`, native ETag and `Last-Modified`, `Cache-Control`, HEAD and conditional `304`.
- `/search/`, `/research/?collection=…`, two-page reading spreads, query-bearing page URLs, padded noncanonical IDs, unknown identifiers, MCP, AG-UI, and source-text JSON APIs remain dynamic. Requests with methods other than GET/HEAD also retain the existing PHP contract.
- **Public GitHub never contains the snapshot `.html` files.** They are already-public readable text and therefore belong only in `ROOT_DEPLOY` and the exact `SITE_ROOT` copy inside `PRIVATE_MASTER`, not in source-code mirrors. Original manuscript PDFs, private `.uai` records, original report Markdown, research reports' mutable source provenance and private `/docs` stay private.
- Static pages bypass opt-in PHP crawler-monitor accounting, just as static JSON does. When traffic measurement is needed, use verified web-server access logs with privacy controls; never silently re-enable per-request PHP locks.

## Deterministic build and release checks

Run in `SITE_ROOT` after setting `RELEASE_ID.txt`, `VERSION.json` and all runtime/application source changes:

```bash
python3 tools/build_static_html.py --write
php tools/build_api_snapshots.php --write
python3 tools/build_static_delivery_manifest.py --write
python3 tools/build_static_html.py --check
php tools/build_api_snapshots.php --check
python3 tools/build_static_delivery_manifest.py --check
bash tools/run_local_qa.sh
```

`--check` validates all 3,702 HTML file SHA-256s, file sizes, expected canonical URL mappings, dependency-tree digest and 40 deterministic PHP re-renders; every canonical HTML response is also examined during the 3,708-page metadata HTTP audit. The public `/ai/static-delivery.json` lists all **7,460** static resources: 3,719 JSON, 3,702 reading HTML, 22 discovery files and 17 assets; its `sha256` entries are hashes, *not* a bulk manuscript download.

The site release verifier must reject any missing/stale snapshot. Building before a template, data, or release-version change is invalid; rebuild and rerun all tests afterward.

The release's full local 15-stage QA and independent Apache HTTP tests are recorded in `RELEASE_CONTROL` inside `PRIVATE_MASTER`. **Live LiteSpeed delivery and latency are unverified until deployment**; site owners must deploy and run production checks separately. Revert by restoring the previous root-deployable ZIP if needed.
