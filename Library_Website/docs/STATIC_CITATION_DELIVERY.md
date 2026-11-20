# Static citation delivery and verification — v3.14.5

## Scope and authority

The public REST API already exposes 1,925 official-book citation objects and 1,553 explicitly supplemental research citation objects. Before this release, these immutable-for-release metadata responses needlessly loaded PHP and opened an individual source JSON record. This release precomputes those **same existing objects**, without including the page or section body text. Books are the canonical authored primary corpus; reports are independently supplied supplemental research, **not approved doctrine**.

The canonical URLs remain unchanged:

- Official: `/api/v1/books/{slug}/citations/{page}/` (1,925 records)
- Supplemental: `/api/v1/research/{group}/{slug}/parts/{section}/citation/` (1,553 records)

## Routing and content security

The root `.htaccess` serves a prebuilt file only for `GET`/`HEAD` with an **empty query string** and an existing exact numbered citation path. This avoids changing methods, query behavior or errors. Invalid IDs and other actions still flow to `index.php`. `api-cache/.htaccess` sets MIME type, cache, CORS, delivery indicator and `noindex`; the web server emits native Last-Modified and ETag. `router.php` provides a development-only equivalent.

No bulk export, original book page text, research section body text, private `.uai`, licensed dataset, credentials or gold benchmark is published by this optimization. Individual text APIs remain dynamic and unchanged. In particular, a static citation does **not** verify the truth of the cited text.

## Deterministic build

- `php tools/build_api_snapshots.php --write` regenerates and `--check` compares 3,719 **exact existing PHP output objects**. It also rejects stale citation snapshots.
- `python3 tools/build_static_delivery_manifest.py --write` regenerates and `--check` compares the public 3,758-entry SHA-256 file inventory `/ai/static-delivery.json`.
- The local complete `bash tools/run_local_qa.sh` checks the 5,105 original source file hashes, 3,708 HTML canonical/JSON-LD pages, 97,937 structural assertions, all 15 test stages, and samples canonical citation static HTTP behavior.
- The independent real Apache integration checks GET, ETag, `If-None-Match`/304, HEAD, content type, cache headers, direct delivery without `X-Powered-By`, and dynamic 404/query fallback. 4,079/4,079 assertions passed in local staging.

Production has **not** been changed or benchmarked. No claims are made about AI crawlers, third-party search indexing, or actual model training. If LiteSpeed rewrites differ, revert to the last known-good deployment.
