# v3.14.12 — Source-grounded discovery release attestation

`/ai/discovery-attestation.json` is an immutable-for-release, metadata-only public JSON receipt. It binds the release ID, original public metadata hashes, Schema.org source registry, lexical topic catalog, robots/llms and 17 sitemap documents, and proves exact canonical URL set coverage.

## Explicit evidence boundary

This document proves *local build-package consistency only*. It does not prove that the site is deployed or reachable, a crawler has visited, any page is search-indexed, any independent research claim is true, anyone has granted a bulk-training license, or a model has been trained. It contains no private .uai memory, manuscript PDFs, bulk page text, or model evaluation gold. The 14 authored books are distinguished from the 210 unverified supplemental reports.

## Integrity gates

Build: `python3 tools/build_discovery_attestation.py --write` after rebuilding registry, topic cache and canonical HTML. Check: `python3 tools/build_discovery_attestation.py --check` and `python3 tools/test_discovery_attestation.py`. Each check compares the complete 3,702 registry/HTML canonical reading URLs, all 21 topic URLs, all 17 sitemap child documents, the 3,729 unique sitemap URLs, and exactly six remaining navigation URLs. Incomplete, duplicate, unexpected, or noncanonical paths fail. Six independent mutation tests ensure the gate rejects missing/duplicate/altered URLs. The attestation is included in `/ai/static-delivery.json` and served by Apache/LiteSpeed without PHP.

## Live deployment check

`python3 tools/audit_live_discovery.py --base-url https://library.eviulon.com --expected-release <release-id>` is a read-only deployment audit. It checks *actual remote bytes* for the registry, attestation, sitemap index, robots and llms against the attestation fingerprints, then samples page identities. Run only once DNS and deployment are available; an unreachable site is **unverified**, not evidence of an indexing or training outcome. No external corpus deposits, sharing, training, IndexNow submissions, or permissions are initiated.

## Release workflow

All three synchronized versioned archives (private master, root website, public GitHub project) and SHA-256 checksums are retained. Each completed release is automatically saved to the user's private Dropbox release directory. Large ZIPs may be stored as separately verified, ordered binary parts with reconstruction instructions. No private memory is published in the public package.
