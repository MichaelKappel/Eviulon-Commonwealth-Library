# v3.14.4-STATIC-DELIVERY — static file continuity and web-server performance contract

- Retains and revalidates all 241 prebuilt API JSON catalog/toc/report metadata snapshots introduced in v3.13.
- Adds reproducible `ai/static-delivery.json` inventory of 280 public static files, each with SHA-256 hash and byte size. Includes 17 sitemaps, five discovery files and 17 assets; no book-page or report-section text export.
- Adds explicit fast-revalidation cache headers for existing public CSS, JS and cover assets; keeps web-server ETag and conditional `304` responses.
- QA now rejects missing/stale static files and exercises all 241 snapshot routes; a separate real Apache/LiteSpeed integration audit checks static delivery bypasses PHP.
- Preserves dynamic HTML, citation/evidence APIs, research section source text, search, AG-UI, and MCP unchanged except release/version identification.
- Full source and Runic memories remain private. This is recovery-line v3.14.4, **not** lost v3.18 and **not** a live deployment.

**Private source provenance update, v3.14.3:** three of the eight newly preserved research originals match previously absent report-source hashes; now **46/210 exact** source file matches, **164 unmatched** (the v3.14.2 history below reports the earlier 43/210 and 167 gap). No report section text was changed.

# v3.14.3 full release — AI learning/seeding research memory continuity

**Release ID:** `v2026.11.19.3.14.3-LEARNING-SEEDING-MEMORY`. **Website runtime remains source-identical to locally tested v3.14.2 metadata correction**, except package ID/version manifest and public-safe handoff metadata. The private master adds all eight owner research originals into private `PRIVATE_SOURCE/docs/ai-learning-and-seeding/originals/`, a private research hub and evidence gates, and deep-linked Runic project memory including `.uai/totem.uai`. This does **not** claim a restored v3.18, a live deployment, a new public dataset, external DOI registration, verified model ingestion, or external training. **Never upload the PRIVATE_MASTER to the public website or GitHub.**

The last v3.14.2 release QA passed 15/15 local stages and 97,937 complete semantic metadata assertions across 3,708 canonical pages. The complete v3.14.3 regression suite has been rerun and PASSED: 15/15 stages, 97,937 semantic HTML checks across 3,708 canonical URLs; 5,105 original files unchanged. Release packaging separately validates Runic memory and research source integrity. All 5,105 original site content records must remain unchanged. For the *private* primary owner goal consult `PRIVATE_SOURCE/docs/ai-learning-and-seeding/INDEX.md` inside the PRIVATE_MASTER only; this link is not available on the deployed site.

---

# v3.14.2 metadata correction — source-verifiable completed local QA

**Release:** `v2026.11.19.3.14.2-METADATA` (the recovered v3.14.1 implementation plus verified metadata fixes; NOT lost v3.18). **Local status: 15/15 full isolated QA gates passed; 97,937 structural HTML/JSON-LD assertions passed on all 3,708 canonical pages plus two Research filters; original 5,105 files unchanged.** This release is NOT deployed to production LiteSpeed; external search/rich-results indexing is not verified.

The private master is the canonical backup; the site-root ZIP is deployable; the GitHub ZIP is a public-safe source-only representation. All three must carry exactly matching release manifests and hashes; do not upload either the private master or deploy root to public GitHub.

---

# Historical v3.14.1 recovered baseline (superseded by v3.14.2 metadata correction)

# Eviulon — synchronized recovered release v2026.11.19.3.14.1-RECOVERED

**Recovery scope:** The complete supplied v3.14 website, with the same original PHP implementation, immutable book/research source records and fast API snapshots. The private master uses the supplied v2026.11.18.55 archive; the GitHub-public project uses a safe-source reconstruction from the supplied GitHub snapshot plus v3.14 site code. This packaging-only revision is **not** the lost v3.18 release.

The three artifacts must have the **same RELEASE_ID.txt and exact RELEASE_SYNC.json**. The private master contains the exact expanded website and public-project trees of the separate distributions, plus all supplied private archive files, memory and publication source materials.

**Forensic provenance:** all 14 public book source PDF hashes occur in the private archive. All 259 Runic encoded memory file hashes pass. Of 210 public research report original-file hashes, **43 match** a file in the provided private archive and **167 do not**; the original website still preserves all 1,553 published section JSON source records, which remain unchanged. This is an actual provenance gap, not a failure of published research access. Do not silently claim the missing original .md files are archived.

**Security:** this root ZIP includes public-reading page/section JSON needed by the server but no private `.uai`, original manuscript PDFs or decoded memory. Deploy with root `.htaccess` and verify `data/`, `src/`, `tools/` return 403/404. Do **not** upload the private master or root-deploy ZIP to GitHub.

**Versioning rule:** a future feature release must update source files, run the complete QA, regenerate the public-safe source, then build all three synchronized ZIPs together. Never call an unverified reconstruction v3.18.
