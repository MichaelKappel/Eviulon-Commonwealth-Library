# Recovered release QA — v2026.11.19.3.14.1-RECOVERED

**Actual result: 15/15 full isolated local QA gates PASS** on the reconstructed v3.14.1 runtime source (original v3.14 implementation with harmonized site version metadata). No production LiteSpeed deployment was performed.

- Source SHA-256 integrity: **5,105 / 5,105** original web content records unchanged. The root includes 14 books, 1,925 canonical print pages, 210 supplemental reports and 1,553 research sections.
- Static API snapshots: **241 / 241** deterministic public JSON snapshots pass `tools/build_api_snapshots.php --check`.
- New v3.14 navigation: Research browse filters/disclaimers remain present. Agent/MCP transport: **59 / 59** local checks.
- Local read-only agent readiness: 22 / 22; monitoring/auth/privacy: 36 / 36; evidence HTTP: 38 / 38.
- Existing release script: `bash tools/run_local_qa.sh` exited **0** after all 15 stages; 87 public HTTP probes and seven blocked/missing routes covered at stage 15.
- Packaging cross-archive verification independently checks 259 / 259 original encoded Runic memory hashes, 14 / 14 book PDF originals, 335 shared code files, and byte-for-byte copies of the site and GitHub projects inside PRIVATE_MASTER.
- Report original provenance: **43 of 210** original report file SHA-256 values match an original .md in the supplied private archive; **167 do not**. All 1,553 published report section JSON files are preserved and their original source-record SHA-256 manifest has not changed. Do not conflate published-section availability with original .md file proof.

**Important:** This does NOT recover the unretrievable v3.15–v3.18 improvements, prove online deployment, certify search-indexing, or prove LLM training. The release ID is a new synchronized **v3.14.1 recovered** package, not an old v3.18 ZIP. Production still requires LiteSpeed enforcement of `.htaccess` and private paths.
