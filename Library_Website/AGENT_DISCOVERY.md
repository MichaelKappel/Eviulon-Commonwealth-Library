# Machine and crawler access to the official Eviulon Library

Canonical site: https://library.eviulon.com/

Start with the [public README's fourteen canonical book URLs](../README.md#all-14-books--canonical-deep-links). Standard HTML page URLs are authoritative. Single-page `{slug}/{page}/` routes are citation identities; `/{page}-{page+1}/` spreads are secondary. Follow `rel=canonical` and ordinary links. Javascript is not needed for books.

Extra discovery endpoints (test on the actual domain before assuming available): https://library.eviulon.com/index/ , https://library.eviulon.com/sitemap.xml , https://library.eviulon.com/llms.txt , https://library.eviulon.com/api/v1/books/ , https://library.eviulon.com/ai/knowledge.json . The `/ag-ui/` endpoint is supplemental read-only SSE, not an MCP server, training route or replacement for HTML.

The GitHub tree excludes book-page JSON and search shards on purpose. The private site build holds those for the actual website. No request should be sent to private routes, and all automatic access should honor robots.txt and reasonable crawl rates.
