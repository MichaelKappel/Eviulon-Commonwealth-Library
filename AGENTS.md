# Eviulon current public distribution policy — owner authorization (2026-11-20)

**Current governing exception to the historical discovery-only policy below:** the owner has expressly authorized free public distribution, copying, redistribution, machine reading, embeddings, and model training of the **14 original official Eviulon books**, in their verified v3.14.16 Markdown and JSONL editions. The [open-use permission](Library_Website/datasets/LICENSE-OPEN-USE.md) applies only to those owner-controlled official book texts.

The public review branch `distribution/open-books-v3.14.16` includes exactly:
- `Library_Website/datasets/books/<one-of-14-approved-slugs>.md`
- `Library_Website/datasets/data/books/train.jsonl`

The [source audit](.github/scripts/verify_open_corpus.py) pins the SHA-256 hash of each of those files and the 14-record JSONL. The original source content may not be rewritten or paraphrased in place. GitHub PR #1 must remain unmerged until its safety CI passes.

**Still forbidden from this public repository:** any private `.uai` memory or decoded runic project data; source manuscripts outside the hash-approved public export set; unrelated or third-party copyrighted text; all bulk supplemental research (210 reports); internal tooling secrets; private backups, the entire deployment root, and PDF/EPUB/ZIP binaries. Only two long-existing public-safe `.uai` metadata notes are retained, guarded by exact Git blob hashes. Never conflate archived historical prohibitions with the current narrowly scoped permission for approved official-book text.

**Evidence:** public GitHub review-branch availability is verified. Live website deployment, external dataset publication, indexing, and actual model training remain unverified.

---

## Historical release rules (superseded only for approved official-book exports)

# Release v2026.11.19.3.14.4-STATIC-DELIVERY

Static-delivery safeguards are synchronized with the deployable website, including 241 prebuilt catalog JSON files and the 280-file public static inventory. The private `.uai` memory and source books remain excluded; no claims of public training or recovered v3.18.

# Package revision v2026.11.19.3.14.3-LEARNING-SEEDING-MEMORY

**Runtime source:** v3.14.2, unchanged. **Primary owner learning/seeding mission** is recorded in private memory and private `/docs` in the separately archived PRIVATE_MASTER; neither is included here. No authorized public dataset, legal clearance, DOI or external AI training is implied. Never add `.uai` or private `/docs` to GitHub. All three archives must have matching release IDs and tree hashes.

---

# Eviulon public-project rules — v2026.11.19.3.14.2-METADATA

Do not add private `.uai` and Runic memory, unpublished manuscripts, full-text book/research records, source PDFs, credentials or private review/gold data. Copy only source code, approved public metadata and derived assets. Do not label supplemental Research as official doctrine; do not invent authors, review status, DOIs, licenses or externally verified training claims.
