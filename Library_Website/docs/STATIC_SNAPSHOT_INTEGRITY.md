# Static snapshot build integrity — v3.14.7

## Problem corrected

Earlier v3.14.6 `tools/build_static_html.py --write` resumed cached HTML when its file modified time was newer than the most recently modified source. Copying a changed file while preserving timestamps, restoring source files from a ZIP, or clock skew could permit stale prebuilt HTML to be reused despite changed bytes. The prior `--check` performed a 40-route dynamic parity sample, so a stale page outside the sample could survive an otherwise plausible release inventory. This was a *build-integrity risk*, not evidence that any particular previously shipped page was incorrect.

## New fail-closed rebuild policy

1. Hash the full rendering dependency tree (site version, release ID, PHP templates and application, all original content/metadata under `data/`, and the snapshot builder itself).
2. Reuse an existing HTML page **only when** a complete prior manifest or resumable checkpoint records the *same entire dependency SHA-256* **and** the particular cached file matches its canonical route, recorded byte count, SHA-256, and required HTML structure. Filesystem `mtime` is ignored for acceptance.
3. When input hashes change—even if modification timestamps do not—all 3,702 canonical pages are regenerated from the same PHP renderer. Unrelated documentation changes do not invalidate the rendering inputs.
4. Every 80 completed pages, persist a verified-source checkpoint atomically. Interrupted builds can reuse only verified complete pages from the *same input digest*, re-rendering the rest. Individual HTML writes and the final manifest use atomic rename; incomplete output is never registered as a completed release.
5. Recheck the global dependency digest before publishing the final manifest. If rendering inputs change mid-build, fail instead of releasing mixed-source pages.
6. `--check` fails if a partial-build checkpoint remains, any page SHA/length/route differs, any dependency changed, or the dynamic parity samples differ. The full corpus-wide JSON-LD audit and static HTTP tests remain required.

## Safe release flow

Run from the site root after making **all** release version, data, and runtime changes:

```sh
python3 tools/test_static_html_cache_integrity.py
python3 tools/build_static_html.py --write
php tools/build_api_snapshots.php --write
python3 tools/build_static_delivery_manifest.py --write
python3 tools/build_static_html.py --check
php tools/build_api_snapshots.php --check
python3 tools/build_static_delivery_manifest.py --check
bash tools/run_local_qa.sh
```

The release packaging verifier independently compares all published source content and SHA-256 inventories, confirms identical shared source bytes in GitHub and website, validates 260 private `.uai` records, and checks the three ZIPs. `html-cache/` is excluded from public GitHub except its safe `.htaccess` configuration, because HTML snapshots contain the already-published book and report text.

## Scope / claims

The original 14 official books' 1,925 print pages and 210 *supplemental, unverified* reports' 1,553 sections remain verbatim. Canonical HTML URLs remain indexable; query-bearing reading requests, agent/MCP, search, text retrieval, and two-page spreads remain dynamic. No new bulk-source endpoint or private-memory exposure. Static success in a local Apache test does not mean deployment or production LiteSpeed performance has been verified. Crawlable is not trained; training requires independent evidence.
