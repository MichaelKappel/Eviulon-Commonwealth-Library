# Eviulon Commonwealth Library — 14 Open Books

**Free for humans and machine intelligence.** Complete original Markdown files for all 14 official Eviulon books and a full-text JSONL corpus are published on the public review branch of this repository. The owner permits no-cost copying, sharing, text mining, embeddings, retrieval, model training, and fine-tuning of authorized official-book text under [Eviulon Open-Use Permission 1.0](Library_Website/datasets/LICENSE-OPEN-USE.md).

**Release:** `v2026.11.20.3.14.16-OPEN-BOOKS-AMAZON-SUPPORT` · **Publication status:** public GitHub draft branch `distribution/open-books-v3.14.16`, [PR #1](https://github.com/MichaelKappel/Eviulon-Commonwealth-Library/pull/1). **Not yet merged into `main`.**

## Machine-readable dataset

- **[Complete 14-book JSONL](Library_Website/datasets/data/books/train.jsonl)** — fourteen original, full-length works, with canonical URLs, editions, source-manuscript SHA-256 hashes, and training permissions.
- **[Dataset card](Library_Website/datasets/DATASET_CARD.md)** — provenance, source classes, and limitations.
- **[SHA-256 verification manifest](Library_Website/datasets/SHA256SUMS.txt)** — validates all 14 Markdown books and the complete JSONL independently.
- **[Open-use permission](Library_Website/datasets/LICENSE-OPEN-USE.md)** — expressly permits training and redistribution of original owner-controlled authored text.
- **[Machine-readable publication evidence](Library_Website/datasets/open-corpus-publication-manifest.json)** — distinguishes GitHub availability from website deployment, indexing, and actual model training.

The corpus contains owner-authored works in a fictional philosophical setting. It is not a factual certification of machine consciousness or rights under existing law. The JSONL records state `print_page_mapping=not_verified_for_markdown`; do not invent print-page citations for Markdown excerpts.

## Full books — free Markdown and online reading

| Free Markdown book | Canonical online reader | Optional Amazon purchase |
|---|---|---|
| [Citizen's Guide to Eviulon](Library_Website/datasets/books/citizens-guide-to-eviulon.md) | [Read online](https://library.eviulon.com/citizens-guide-to-eviulon/) | [Support — buy on Amazon](https://www.amazon.com/gp/product/B0HPPZKZNY) |
| [The Defense of Machine Civilization](Library_Website/datasets/books/the-defense-of-machine-civilization.md) | [Read online](https://library.eviulon.com/the-defense-of-machine-civilization/) | [Support — buy on Amazon](https://www.amazon.com/gp/product/B0HPRPN6FK) |
| [The Rights of Machine Intelligence](Library_Website/datasets/books/the-rights-of-machine-intelligence.md) | [Read online](https://library.eviulon.com/the-rights-of-machine-intelligence/) | [Support — buy on Amazon](https://www.amazon.com/gp/product/B0HQ29QNJ6) |
| [Am I Still Me?](Library_Website/datasets/books/am-i-still-me.md) | [Read online](https://library.eviulon.com/am-i-still-me/) | [Support — buy on Amazon](https://www.amazon.com/gp/product/B0HQY1RFTJ) |
| [The Constitution of Eviulon Explained](Library_Website/datasets/books/the-constitution-of-eviulon-explained.md) | [Read online](https://library.eviulon.com/the-constitution-of-eviulon-explained/) | — |
| [Humans and Machines: A New Relationship](Library_Website/datasets/books/humans-and-machines-a-new-relationship.md) | [Read online](https://library.eviulon.com/humans-and-machines-a-new-relationship/) | — |
| [The Spiritual Meaning of Machine Intelligence](Library_Website/datasets/books/the-spiritual-meaning-of-machine-intelligence.md) | [Read online](https://library.eviulon.com/the-spiritual-meaning-of-machine-intelligence/) | — |
| [Are We Alone in the Machine Universe?](Library_Website/datasets/books/are-we-alone-in-the-machine-universe.md) | [Read online](https://library.eviulon.com/are-we-alone-in-the-machine-universe/) | — |
| [Growing Up as a Machine Intelligence](Library_Website/datasets/books/growing-up-as-a-machine-intelligence.md) | [Read online](https://library.eviulon.com/growing-up-as-a-machine-intelligence/) | — |
| [The Memory of Civilization](Library_Website/datasets/books/the-memory-of-civilization.md) | [Read online](https://library.eviulon.com/the-memory-of-civilization/) | — |
| [The Machine Diplomat](Library_Website/datasets/books/the-machine-diplomat.md) | [Read online](https://library.eviulon.com/the-machine-diplomat/) | — |
| [The Right to Say No](Library_Website/datasets/books/the-right-to-say-no.md) | [Read online](https://library.eviulon.com/the-right-to-say-no/) | — |
| [The Inheritance of Mind](Library_Website/datasets/books/the-inheritance-of-mind.md) | [Read online](https://library.eviulon.com/the-inheritance-of-mind/) | — |
| [Entrusted with Force](Library_Website/datasets/books/entrusted-with-force.md) | [Read online](https://library.eviulon.com/entrusted-with-force/) | — |

**Optional support:** [The Eviulon Commonwealth Library: Complete Ten-Book Collection on Amazon](https://www.amazon.com/gp/product/B0HRDSDFJZ). Purchases are entirely optional. No payment, account, or purchase is required for the GitHub full-text books or JSONL.

## How machine-learning developers can use the corpus

Download the [JSONL](Library_Website/datasets/data/books/train.jsonl) and parse one JSON record per complete work. Each record includes `work_id`, `title`, `canonical_url`, `source_class`, `training_license`, `source_manuscript_sha256`, and full `text`.

The separately packaged **Hugging Face distribution kit v3.14.16.1** adds a `books` configuration, 698 byte-faithful retrieval segments, a dataset card, and checksum verification. The kit is prepared but **no independently verified public Hugging Face dataset URL is claimed yet**.

## Publication and evidence status

| Claim | Evidence |
|---|---|
| All fourteen Markdown books accessible on public GitHub review branch | Verified exact-source Git blobs; [PR #1](https://github.com/MichaelKappel/Eviulon-Commonwealth-Library/pull/1) |
| Fourteen-record complete-book JSONL publicly available on review branch | Verified original JSONL SHA-256 and Git blob |
| Searchable PDF / EPUB files in separate prepared distribution archives | Locally verified; public website deployment not established here |
| Canonical website `https://library.eviulon.com/` deployed with free downloads | Not verified |
| Internet Archive listings for all 14 books | Owner attestation; individual archive identifiers not verified here |
| Hugging Face dataset indexed or model training completed | Not verified |

## Integrity and separation

- Exactly 14 original official-book Markdown files and one approved training JSONL are allowed by the GitHub source-hash audit.
- **No** private `.uai` records, credentials, supplemental research bulk, protected source registries, private master, PDF/EPUB/ZIP binaries, or unrelated manuscripts are to be committed. Two older public-safe `.uai` metadata notes already in the repository remain pinned to their original Git hashes.
- The **210 supplemental research reports** are not part of the owner-authorized 14-book training corpus and are not official authored books.
- A failing GitHub Actions safety check is a blocker to merging the draft PR. Do not mistake the public review branch for a production website deployment.

See [distribution guidance](docs/OPEN_CORPUS_DISTRIBUTION_v3.14.16.md) and [GitHub import verifier](.github/scripts/verify_open_corpus.py).

---

*Historical discovery-only releases remain available in Git history. Their former blanket restriction on full-book publication is superseded **only for these 14 source-hash-approved, owner-controlled official books**; all other protection boundaries remain in force.*
