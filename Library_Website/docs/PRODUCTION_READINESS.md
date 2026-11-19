# Production Readiness Verification — v3.7

**Status:** Local PHP pass is not production verification. No API keys or paid services needed.

## Operator preflight

1. Back up the live document root and current `data/monitor-config.php`, `data/monitor-logs/`, webserver and TLS settings. Keep the previous v3.6 release for rollback.
2. Deploy the **website ZIP only** to the existing document root; keep the private operator/evaluation ZIP entirely off the public host and public GitHub.
3. Ensure Apache honors `.htaccess`; the canonical book page must return HTTP 200 and a unique `<link rel="canonical">`, while `/data/books.json`, `/src/bootstrap.php`, `/tools/agent_answer_benchmark.py`, `/data/research/reports.json` and `/.uai/...` return 403/404.
4. Run the bounded live preflight with `python3 tools/live_agent_readiness.py --base-url https://library.eviulon.com --report-out /secure/operator/live-check.json`. Do not overwrite prior evidence reports.
5. Manually inspect book reading behavior (portrait one-page, landscape two-page), books-first checkboxes, the research disclaimer, mobile navigation and authenticated crawler admin. Confirm the host's logs and credentials were preserved.
6. If all checks pass, use the free Google Search Console and Bing Webmaster Tools to submit the existing sitemap and record subsequent indexing evidence separately. Never infer model training from successful HTTP checks.

## Checks covered by the script

- HTTPS canonical home and the public agent guide
- robots.txt and 16-child sitemap index
- OpenAPI contract, agent endpoint catalog and 14-book JSON catalog
- books-only default, explicit research opt-in and the user-facing two-checkbox state
- original Book XIII page 1, page-citation API, chapter contents API
- research directory visibly labeled supplemental
- blocked internal source and memory paths; unknown book 404

The script sends **GET only**, limits response size to 1.2 MB, rejects redirects, and restricts production access to `https://library.eviulon.com/` (or a specifically selected local loopback server for testing). Reports contain request paths, status codes and pass/fail details, **not source responses, private questions, search terms entered by readers, auth tokens or agent transcripts**.

## Rollback triggers

Immediately restore the prior release if any private path becomes publicly accessible, the Books-only default changes, the citation permalink contract breaks, any authoritative book content is altered, the research disclaimer disappears, or the site becomes unusable. Investigate at the hosting layer before changing the authored text. **A failed readiness check is an explicit stop, not a partial success.**

## Evidence levels

A readiness PASS demonstrates only sampled public route correctness and access controls. It does not establish real crawler identity, search engine indexing, AG-UI reasoning, independent agent answer faithfulness, dataset inclusion or model training. Those need respectively verified network evidence, webmaster console/index evidence, real agent transcripts, source-grounded blinded human reviews, dataset provenance and training records.

## v3.8 exact source evidence checks

The probe now checks **22** GET-only conditions (up from 20), including Books-only extractive evidence via `/api/v1/context/?q=cognitive+liberty` and explicit research opt-in via `/api/v1/context/?q=machine&scope=books,research`. Verify actual quote bytes separately with the offline/local HTTP suite. Neither check proves accurate model understanding or training.
