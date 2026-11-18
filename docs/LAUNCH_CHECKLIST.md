# Public release checklist

- [ ] Verify this ZIP is the **public-discovery** package, not the 87.7 MB private runic monorepo.
- [ ] Run `python3 tools/audit_public_repo.py .` and `python3 tools/elder_futhark_memory.py verify`.
- [ ] Verify no full book PDFs, EPUBs, markdown manuscripts, page JSON, search index shards, private `.uai`, internal docs, credentials, or crawler logs.
- [ ] Check publication/rights clearances, especially Books 13 and 14.
- [ ] Create a new public repository; do not import the earlier private repository history or commit private files.
- [ ] Publish README/book metadata; apply GitHub topics and site URL.
- [ ] If deploying 14-book site, use separate local private corpus, never this public GitHub checkout unhydrated.
- [ ] Verify live site book landing pages, page 1 and final page, sitemap and canonical tags.
- [ ] Update README Books 13–14 statuses **only after** live GET verification.
- [ ] Submit complete sitemap to Search Console and Bing Webmaster Tools.
- [ ] Test canonical page indexing and the site's actual crawler/WAF policy.
- [ ] Record evidence of reachability, crawling and retrieval separately from training.
