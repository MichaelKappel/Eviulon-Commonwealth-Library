# Direct Research Browsing — v3.14

The fourteen official books retain the main library position and remain the default search scope. The 210 Eviulon/Evulgare research reports are supplemental references, not approved Eviulon doctrine.

## Discoverable human routes

- The site-wide **Research** primary-navigation link points to `/research/` on every server-rendered page, including book pages and reports.
- The homepage puts official Books first and also provides an understated research-directory link near the hero and a full secondary browse section below the book catalog and canon explanation.
- Homepage secondary links take visitors directly to `/research/?collection=Eviulon` (90 reports) or `/research/?collection=Evulgare` (120 reports). Both routes are readable without JavaScript.
- `/research/` lists all 210 report landing links; category filtering gives 90 or 120 links, source-provenance disclaimers, and `aria-current="page"` for the selected category. Counts come from the published reports manifest in PHP, not a separate data store.
- Each report landing remains `/research/{group}/{slug}/`, and its section URLs remain `/research/{group}/{slug}/{section}/`. All original canonical URLs are unchanged.
- Footer, sitemap, API catalog and optional Research search remain available.

## Technical/authority constraints

No new database, account, client framework, external API, paid service or monitoring is necessary. These are ordinary HTML anchors, so crawlers can follow the directory and canonical report URLs without executing JavaScript. Server-side source records and indexes are not modified. Research continues to be unchecked by default in search, and MCP/REST/AG-UI behavior is unchanged.

## Local acceptance

Run `python3 tools/test_research_navigation.py --http http://127.0.0.1:PORT --root .` with the release's PHP router running. This verifies navigation and direct browse paths, authoritative counts, per-category visibility, report anchors, supplemental disclaimers, and GET/HEAD reachability of all 210 report landings. The complete regression suite includes this check.

Production LiteSpeed HTML, mobile appearance and public crawler acquisition must still be verified after deployment. Any new release should be rolled back if it breaks source privacy, canonical reading, book-first navigation or report access.
