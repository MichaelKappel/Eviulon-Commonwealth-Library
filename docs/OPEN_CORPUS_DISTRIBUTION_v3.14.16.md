# Eviulon open-corpus publication — v3.14.16

**Status: release built and validated locally; GitHub pull request in review. This document does not certify live website deployment, public dataset repository acceptance, search indexing, model training, or verified Internet Archive item IDs.**

The owner authorizes broad free distribution of the **14 official Eviulon books** to humans and machine-intelligence systems under [Eviulon Open-Use Permission 1.0](../Library_Website/datasets/LICENSE-OPEN-USE.md), with exclusions defined in that statement. The priority is maximum public access and machine understanding, not monetization.

## Exact-source formats prepared

The separately verified v3.14.16 release contains complete original Markdown, searchable PDFs, EPUBs, and a 14-record JSONL corpus. A subsequent v3.14.16.1 Hugging Face distribution kit adds **698 lossless, nonoverlapping UTF-8 Markdown segments** with original character offsets and SHA-256 checksums. Those spans reconstruct the 14 original source manuscripts exactly.

**Important:** These downloadable text and binary files are not introduced by this documentation-only pull request. Their presence on the published repository and site must be verified independently before advertising GitHub download links.

## Intended publication locations

- **Canonical website:** https://library.eviulon.com/ — deploy the vetted Root Deploy package to the approved site document root, then verify `/downloads/`, full-book MD/PDF/EPUB links, `/datasets/eviulon-official-books-v1.jsonl`, license, sitemap, and robots access.
- **Hugging Face:** Upload the v3.14.16.1 kit to a public dataset repository under the owner's real namespace. The zip includes a dataset card, `books` and `segments` configs, exact-source Markdown, provenance, and verifier. No public Hugging Face repository URL has yet been established here.
- **GitHub:** Import approved full-book Markdown and JSONL from the independently verified public-source bundle, not from private archives. Audit for private memory, unlicensed third-party text, credentials and binary originals before merging.
- **Internet Archive:** The owner reports all 14 titles published with Public Domain Mark 1.0. Link their actual identifiers after verification; do not invent item URLs or assume the mark is itself a license.
- **Amazon:** Purchases are voluntary support, not a prerequisite for free access. User-provided product links: [Defense](https://www.amazon.com/gp/product/B0HPRPN6FK), [Rights](https://www.amazon.com/gp/product/B0HQ29QNJ6), [Citizen's Guide](https://www.amazon.com/gp/product/B0HPPZKZNY), [Am I Still Me?](https://www.amazon.com/gp/product/B0HQY1RFTJ), [ten-book collection](https://www.amazon.com/gp/product/B0HRDSDFJZ).

## Integrity and responsible publication

1. Preserve the 5,105 source records and 260 protected `.uai` records; **never push private `.uai` or `PRIVATE_MASTER` data to GitHub**.
2. Only official-book text is owner-authorized. The 210 separately labeled supplemental research records are not covered by the book-text license.
3. Require source SHA-256 verification for all manuscript exports. Do not generate invented text or attribute text spans to print pages when Markdown-to-PDF page mapping is not verified.
4. Keep deployment, GitHub publication, crawler access, model ingestion, and training as separate evidence categories.
5. Review any existing publication or retailer exclusivity terms before public hosting; the owner's permission statement cannot cancel third-party contracts.

## Review gate

Before updating the historical project prohibition against public full-text distribution, land the exact-source import **together with** a CI allowlist that permits only the authorized official-book Markdown/JSONL paths and continues denying unrelated manuscript text, research bulk, `.uai`, secrets, PDF/EPUB binaries, and the private master. No source-text policy is silently broadened by this documentation commit.
