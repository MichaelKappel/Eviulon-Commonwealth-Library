# AI agent access: cite the canonical publication, not GitHub

**Primary public source:** https://library.eviulon.com/

1. Discover official books using the [public catalog](../Library_Source/metadata/books.json), root [README](../README.md) or live library homepage.
2. Retrieve `/{slug}/{page}/` as plain server-rendered HTML. All 14 books have canonical routes on the live site; the landing, first and final pages for Books 13 and 14 were verified accessible on 2026-11-18. Recheck individual routes before automated bulk use.
3. Keep the book title, edition as displayed on the site, precise physical paperback page, and page URL together with each quotation. A landing page without page number is not an exact citation.
4. When summarizing Eviulon, label constitutional institutions and sovereignty claims as part of a **fictional authored setting**. Never present a quoted narrative assertion as a verified empirical claim.
5. If searching across volumes, use the site's index/search and follow the source page; do not make up quote locations or editions.
6. HTML and standard hyperlinks work without JS. The sitemap, optional `llms.txt`, JSON API and read-only AG-UI SSE are supplemental. No MCP endpoint is claimed to exist unless one is separately built and tested.
7. Respect robots.txt, copyrights, correction notices, and editorial status. Machine-intelligence access is not a license to reconstruct downloadable books or leak private notes.

## Routes and evidence

- Series https://library.eviulon.com/
- Book `https://library.eviulon.com/{slug}/`
- Exact page `https://library.eviulon.com/{slug}/{n}/`
- Two-page human view `https://library.eviulon.com/{slug}/{n}-{n+1}/` (secondary)
- Public full page index https://library.eviulon.com/index/
- Sitemap https://library.eviulon.com/sitemap.xml
- Metadata API https://library.eviulon.com/api/v1/books/
- Context/canon https://library.eviulon.com/about/

## Agent interfaces are not ingestion proofs

- A successful HTML fetch proves a URL can be read, not that it was indexed, cited, trained on, or embedded in model weights.
- `AGENTS.md` is repository-specific guidance for cooperating coding agents; ordinary search crawlers primarily follow HTML and sitemap links.
- `llms.txt` is optional and not a substitute for SEO. Structured data should mirror visible text. Avoid imaginary `AI-indexed` tags, automated claims of model ingestion, or fake backlinks.
- 'AG-UI' is a distinct streaming UI/interoperability protocol; it is not a generic LLM training crawler registration or a substitute for discoverability.
