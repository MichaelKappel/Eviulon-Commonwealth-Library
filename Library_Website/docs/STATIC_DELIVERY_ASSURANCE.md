# Static delivery assurance (v3.14.4)

## What is and is not static

The 241 prebuilt JSON API catalog/metadata responses, 17 XML sitemaps, five other discovery files and 17 visual/reader assets are served by the web server without starting PHP. The public `ai/static-delivery.json` is itself a static, source-fingerprinted inventory of **280** public files. It does not publish the book texts or supplemental report section bodies. The 1,925 print pages, 1,553 research sections, interactive search, MCP and AG-UI remain dynamic, with the exact source-record authorization boundaries preserved.

## Enforced checks

- `php tools/build_api_snapshots.php --check`: regenerated PHP payload hashes equal the 241 on-disk immutable-for-release catalog responses.
- `python3 tools/build_static_delivery_manifest.py --check`: file existence, route inventory, byte counts and SHA-256 of all 280 published static resources.
- `python3 tools/test_static_delivery.py --http http://127.0.0.1:PORT --all --strict-web-server`: real Apache/LiteSpeed HTTP checks (no PHP) for direct delivery, exact bytes, ETag/Last-Modified, cache semantics, 304, HEAD, source isolation and dynamic fallback. The ordinary PHP development server cannot prove Apache rewrite behavior.
- `bash tools/run_local_qa.sh`: complete 15-stage regression including the static manifest and all 241 API metadata endpoints (development-server semantic behavior, with separate strict Apache run).

Deploy `api-cache/`, `assets/`, `ai/static-delivery.json`, all 17 sitemaps, root `.htaccess` and `assets/.htaccess` with the same ZIP. Do not deploy an older static snapshot tree with newer metadata. The LiteSpeed host must honor `.htaccess` rewrites; verify via `curl -sSI https://library.eviulon.com/api/v1/books/` and require `X-Eviulon-Delivery: prebuilt-static-json` and ETag. Revalidate with `curl -sSI https://library.eviulon.com/ai/static-delivery.json`. The deployment may be rejected/rolled back if these checks do not pass. Live speed improvements were not measured in this local release.

No private `.uai` source, original manuscript PDFs, bulk text export, invented source status, crawler ingestion or LLM training claim is introduced.
