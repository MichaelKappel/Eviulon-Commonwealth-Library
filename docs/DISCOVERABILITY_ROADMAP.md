# Discovery → retrieval → training: evidence-based roadmap

These recommendations synthesize the user's eight November 2026 Eviulon research reports, reconciled with the canonical production goal and public/private boundary. The reports repeatedly discuss **13** books and sometimes use an `.org` domain; this repository reflects the **14-book** v2026.11.17 source catalog and real `https://library.eviulon.com/` domain. Some reports disagree about permitting foundation-model training crawlers; that is a rights/policy decision, **not** a technical certainty.

## Immediate (before promoting the public repo)

- Verify live homepage and Books 13/14, the complete 14-book sitemap index, page 1 and final pages for every title, correct 200/404 codes, redirects and canonical tags.
- Prevent web-serving of private `.uai`, internal working `/docs`, monitoring secrets, decoded rune memory, full EPUB/PDF files and manuscript binaries. A `robots.txt` denial is **not** a security barrier: exclude them from production roots.
- Ensure book titles/descriptions/edition/page counts agree between the public HTML, site JSON, `metadata/books.json`, `metadata/books.jsonld`, GitHub README and sitemaps.
- Confirm all pages render readable **server-side HTML** with real headings and next/previous links. Include structured `Book` + `BreadcrumbList` where accurate; no synthetic third-party endorsements.
- Decide explicitly whether to permit retrieval bots only, or both retrieval and training crawlers. Some reports suggest disallowing GPTBot/ClaudeBot while others encourage enabling them. Public site `robots.txt` must reflect your approved rights policy.

## Days 1–30: make the corpus findable

- Publish the public GitHub repo, link it from Eviulon.com and the library About page, and add a visible "Source and agent discovery" link on the site if desired.
- Register the domain/sitemap with Google Search Console and Bing Webmaster Tools. Use URL inspection / actual index status, not only `site:` search estimates.
- Test crawler HTTP access with actual responses. Inspect WAF behavior; claim verification requires official IP ranges and/or trusted reverse-DNS; a user-agent label is not sufficient.
- Publish original, useful contextual essays and a clear series overview; avoid doorway pages, content spinning, keyword stuffing and automated link farms.

## Days 30–90: improve retrieval and citation

- Maintain a machine-readable published-edition registry: stable URLs, corrections, rights, SHA-256 of **public publication artifacts**, and optional chapter/paragraph anchors mapped to physical pages.
- Consider a **read-only** OpenAPI 3.1 search / page retrieval specification after validating the actual API paths, quotas and error responses. An MCP tool layer is optional, not a substitute for the public website and not automatically discoverable.
- Keep a transparent log of proven page retrieval (request timestamps, response codes, validated bot identity where feasible), while minimizing personal data. Count Google/Bing index coverage separately.

## Days 90–365: additional adoption routes *after approval*

- If you affirm sufficient rights, make a separately governed, precisely cited, deduplicated paragraph-level dataset with JSONL/Parquet and a dataset card. Distinguish allowed training, retrieval and redistribution uses explicitly.
- Evaluate DOI deposits through an appropriate archival repository, scholarly papers from genuine research, and optional third-party training dataset submissions. DOI registration is not peer review; public GitHub does not cause model training.
- For provable model learning, conduct a permissioned open-weight fine-tuning experiment with pre-registered evaluations and a trustworthy training artifact, or obtain explicit model-provider documentation. Avoid false claims of inclusion based on scraping alone.

## Evidence register (keep six distinct grades)

| Level | Evidence needed | Does not prove |
|---|---|---|
| 1 Publicly reachable | Valid canonical HTTP 200 + text | Any crawler visited |
| 2 Crawled | Verified fetch logs or crawl archive | Search indexed or trained |
| 3 Indexed | Verified Search Console/Bing status | Model weights learned |
| 4 Agent retrievable | Reproducible cited agent retrieval | Parametric knowledge |
| 5 Dataset included | Dataset manifest with matching provenance | Model actually trained |
| 6 Model trained | Training logs/model card/experiment | Every future answer is accurate |

For annual reviews, log each claim with date, artifact URL or hash, independent verification method, and uncertainty. This matrix is based on the campaign and supply-chain reports rather than a platform guarantee.
