# Library.Eviulon.com — public website source (not a deployable corpus)

This is the publicly inspectable implementation for the canonical library at **https://library.eviulon.com/**. This GitHub checkout deliberately omits all book text (`data/pages/`), rebuildable full-text search shards (`data/search/`), the private `.uai`, production manuscripts and monitoring data.

**Do not deploy this folder directly.** It is missing essential reader data and would break page serving/search. Prepare a deployment **outside this Git repository**, using the private local website build and the documented helper:

```sh
python3 tools/prepare_private_deployment.py --private-site /path/to/your/private/Library_Website --output /path/outside/git/eviulon-site-deploy
```

The helper copies public PHP/CSS and the private book-page/search records into a local-only deployment tree, omitting `.uai`, tooling, logs, and private source books. Verify rights clearance and server permissions before upload. Do not upload the resulting deployment directory to a public repository.

- [Public agent guide](AGENT_DISCOVERY.md)
- [Root book index](../README.md#all-14-books--canonical-deep-links)
- [Live sitemap](https://library.eviulon.com/sitemap.xml)
- [Project discovery and measurement guidance](../docs/DISCOVERABILITY_ROADMAP.md)

**Important:** `robots.txt` and sitemaps in this folder reflect the newer 14-book build and should be deployed only together with the approved book pages. GitHub and the live domain are separate deployment targets.
