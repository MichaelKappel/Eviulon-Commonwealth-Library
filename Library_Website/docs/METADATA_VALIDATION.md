# Eviulon v3.14.2 — complete metadata consistency contract

## Validated corpus

The published canonical sitemap contains 3,708 URLs: 1,925 official print pages, 14 Book landings, 210 supplemental Report landings, 1,553 supplemental report sections, the Research directory, and five ordinary routes. All three source classes are distinct: original official authored Books, source-backed chapter *headings* within book pages, and optional research reports. The original separately recovered v3.15–v3.18 features are NOT part of this patch.

## Schema.org JSON-LD

- `Book` identity: `/<book-slug>/#book` with source-backed title, credited author/publisher and working edition; `Book.hasPart` uses `Chapter` entities at verified `/<book-slug>/<print-page>/#section-{page}-{index}` heading anchors. Do not claim exact ending pages.
- `WebPage` print identity: `/<book>/<page>/#page`, with `mainEntity` a separately identified `CreativeWork` `/<book>/<page>/#print-page`, the original book as `isPartOf`, and exact print-page identifier. `WebPage.pagination` is omitted because it is not a supported domain; two-page spreads remain noindex.
- Research directory: unfiltered `/research/#collection` is a `CollectionPage` with exactly 210 actual `ListItem` report links. `?collection=` views do not assert an invisible complete ItemList and are noindex.
- Supplemental `Report` identity: `/research/<group>/<slug>/#research`, source report ID, explicit unverified status, isPartOf the Research directory, and `hasPart` section links. This is **not** `ScholarlyArticle`, `ClaimReview` or peer-reviewed work.
- Section: `/research/<group>/<slug>/<section>/#section` as `CreativeWork` with `isPartOf` the Report and `WebPage.mainEntity` pointing to the section.
- All pages: one `WebSite` ID, one parseable JSON-LD @graph, distinct IDs, canonicals and Open Graph URL parity, Dublin Core `DC.title`, `DC.language`, `DC.type`, `DC.identifier`.

## Exclusions to avoid invented claims

Do **not** issue fake DOI/ISBN, `datePublished`, `dateModified`, `sameAs`, academic paper `citation_pdf_url`, creative-commons license, formal scholarly review, membership in the world's real legal institutions, modeled facts from fictional institutions, external corroboration or AI-training-completed badges. Do not retroactively substitute reports for the 14 original Books or turn original page headings into reconstructed chapter texts. Preserve manuscript rights and private memory isolation. External scholarly metadata (DataCite, OAI-PMH, Highwire) must wait until appropriate publication/rights evidence exists.

## Reproducible local tests

`python3 tools/test_semantic_metadata.py --root .` checks source inventories and sitemaps. `python3 tools/test_semantic_metadata.py --root . --http http://127.0.0.1:PORT` checks all HTML markup, exact JSON-LD relationships and filtered Research views. This is included in `tools/run_local_qa.sh` alongside the 15-stage source/performance/MCP/security tests. HTML source inspection does not guarantee Google rich-result eligibility, search indexing or downstream model ingestion. Live LiteSpeed deployment and external validator results require separate verification.
