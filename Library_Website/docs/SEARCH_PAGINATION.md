# Search Result Pagination and Facets — v3.10

## Authority policy

The fourteen Eviulon books are the official authored works, searched by default. The 210 Eviulon and Evulgare research reports are supplemental public-source material, NOT approved doctrine. Research must be explicitly selected on the website or in agent/API scopes. In combined results Books appear first. Search pages remain `noindex,follow` to avoid generating duplicate crawling surfaces.

## Human search (`GET /search/`)

- Default: Books on, Research off; **50 hits per selected source**.
- Selector: 25, 50, or 100 **per source** (not an overall split budget). With both sources selected, a full page can include 100 Books and 100 Research results. Large result pages may load more slowly on shared hosting.
- Independent query parameters: `books_page` and `research_page`. Each defaults to 1. When one source moves, the other stays on its current page. Search form submissions reset both page parameters.
- Stable paging links preserve query, source selection and per-source page size; they target `#book-results` or `#research-results` for keyboard and mobile navigation.
- Requested pages beyond the final populated page are clamped to the last available page; zero-result searches display zero results, not empty spurious pages.
- “Results by book” is a collapsible list of exact counts by each represented volume. Research shows exact section counts for Eviulon vs. Evulgare, unique matched report count, and eight most-matched reports.
- Result sets contain indexed term matches. These numbers do not represent unique mentions, keyword frequency, validated factual assertions, or semantic similarity.

## Read-only JSON search (`GET /api/v1/search/`)

**Legacy (unchanged for REST, AG-UI, MCP compatibility):** `?q=identity&scope=books,research&page=2&limit=20`. Legacy combined paging retains the existing book-first allocation, max 40. This is intentional to prevent a breaking API change.

**Opt-in independent paging:** `?q=identity&scope=books,research&per_page=50&books_page=2&research_page=3`.

When any new parameter `per_page`, `books_page`, or `research_page` is supplied, the response gains `pagination_mode: independent`, `book_pagination`, `research_pagination`, and `breakdown`, while retaining the familiar `book_total`, `research_total`, `book_results`, `research_results`, `results`, source authority labels, canonical URLs, citation text, and research disclaimer. `book_pagination` and `research_pagination` each contain `{page,pages,per_page,from,to,total}`. `breakdown` contains `books_matched`, `by_book` (matching print-page counts), `reports_matched`, `by_research_collection` (matching section counts), and `top_research_reports` (max eight), plus explicit counting-unit descriptions.

The API's existing defaults do not change. Agents only opt into the new mode through explicit query parameters, so v3.9 MCP tools and AG-UI can retain their existing output contract.

## Statistical correctness and performance

Facets are calculated from **all indexed matching source IDs**, before slicing/paging. The sum of `by_book[*].pages` equals `book_total`; the sum of `by_research_collection` counts equals `research_total`. Book match IDs are original print pages, and research match IDs are individual report sections. Ties for top reports are broken by stable source ID; chapter ranking remains unchanged. The feature uses the existing on-disk lexical index and PHP implementation—no database, cloud search service, client JavaScript, or paid subscription is introduced.

## Security and operational acceptance

- Preserve source privacy and `data/`, `src/`, `tools/` Apache direct-access restrictions; avoid deploying to a host that ignores `.htaccess`.
- No source content, page IDs, primary text, private memory, or original research record is modified by v3.10.
- Run `bash tools/run_local_qa.sh` and verify the new independent search tests before deployment.
- After deploying, open `/search/?q=machine&filters=1&scope%5B0%5D=books&scope%5B1%5D=research&per_page=50`; exercise each pager and its anchored navigation. Verify actual production browser rendering, caching, security, and PHP resource usage.
- Roll back to the last successfully deployed version if canonical URLs, authority defaults, direct file protection, book/research indexing, or page navigation regress. Preserve live monitoring configuration and logs.
