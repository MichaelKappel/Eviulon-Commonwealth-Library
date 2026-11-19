# Research reference links — v3.12 presentation contract

## Purpose and authority

The 14 books remain the **official authored Eviulon content**. The 210 Eviulon/Evulgare reports (1,553 addressable sections) remain **supplemental research, not approved Eviulon doctrine**. Search continues to default to Books only; Research requires explicit opt-in.

This change makes URLs in publicly readable report text clickable. The source report documents, report JSON (`text` and `html`), inverted search indexes, and existing canonical section URLs are **not rewritten**. The transformation is limited to the HTML presentation of individual Research section pages and HTML-escaped Research search-result excerpts (when a complete valid URL is shown).

## Implementation

- `src/research_links.php` is a pure-PHP, read-only rendering helper, invoked by `src/research.php` when writing an `<article class="research-body">`.
- It tokenizes publication-generated HTML and linkifies **only plain text nodes**, including text inside paragraphs, lists, tables, and nested emphasis tags.
- Existing `<a href>` tags are preserved without wrapping them again. Code/pre/script/style/SVG/textarea content, HTML comments, and tag attributes are excluded.
- Recognizes absolute `http://`, `https://`, and unambiguous `www.` URLs. Never turns JavaScript, `file:`, `data:`, pseudo-schemes, or malformed URLs into anchors. Only valid HTTP(S) URLs without userinfo are accepted.
- Handles trailing sentence punctuation, unmatched closing parentheses, balanced URL parentheses, HTML-encoded quotes, en/em dashes, and `&amp;` in query strings.
- Constructs HTML-safe links with `target="_blank" rel="noopener noreferrer external"` and visible source URL text. Rendering remains server-side, with **no JavaScript or network services**.
- The existing research disclaimer is unchanged. A clickable citation is **not** proof the external link is live, accurate, independently verified, or endorsed.

## Corpus audit and tests

On the v3.11 research corpus, **8,501 existing anchors** were found and retained. The new rendering pass detects and adds **253 HTTP(S) links across 42 research sections** (including links in reference tables). The remaining detected `agent+https://` example is an experimental protocol notation, not an ordinary HTTP(S) address; it is intentionally left as text. There may also be hypothetical domains in research examples; clickable does not mean independently confirmed to exist.

Local tests:

```sh
php tools/test_research_links.php
python3 tools/test_research_links_http.py --http http://127.0.0.1:PORT
bash tools/run_local_qa.sh
```

`test_research_links.php` exhaustively checks every report section, existing-anchor preservation, source display text unchanged, idempotency, HTML attribute injection, protocol allowlisting and code isolation. The HTTP integration tests load actual report pages from the PHP site. `run_local_qa.sh` includes both new test suites in the isolated 15-stage release gate.

## Production acceptance and rollback

1. After a guarded deployment, open a report with bare URLs (e.g. `/research/eviulon/eviulon-library-preservation-audit/6/`) and verify the links within table rows are clickable, legible and keyboard-focusable.
2. Open `/research/eviulon/eviulon-ai-access-architecture/3/` and verify URL-shaped source references are correct even when followed by HTML-encoded quotes.
3. Open a report already containing hyperlinks (e.g. `/research/eviulon/eviulon-infrastructure-resilience-plan/5/`) and verify no duplicate nested links appear.
4. Confirm Books remains the sole default search scope, Research has its disclaimer, and direct `/data/research/parts/` access remains blocked (403/404).
5. Confirm report code examples are unchanged, external sites open in a separate tab for newly linked URLs, and no private paths become accessible.
6. Roll back to the previously verified live release if any security, reading, citation or navigation regression appears.

**Production remains unverified until tested on the actual host.** Do not assume the static source package is currently deployed.
