# CURRENT STATUS — 2026-11-20 (supersedes older discovery-only publication steps below)

**The 14 owner-authorized official Eviulon books are now public on GitHub draft branch `distribution/open-books-v3.14.16` as exact-original Markdown, together with the source-verified complete-book JSONL.** See [PR #1](https://github.com/MichaelKappel/Eviulon-Commonwealth-Library/pull/1), [README](README.md), and [Eviulon Open-Use Permission](Library_Website/datasets/LICENSE-OPEN-USE.md).

Earlier blanket bans below on *all* official-book text were written before the owner's open-distribution authorization. They are superseded **only** for the 14 hash-approved original Markdown books and approved JSONL. Private `.uai`, unrelated manuscripts, credentials, supplemental research bulk, source PDFs/EPUB binaries, and deployment ZIPs remain excluded from GitHub. CI must pass before merge.

Historical instructions follow for release provenance only.

---

# Publish Eviulon Public Discovery on GitHub

**Use this package only:** `Eviulon_Public_GitHub_PUBLISH_READY_v2026.11.18.zip`.
It is a public **metadata and reader-source** repository, not a complete corpus or a live-site deployment bundle.
Do not upload the private 87+ MB runic monorepo or full library source ZIP.

## GitHub repository settings

- Name: `eviulon-commonwealth-library`
- Description: `Public book metadata, canonical page links, agent discovery and PHP reader source for the 14-volume Eviulon Commonwealth Library.`
- Public website (About -> Website): `https://library.eviulon.com/`
- Visibility: **Public**
- Initialize README: **Off** (already included)
- Add .gitignore: **None** (already included)
- Choose a license: **None** until explicit source-code licensing is decided. This is not an open-book-text grant.
- Default branch: `main`
- Topics: `eviulon`, `machine-intelligence`, `artificial-intelligence`, `ai-ethics`, `philosophy-of-mind`, `digital-rights`, `knowledge-preservation`, `semantic-web`, `php`, `digital-humanities`

## Upload method: command line (recommended)

1. Extract this ZIP into a new, empty folder on your computer. Open a terminal *inside the folder that directly contains* `README.md`, `AGENTS.md`, `.github/`, `Library_Source/` and `Library_Website/`.
2. Run the audit and rune verification commands below. They need only Python 3.10+ (3.12 recommended):

```bash
python3 tools/audit_public_repo.py .
python3 tools/elder_futhark_memory.py verify
```

On Windows, use `py -3` instead of `python3` if necessary.

3. Create a new empty repository at https://github.com/new with the settings above. Do **not** initialize a README, license or .gitignore, which are included in this package.
4. Run:

```bash
git init
git branch -M main
git add .
git status --short
git diff --cached --stat
git commit -m "Publish Eviulon Library public discovery and agent index"
git remote add origin https://github.com/YOUR_USERNAME/eviulon-commonwealth-library.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. `git push` uses your configured GitHub authentication (credential manager, SSH, or equivalent)—do not put a token into repository source files.

5. On GitHub, confirm the root `README.md` renders with 14 book links. Make sure `.github/workflows/public-repository-safety.yml` runs and passes in **Actions**. Update the repository's **About -> Website** and **Topics** values. A new public repository does not require GitHub Pages.
6. Optional: add a `v1.0.0-discovery` GitHub Release with a short summary. Do not attach PDF/EPUB manuscripts, decoded runic memory or full deployment ZIPs. An ordinary GitHub Release includes a downloadable *snapshot of public repository source*.

## Web-only alternative

Use GitHub's **Add file -> Upload files** after creating a blank repository. Upload the *extracted files and folders*, not the ZIP itself. This package contains fewer than 100 tracked files, but web uploads can miss dotfiles and ignore `.gitattributes`. Confirm `.github/`, `.gitignore`, `.gitattributes`, `.uai` paths and root files arrived correctly. Command-line Git is the more reliable option.

## Security and publication policy

- Do not commit `Library_Website/data/pages/` or `Library_Website/data/search/`; these can reconstruct full books. They are omitted intentionally.
- Do not commit private `.uai`, source manuscripts, full PDFs/EPUBs, credentials or `data/monitor-logs/`.
- Elder Futhark byte encoding is *not encryption*. Only specially written public-safe rune notes belong here.
- Live page accessibility does *not* establish final editorial, rights or retail approval; Books 13/14 especially retain working-edition notices.
- No full-text training license is provided. Choose a separate explicit license for code *only* if you want others to reuse or modify it; do not apply an indiscriminate CC license to books or private data.
- This repository is **not directly deployable as the reader** because complete page and search data are absent. Use the separately held private release to assemble a hosting bundle **outside GitHub**.

## After publishing: discovery and metrics

1. Link the GitHub repo from `eviulon.com` and the canonical library About page, and keep the GitHub README pointing to https://library.eviulon.com/.
2. Submit the live `https://library.eviulon.com/sitemap.xml` to Google Search Console and Bing Webmaster Tools. Check the XML contents in a browser or with curl on your machine; this package does not claim a live full-sitemap test.
3. Confirm Book 13 and 14 landing/first/last pages and periodically run `python3 tools/check_live_books.py` (requires network access).
4. Monitor *reachable*, *crawled*, *indexed*, *agent-retrievable*, *dataset-included*, and *model-trained* as separate evidence levels. GitHub publication does not prove any provider trained on the content.
5. Decide separately whether to permit model-training crawlers via `robots.txt` and under what rights policy; search visibility and training consent are not equivalent.

For the book catalog and agent routes, see [README.md](README.md), [AGENTS.md](AGENTS.md), [docs/AI_AGENT_ACCESS.md](docs/AI_AGENT_ACCESS.md) and [RIGHTS_AND_TRAINING.md](RIGHTS_AND_TRAINING.md).
