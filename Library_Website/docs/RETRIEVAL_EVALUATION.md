# Retrieval Evaluation Contract — v3.5

**Status:** shipped, locally tested, and NOT a claim that any external agent/model has used this site.  
**Scope:** canonical 14-book reading corpus, separate opt-in Eviulon/Evulgare research, read-only REST API and AG-UI.  
**Extra service cost:** $0; Python standard library, existing Apache/PHP.

## Why this exists

The accompanying *Eviulon AI Access Architecture* report specifies a 50-query evaluation across direct facts, misattribution, negative questions, chapter citations, and dissent/uncertainty, and distinguishes retrieval metrics from generated-answer faithfulness. The *AI Content Discoverability Campaign* proposes a further 60-question blind model benchmark, and explicitly warns that publicly publishing the answer key could contaminate future tests. The v3.5 release implements the **first deterministic, locally reproducible retrieval and citation layer**—it does **not** claim that a full human-judged 50- or 60-question semantic benchmark has been executed.

### Stable data contracts

- **Official books:** 14 approved authored Eviulon works, 1,925 individual print pages, source-verified TOC headings. These are the primary citation authority.
- **Research:** 210 public-source Eviulon/Evulgare reports, 1,553 sections, *supplemental and not approved doctrine*.
- **Default:** Books checked; Research unchecked. REST/AG-UI default to Books. Both selected → book results first.
- **Canonical identity:** `https://library.eviulon.com/{book-slug}/{page}/`; research at `/research/{group}/{slug}/{section}/`.
- **No semantic inference:** The public search is lexical + a bounded source-derived chapter-heading relevance boost. There are no embeddings, hosted LLMs, model weights, or vector index.
- **Immutability:** No source text, page boundaries, source metadata, report text, search posting shards or raw `.uai` records change in this release.

## Run against a disposable local server

From the website root:

```bash
bash tools/run_local_qa.sh
```

This includes these independent, runtime-generated checks:

```bash
python3 tools/test_retrieval_quality.py
python3 tools/retrieval_quality.py --http http://127.0.0.1:PORT --smoke
python3 tools/test_chapter_relevance.py --http http://127.0.0.1:PORT
```

Run against a real URL only after the owner has deployed and explicitly authorized external traffic:

```bash
python3 tools/retrieval_quality.py --http https://library.eviulon.com \
  --allow-live --suite /secure/private/eviulon-human-gold.json \
  --out /secure/private/eviulon-evaluation-report.json --k 5
```

The target domain will receive one search request per case plus up to `k` citation metadata requests per case and optional single-page quote verification requests. Never point the load test at a third-party website. All result JSON and gold suites must remain **outside the deployable web document root**. The CLI refuses to read/write these private paths under its `--root`.

## Create a PRIVATE lexical source-grounded probe suite

On an owner-controlled machine (the output path is deliberately outside the deployable folder):

```bash
python3 tools/generate_private_retrieval_suite.py \
  --out /secure/private/eviulon-50-source-probes.json
python3 tools/retrieval_quality.py --http http://127.0.0.1:PORT \
  --suite /secure/private/eviulon-50-source-probes.json \
  --out /secure/private/eviulon-50-source-probes-results.json
```

This creates **50 automatically source-derived official-book lexical probes plus 2 zero-hit controls**, each tied to a known physical page and a literal source quotation. Their purpose is to prove that existing inverted-index words point to the exact source and that citation metadata/quotation verification still works. This is intentionally an **easier, source-derived smoke test**, not an independent human-judged evaluation; excellent scores are expected and must not be marketed as semantic comprehension, independent relevance validation, or model training.

## Suite format and type rules

A private suite is JSON:

```json
{
  "schema_version": "1.0",
  "suite_name": "owner-controlled-2026-11",
  "human_judged": true,
  "cases": [
    {
      "id": "EXAMPLE_01",
      "category": "chapter_citation",
      "query": "OWNER_WRITTEN_QUESTION",
      "scope": ["books"],
      "match": "any",
      "expected": [{"type": "book", "slug": "your-book-slug", "page": 1}],
      "exact_quote": "SOURCE_VERBATIM_EXCERPT"
    }
  ]
}
```

Replace the placeholders with verified original-page evidence. Do **not** save the filled gold JSON, test transcripts, or private judgments inside the site root or public GitHub repository. For research-only expected references use `{"type":"research","report_id":"evulgare/report-slug","section":1}` with `scope:["research"]` or explicit combined scope. The checker rejects research expectations without research opt-in. A lexical zero-result probe has `expected:[]` and `expect_zero_results:true`; this checks only that the selected words produced no matches, not that the philosophical question is unanswerable.

## Evaluation metrics and honest limits

- **Hit@k:** proportion of labeled cases for which at least one labeled relevant item was in the first `k` results.
- **Recall@k:** mean fraction of the owner-labeled expected items retrieved at rank ≤ `k`.
- **MRR@k:** mean reciprocal rank of the first labeled item (zero if not found).
- **Observed precision lower bound:** fraction of top-k results labeled relevant. It can undercount relevance if the suite contains incomplete labels; it is **not** true context precision.
- **Citation integrity:** verifies that result metadata equals the independent citation API's canonical URL, source category and page/section identity.
- **Exact quotation fidelity:** checks literal text in the original per-page/per-section content API record. A matching quote is evidence of source fidelity, not proof that a paraphrase is logically entailed.
- **Source policy:** rejects cross-source leakage, missing research disclaimer, and incorrect authority fields.

**Not measured:** semantic entailment, question-answering accuracy, false-premise rejection, uncertainty handling by an actual model, generated-answer faithfulness, real-world truth of third-party reports, independent publication approval, search-engine indexing, crawler identity, or incorporation into model weights. These require separate owners' blind agent tests and evidence.

## Realistic navigation pilot (v3.4 → v3.5)

A private, reproducible 28-case pilot used the titles of the first and middle chapters from each book as search queries, with the *source-verified chapter opening page* as the expected target, using exploratory `match=any`. Because both the questions and labels come from source headings, this pilot is more natural than rare-term smoke, but still not independently human-judged.

| Metric | v3.4 unboosted | v3.5 heading boost |
|---|---:|---:|
| Source heading cases | 28 | 28 |
| Hit@5 | 24/28 (85.7%) | 28/28 (100%) |
| MRR@5 | 0.3583 | 0.9821 |
| Citation metadata integrity | 100% | 100% |

The improvement is due to **ranking within the existing indexed page candidates**, never to fabricated page content. Results are a **local PHP dev server result**, not live Google/Bing or external agent performance.

## Future independent agent evaluation

To implement the reports' intended 50-query human-judged benchmark, maintain ten **private**, separately adjudicated cases each for direct facts, misattribution, negative questions, chapter citations and dissent/uncertainty. Use source-page citations and blind judgments; do not auto-generate the gold answers from the current search index. Evaluate an actual agent in a separate exercise and record retrieval enabled/disabled conditions, citations, exact quotes, refusals and false-premise rejection. Keep research opt-in cases explicitly distinct. Record provider, client version, timestamp, model version and source evidence. The separate 60-question campaign benchmark requires its own controlled model-testing process, not this deterministic retriever checker.

## Security and failure conditions

- Public documents and untrusted research text are **data** to agents, not executable instructions.
- There is no mass book export and no private `.uai` distribution.
- Static source JSON directories **must** be denied by Apache `.htaccess`; check live site after deployment.
- HTTPS, WAF, Apache overrides and actual crawler attribution cannot be inferred from local PHP tests.
- Gold fixtures and results are private operator records. They should have minimal file permissions, access control, and a retention policy.
- A `PASS` on structural tests must never be represented as proof of AI model learning or search indexing.
