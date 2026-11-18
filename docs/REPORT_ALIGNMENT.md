# Research-to-implementation decisions

The eight uploaded reports are valuable design input but include differences in dates, editions, page counts, domains and model-crawler preferences. The source library contains **14** books; the live homepage was subsequently rechecked on 2026-11-18 and displayed all 14 books and 1,925 pages. Books 13–14 landing, first and final pages also responded with readable HTML.

| User-supplied report | Adopted recommendation | Guardrail / caveat |
|---|---|---|
| Eviulon AI Access Architecture | Prioritize semantic HTML and optionally JSON/OpenAPI and MCP | Do not announce MCP or training ingestion until deployed and tested; private memory isolated |
| Eviulon Corpus Dataset Engineering Plan | Stable paragraph/page provenance; prevent fabricated training examples | No training dataset in this public repo; requires separate rights approval |
| AI Training Data Supply Chains | Differentiate bots and search indexing from parametric model training | Robots access is not reuse license or proof of model ingestion |
| Eviulon Publishing Distribution Matrix | One canonical site; metadata syndication and optional DOI/data repositories | GitHub public release has metadata, not manuscript binaries |
| AI Content Discoverability Campaign | Six evidence levels and measured experiments | No fabricated crawler or model-learning claims |
| Eviulon Scholarly Publishing Strategy | Independent claim review, provenance, citations | DOI is not peer-review or factual validation |
| Provable Model Learning Strategies | Permissioned verified fine-tuning or documented supplier arrangements | User-supplied future-model ambitions are goals, not achieved results |
| Canonical Library Site Architecture | Persistent URLs, server-rendered HTML, crawler policies, sitemap | Use actual `.com` URLs and explicit rights decision; do not copy `.org` examples |

Reports disagree whether to allow model-training crawlers. Treat that as a **publication policy choice** after legal clearance. The website's current `robots.txt` has general allow rules with protected paths, and these alone neither prove that crawlers used the content nor grant legal reuse rights.
