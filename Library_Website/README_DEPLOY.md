# Deploying Library.Eviulon.com from the PUBLIC GitHub source snapshot

**This public GitHub folder is not directly deployable as a functioning book library.** The public package deliberately excludes `data/pages/` (all page text) and `data/search/` (the full-text index). This is by design: the original owner wants the website to offer online reading rather than a bulk GitHub mirror of complete books.

## Restore an approved deployment locally

1. Keep the original private Eviulon website release in a location OUTSIDE the public Git repository.
2. Ensure Books 13 and 14 have appropriate publication rights and editorial clearance before releasing their complete text.
3. Run from the repository root:

```sh
python3 tools/prepare_private_deployment.py \
  --private-site /path/to/private/Library_Website \
  --output /path/outside/git/Library_Eviulon_DEPLOY
```

The tool combines the public implementation with the complete book-page JSON and search shards from your PRIVATE website release. It verifies the per-book total. It explicitly excludes the `.uai` notes, private documents, decoder tools, monitoring credentials, log files, and source book PDFs/EPUBs. **Never publish or commit the assembled deployment directory to public GitHub**.

4. Inspect the assembled deployment directory and PHP version requirements (PHP 8.1+, Apache rewriting or equivalent), configure the webserver to restrict `data/`, `src/` and admin paths, then deploy only the assembled website output into the `library.eviulon.com` document root.
5. Preserve existing local live `data/monitor-config.php` and `data/monitor-logs/` during deployment. Do not add them to any public repository.
6. Confirm live HTML on each book's first and last page, correct canonical URLs, the complete XML sitemap, and no public access to protected files. Update README live status for Books 13 and 14 only after confirming successful live responses.

## Copyright and web crawling

This website exposes print-page HTML for browser reading, citations, and machine retrieval. Any public HTML text remains technically reproducible by a scraper; no download links are not copy prevention. `robots.txt` is a crawler-cooperation rule, not security or a license for downstream training. See `../RIGHTS_AND_TRAINING.md` and `../docs/DISCOVERABILITY_ROADMAP.md`.

**Do not upload the original private runic monorepo to the public repository. Elder Futhark encoding is reversible, not confidentiality protection.**
