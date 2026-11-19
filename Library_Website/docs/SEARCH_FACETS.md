# Faceted Search Contract — v3.11

## Authority and user-facing defaults

The **14 books** are official authored Eviulon content. The **210 reports** are supplemental Eviulon/Evulgare public-source research and do not define approved Eviulon doctrine. The site's Books checkbox is selected by default and Research is not. Facet selection must never implicitly select Research. In combined search output, Books precede Research. Source data, print-page numbering, and canonical reference URLs remain unchanged.

## Facets and navigation

The human-facing `GET /search/` search form offers two optional refinements:

- `book_filter={slug}`: one of the published 14 official book slugs; it narrows **only Books**.
- `research_collection=eviulon|evulgare`: narrows **only explicitly selected Research** to the chosen research collection.

A user can search all Books, all Research (explicit checkbox), or both. Facets also work independently when both scopes are selected. The selected facet can be changed using either the form or the linked source breakdown. Selected facets and both independent page numbers survive pagination links. Changing a book facet resets `books_page` to 1 while preserving `research_page`; changing a research collection resets `research_page` to 1 while preserving `books_page`. Submitting a new search from the form resets both pages to 1. Clear links remove just one source's refinement. Every page remains server rendered, keyboard navigable, and functional without JavaScript.

The form still defaults to 50 results **per selected source** (25/50/100 supported). Research appears after the Books section and remains explicitly disclaimed. Search pages are `noindex,follow` and excluded from the XML sitemap; facet query URLs do not create additional canonical search-index surfaces.

## API contract

Legacy API calls (no opt-in pagination or facets) retain the existing response shape and shared paging behavior used by REST, AG-UI and MCP clients. Opt-in independent mode is triggered by supplying `per_page`, `books_page`, `research_page`, `book_filter`, or `research_collection`.

Example:

`/api/v1/search/?q=machine&scope=books,research&per_page=50&books_page=2&research_page=3&book_filter=the-inheritance-of-mind&research_collection=evulgare`

The output includes:

- `book_total` and `research_total`: **filtered** matching print pages and research sections, from all hits before slicing into pages.
- `book_pagination` and `research_pagination`: independent, filtered page-window descriptors.
- `filters`: normalized selected facet values.
- `breakdown.by_book` and `breakdown.by_research_collection`: counts of matching items **inside the current filters**, summing to the corresponding filtered total.
- `breakdown.available_by_book`, `available_book_total`, `available_by_research_collection`, `available_research_total`: available facets and **unfiltered original-query** counts for the corresponding source. These allow changing facets without losing the original distribution; these totals do not represent the current visible selection if a filter is active.
- `results`: all Books first, then optional Research, each with its own canonical citation and authority label.

Allowed facet values are checked against canonical book metadata and the two known report collections. Unknown, malformed, nested or array-shaped filters return HTTP 400. Filtering Research without selecting the Research scope does not expose Research. No bulk manuscript or PDF endpoint is introduced.

Counts represent **distinct indexed print pages** or **distinct research report sections** containing matching terms—not total word occurrences, unique claims, semantic similarity, or estimated entity relevance. Research reports and book pages are independent counting units; do not compare the counts as frequencies of one common unit.

## Verification

`python3 tools/test_faceted_search.py --http http://127.0.0.1:PORT` performs 29 black-box tests against a local PHP HTTP server, including scope isolation, filtered/unfiltered total math, independent pagination, facet retention and reset, malformed input, authority metadata and legacy compatibility. The release gate calls this alongside the v3.10 independent pagination regression.

Before production promotion, run `bash tools/run_local_qa.sh`, verify direct `/data/`, `/src/` and `/tools/` access is forbidden under the actual Apache configuration, inspect the search on desktop and mobile, and check server load for 100-results-per-source broad queries. This environment has not independently certified the production server or a third-party agent's behavior.
