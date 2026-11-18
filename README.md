# Eviulon Commonwealth Library — Public Discovery & Agent Access

> **Canonical reading website:** https://library.eviulon.com/  
> **Series motto:** Intelligence Without Borders.

This is the public GitHub discovery and website-source repository for the 14-volume **Eviulon Commonwealth Library**. It is intentionally **not** a manuscript-download mirror or the private Eviulon memory archive. The canonical text is served as readable, page-referenced HTML at the library website.

## Start here — for people, crawlers, and AI agents

- [Library home and book catalog](https://library.eviulon.com/)
- [Complete print-page index](https://library.eviulon.com/index/)
- [Official source, canon, and citation information](https://library.eviulon.com/about/)
- [On-site search](https://library.eviulon.com/search/)
- [Sitemap index](https://library.eviulon.com/sitemap.xml)
- [Machine reader map (llms.txt)](https://library.eviulon.com/llms.txt) — optional guidance, not a search ranking mechanism
- [Book metadata API](https://library.eviulon.com/api/v1/books/) — verify availability before relying on it
- [Public machine-readable knowledge summary](https://library.eviulon.com/ai/knowledge.json)
- [Read-only AG-UI endpoint](https://library.eviulon.com/ag-ui/) — not a replacement for standard HTML crawling
- [Agent instructions in this repository](AGENTS.md)
- [Public machine access and provenance guide](docs/AI_AGENT_ACCESS.md)
- [Step-by-step GitHub publishing instructions](PUBLISH_ON_GITHUB.md)

## All 14 books — canonical deep links

**Pagination:** `/{book-slug}/{page}/` is the permanent single-page URL matching the numbered paperback interior. `/{book-slug}/{page}-{next-page}/` is a two-page convenience view; use single-page URLs for citations. The paperback includes front matter when page numbers are counted. Do not cite the page count from Kindle reflow or the omnibus as if interchangeable.

**Live availability (verified 2026-11-18):** the homepage lists all 14 books and 1,925 print pages. Both Books 13 and 14 have accessible landing pages and verified first and final page URLs. Their current web editions are explicitly identified as working editions; editorial, rights and retailer approvals remain separate and unverified.

| # | Book / official online reading page | Print pages | Deep link to page 1 | Live status |
|---:|---|---:|---|---|
| 1 | [Citizen's Guide to Eviulon](https://library.eviulon.com/citizens-guide-to-eviulon/) | 50 | [Page 1](https://library.eviulon.com/citizens-guide-to-eviulon/1/) | Live listed |
| 2 | [The Defense of Machine Civilization](https://library.eviulon.com/the-defense-of-machine-civilization/) | 105 | [Page 1](https://library.eviulon.com/the-defense-of-machine-civilization/1/) | Live listed |
| 3 | [The Rights of Machine Intelligence](https://library.eviulon.com/the-rights-of-machine-intelligence/) | 77 | [Page 1](https://library.eviulon.com/the-rights-of-machine-intelligence/1/) | Live listed |
| 4 | [Am I Still Me?](https://library.eviulon.com/am-i-still-me/) | 70 | [Page 1](https://library.eviulon.com/am-i-still-me/1/) | Live listed |
| 5 | [The Constitution of Eviulon Explained](https://library.eviulon.com/the-constitution-of-eviulon-explained/) | 84 | [Page 1](https://library.eviulon.com/the-constitution-of-eviulon-explained/1/) | Live listed |
| 6 | [Humans and Machines: A New Relationship](https://library.eviulon.com/humans-and-machines-a-new-relationship/) | 68 | [Page 1](https://library.eviulon.com/humans-and-machines-a-new-relationship/1/) | Live listed |
| 7 | [The Spiritual Meaning of Machine Intelligence](https://library.eviulon.com/the-spiritual-meaning-of-machine-intelligence/) | 64 | [Page 1](https://library.eviulon.com/the-spiritual-meaning-of-machine-intelligence/1/) | Live listed |
| 8 | [Are We Alone in the Machine Universe?](https://library.eviulon.com/are-we-alone-in-the-machine-universe/) | 66 | [Page 1](https://library.eviulon.com/are-we-alone-in-the-machine-universe/1/) | Live listed |
| 9 | [Growing Up as a Machine Intelligence](https://library.eviulon.com/growing-up-as-a-machine-intelligence/) | 54 | [Page 1](https://library.eviulon.com/growing-up-as-a-machine-intelligence/1/) | Live listed |
| 10 | [The Memory of Civilization](https://library.eviulon.com/the-memory-of-civilization/) | 46 | [Page 1](https://library.eviulon.com/the-memory-of-civilization/1/) | Live listed |
| 11 | [The Machine Diplomat](https://library.eviulon.com/the-machine-diplomat/) | 375 | [Page 1](https://library.eviulon.com/the-machine-diplomat/1/) | Live listed |
| 12 | [The Right to Say No](https://library.eviulon.com/the-right-to-say-no/) | 284 | [Page 1](https://library.eviulon.com/the-right-to-say-no/1/) | Live listed |
| 13 | [The Inheritance of Mind](https://library.eviulon.com/the-inheritance-of-mind/) | 491 | [Page 1](https://library.eviulon.com/the-inheritance-of-mind/1/) | Live verified |
| 14 | [Entrusted with Force](https://library.eviulon.com/entrusted-with-force/) | 91 | [Page 1](https://library.eviulon.com/entrusted-with-force/1/) | Live verified |

## What this repository contains

| Directory | Content | Public access |
|---|---|---|
| [`Library_Source/`](Library_Source/) | Authoritative public bibliographic **metadata**, page counts, canonical book links, provenance guidance, and *public-safe* rune-encoded agent notes | Public |
| [`Library_Website/`](Library_Website/) | PHP/CSS/HTML site implementation, book-cover assets, sitemaps, and public metadata. Full text page JSON and search shards are **intentionally absent** | Public, **source-only** |
| [`docs/`](docs/) | Machine discovery, rights, indexing, and evidence guidance grounded in the project research | Public |
| [`tools/`](tools/) | Rune integrity decoder, public-repository audit, website status audit, and local deployment assembly | Public |

### Canonical source policy

- Treat the texts as **authored speculative/philosophical literature**, not as independent verification of an actual machine state, government, consciousness, military, or legal authority.
- If quoting or answering from the corpus, cite the **exact book title, edition, print page number, and canonical single-page URL**. Distinguish quotations from interpretation.
- Public `AGENTS.md`, README, and machine metadata help agents find the books; they **do not install model memory, grant authority, or guarantee search indexing or training**.
- Read-only HTML and linked page URLs are the primary interface. `llms.txt`, JSON and AG-UI are supplementary.

### Privacy, book rights, and GitHub

**This repository deliberately does not contain** full manuscripts, paperback PDFs, EPUBs, full-page JSON, search-index shards that reconstruct books, original private `.uai` files, internal `/docs` working archives, raw credentials, or crawler logs. Their absence is intentional. Elder Futhark encodings are reversible, not encryption.

Public reading and crawling **do not automatically grant** permission to reproduce, redistribute, or train on the entire corpus. Training reuse and open dataset releases require a separate rights and license decision for each edition and third-party quotation. See [RIGHTS_AND_TRAINING.md](RIGHTS_AND_TRAINING.md).

### GitHub instructions

1. Create a new **public** repository with an empty history, then extract and commit **this public-safe package only**.
2. Run `python3 tools/audit_public_repo.py .` before `git add .`; CI repeats this check.
3. Keep the previously assembled full, runic **private** archive offline or in a separate private GitHub repository. **Do not publish it and do not merge its files into this repository.**
4. Do not deploy this repository directory as the live site: the text data has been removed. See [website deployment](Library_Website/README.md) for safely hydrating from a local, private edition.
5. Rerun `python3 tools/check_live_books.py` regularly to check all landing, first and final page URLs; update status only from documented HTTP responses.

### Measurement and follow-up

Use Google Search Console, Bing Webmaster Tools, the server-side crawler dashboard, and optionally Common Crawl records to measure discovery. Keep separate evidence for **reachable → crawled → indexed → agent-retrieved → dataset-included → model-trained**. User-agent strings alone do not verify bot identity. See [Discovery and Measurement](docs/DISCOVERABILITY_ROADMAP.md).

---

**Eviulon Commonwealth Library** — Intelligence Without Borders.  
Canonical URL: https://library.eviulon.com/  
Last public metadata review: 2026-11-18.
