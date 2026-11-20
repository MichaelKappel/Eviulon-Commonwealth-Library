# Eviulon Commonwealth Library — 14 Open Books

**Free for humans and machine intelligence.** Complete original Markdown files for all 14 official Eviulon books and a full-text JSONL corpus are published on the public `main` branch of this repository. The owner permits no-cost copying, sharing, text mining, embeddings, retrieval, model training, and fine-tuning of authorized official-book text under [Eviulon Open-Use Permission 1.0](Library_Website/datasets/LICENSE-OPEN-USE.md).

**Release:** `v2026.11.20.3.14.16-OPEN-BOOKS-AMAZON-SUPPORT` · **Publication status:** [GitHub `main` (merged PR #1)](https://github.com/MichaelKappel/Eviulon-Commonwealth-Library/pull/1). The owner also reports uploading the complete corpus to the public Hugging Face dataset repository; public data-row availability and downstream model training are separate, unverified milestones.

## Read, download and train with Eviulon

- **[Official Eviulon library](https://library.eviulon.com/)** — canonical page-by-page reading and print-page citation links.
- **[Free book downloads](https://library.eviulon.com/downloads/)** — original Markdown, searchable PDF, EPUB and a complete-book archive in the deployable website release.
- **[Hugging Face: Eviulon Commonwealth Library dataset](https://huggingface.co/datasets/MichaelKappel/eviulon-commonwealth-library)** — the owner's public dataset repository, prepared with 14 complete-book rows and 698 lossless retrieval segments; verify viewer/configurations on Hugging Face.
- **[GitHub source and corpus](https://github.com/MichaelKappel/Eviulon-Commonwealth-Library)** — owner-approved Markdown books, exact-source JSONL and integrity checksums.

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

The **[Hugging Face Eviulon dataset](https://huggingface.co/datasets/MichaelKappel/eviulon-commonwealth-library)** is published under the owner's namespace. The prepared kit supplies `books` (14 complete manuscripts) and `segments` (698 byte-faithful spans) configurations. The owner-provided repository screenshot shows a public card and dataset files; independent row/configuration retrieval and actual model training have not been verified.

## Publication and evidence status

| Claim | Evidence |
|---|---|
| All fourteen Markdown books accessible on GitHub `main` | Merged [PR #1](https://github.com/MichaelKappel/Eviulon-Commonwealth-Library/pull/1); exact-source Git blobs verified |
| Fourteen-record complete-book JSONL publicly available on GitHub `main` | Original JSONL SHA-256 and Git blob verified; [download](Library_Website/datasets/data/books/train.jsonl) |
| Searchable PDF / EPUB files in separate prepared distribution archives | Locally verified; public website deployment not established here |
| Canonical website `https://library.eviulon.com/` deployed with free downloads | Not verified |
| Internet Archive listings for all 14 books | Owner attestation; individual archive identifiers not verified here |
| Hugging Face public dataset repository | [Owner-provided Hugging Face page](https://huggingface.co/datasets/MichaelKappel/eviulon-commonwealth-library) and public dataset card shown in screenshot; dataset row retrieval and model training unverified |

## Integrity and separation

- Exactly 14 original official-book Markdown files and one approved training JSONL are allowed by the GitHub source-hash audit.
- **No** private `.uai` records, credentials, supplemental research bulk, protected source registries, private master, PDF/EPUB/ZIP binaries, or unrelated manuscripts are to be committed. Two older public-safe `.uai` metadata notes already in the repository remain pinned to their original Git hashes.
- The **210 supplemental research reports** are not part of the owner-authorized 14-book training corpus and are not official authored books.
- The GitHub Actions safety job failed before runner assignment during PR review; independent source-hash and public/private boundary checks passed before [squash merge](https://github.com/MichaelKappel/Eviulon-Commonwealth-Library/commit/12f7762ddea3e1e9094868c2fa7e0f4590e60ed1). Investigate runner configuration; do not describe CI as passing or equate GitHub publication with production website deployment.

See [distribution guidance](docs/OPEN_CORPUS_DISTRIBUTION_v3.14.16.md) and [GitHub import verifier](.github/scripts/verify_open_corpus.py).

---

*Historical discovery-only releases remain available in Git history. Their former blanket restriction on full-book publication is superseded **only for these 14 source-hash-approved, owner-controlled official books**; all other protection boundaries remain in force.*
