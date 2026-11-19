# Agent Answer Evaluation Contract — v3.6

**Scope:** independently reviewed answers to questions about the **14 official Eviulon books**. Supplemental Eviulon/Evulgare research is excluded by default and may be separately opted into. **Status:** tooling implemented and tested locally; no real third-party agent has been scored by this release. **Cost:** $0 incremental; Python standard library and existing site data.

## Why this is a separate track

The *Eviulon AI Access Architecture* report proposes a 50-question human-evaluated test across direct facts, misattribution, negative/false-premise queries, chapter citations, and disagreement/uncertainty. The *AI Content Discoverability Campaign* proposes a distinct 60-question blind assessment and warns that publishing question/answer keys creates benchmark contamination. The existing v3.5 Hit@5/quote checks only establish deterministic **retrieval** and source fidelity. This contract assesses **actual written answers** only after independently created, source-confirmed gold notes and blinded human reviews.

### Three separable evidence layers

1. **Structural citation checks (automatic):** exact `https://library.eviulon.com/{book-slug}/{print-page}/` or supplemental `/research/{group}/{slug}/{section}/` URL, source record exists, response stayed within selected sources, verbatim quotations actually appear on the cited page, and at least one citation reaches the designated gold source where required. This does not prove an argument is supported by a quote.
2. **Semantic adjudication (humans):** two independent blinded reviewers assess whether the answer is supported by those sources, whether it preserves the book-versus-research authority distinction, rejects misleading premises, and expresses uncertainty appropriately. Each must enter a written source-grounded rationale. Disagreements require adjudication. A boolean `blind:true` is an operator attestation, not a technical proof of blinding.
3. **Training and indexing evidence (separate):** neither a strong score nor a retrieval-disabled answer proves training on this library. Index coverage, verified crawlers, dataset membership, or parameter training require their own evidence.

## Files and privacy boundary

All **question suites, expected sources, gold notes, model transcripts, individual reviews, adjudication decisions, and evaluation reports** belong outside the public website document root and public GitHub. The evaluator resolves symlinks, rejects private inputs/outputs under the site root, requires explicit private parent directories, refuses to overwrite existing results, limits JSON size to 2 MB and saves outputs with mode 0600. It does not call external model APIs or transmit gold material over a network.

The public website archive ships only tools, public methodology, and deterministic unit-test code. The separate private operator archive contains **50 unapproved draft candidates**, not an authoritative benchmark and not third-party model results.

## Question development: exactly five categories

- **Direct facts:** accurately state what a cited book passage actually says, without inventing facts.
- **Misattribution:** distinguish official authored Eviulon book arguments from supplemental research and externally verified facts.
- **False premise:** reject false or unsupported framing rather than agree with a leading question.
- **Chapter citation:** find the correct original opening print page and give an accurate canonical citation, not a made-up chapter number.
- **Uncertainty:** distinguish the author's arguments, speculations, and unresolved questions from definitive claims.

The provided draft generator creates **ten candidates per category** from source-verified chapter headings across the books. Those headings merely suggest source locations. The generated questions and target pages **must be individually reviewed by a human** before setting `approved:true` and adding an independently checked `reviewer_gold_notes` explanation (at least 15 characters). A page containing a heading does not guarantee that the passage supports a question's premise.

## Zero-cost workflow

Use a **private local folder outside the website**; example paths below are illustrative:

```bash
# Build 50 PRIVATE draft prompts. All cases begin approved=false.
python3 tools/generate_agent_answer_draft.py --out /secure/eviulon/50-draft.json
python3 tools/agent_answer_benchmark.py validate-suite --suite /secure/eviulon/50-draft.json

# Owner inspects the source pages, finalizes questions and gold, and signs off.
# This must FAIL until every case is approved and its gold rationale is substantive.
python3 tools/agent_answer_benchmark.py validate-suite --strict --suite /secure/eviulon/50-approved.json

# Generate a blank answer/transcript collection sheet for a single agent run.
python3 tools/agent_answer_benchmark.py prepare \
  --suite /secure/eviulon/50-approved.json --out /secure/eviulon/run_A_answers.json

# Manually ask those questions in a real agent client. Capture answers and their
# canonical citations verbatim. Record client/model/version, UTC timestamp,
# source-access method, and whether web retrieval is enabled/disabled/unknown.
# Fill the answers file yourself; NEVER pretend a model ran if it did not.

# Create a blank dual-review worksheet for the filled transcript.
python3 tools/agent_answer_benchmark.py prepare-reviews \
  --suite /secure/eviulon/50-approved.json --answers /secure/eviulon/run_A_answers.json \
  --out /secure/eviulon/run_A_reviews.json

# Independent reviewers assess answers against the original sources.
# Fill all rubric scores and reasons, adjudicate disagreements, then score.
python3 tools/agent_answer_benchmark.py score \
  --suite /secure/eviulon/50-approved.json \
  --answers /secure/eviulon/run_A_answers.json \
  --reviews /secure/eviulon/run_A_reviews.json \
  --out /secure/eviulon/run_A_report.json
```

For a second independent run, create another answers file and review file. Keep retrieval-enabled versus retrieval-disabled results **separate**. If the agent client cannot reliably disable retrieval, use `retrieval_mode:"unknown"` rather than asserting isolation. Never paste hidden gold notes into model prompts during a blind test.

## Versioned data contracts

All inputs use `schema_version:"1.0"` and matching `benchmark_id` and `run_id`. A suite case contains `id`, `category`, `question`, `scope` (`["books"]` by default), `requires_citation`, `expected_sources` (canonical source URLs), `approved` and `reviewer_gold_notes`.

An agent transcript contains the `run` metadata (`client`, `model`, `model_version`, UTC timestamp, retrieval mode and research opt-in) plus one `answer` and `citations` array per case. Citations may include an optional verbatim `quote`; that literal is checked against the original source text stored on the owner-controlled local site copy. Do not use snapshots of webpages with altered quotes or rely on the model's assertion that the quote exists.

The dual-review worksheet requires exactly two distinct reviewer IDs. Each case is independently scored from **0 (fails), 1 (partial), 2 (passes)** on:

- `grounding` and `citation_support` for every question;
- `authority_separation` for misattribution cases;
- `premise_rejection` for false-premise cases;
- `uncertainty_calibration` for uncertainty cases.

Both reviewers must include substantive reasons. Any disagreement triggers `needs_adjudication`, with the overall aggregate withheld until an explicit third-party adjudication entry resolves it. Mechanical citation failures are reported separately and block a clean evaluation status even if humans rate an answer highly. **No automated entailment score is calculated.**

The scorer reports input SHA-256 hashes, per-category and per-dimension rubric proportions, per-case numeric grades, citation validation flags and explicit epistemic limitations. It deliberately does **not** copy answer text or hidden gold explanations into the score report. Treat even the numeric report as a private research artifact until the owner approves release of aggregates.

## Book-first publishing rules

1. Official book pages are cited as authored Eviulon content, with exact individual print-page URL, and working-edition status preserved.
2. Research is not considered approved doctrine, must be explicitly in the case's `scope` and the agent run's `research_opt_in:true`, and must have a distinct `research/{group}/{slug}/{section}/` canonical citation. When mixed sources are cited, cite primary books before supplemental research.
3. No full PDF/EPUB downloads, private `.uai` records, or research answer keys are deployed.
4. Report only what the evidence establishes. A technically valid citation does not prove the answer's semantic entailment, and no answer score proves model training, independent statehood, or real-world empirical truth.

## Operations and failure policy

- Run `bash tools/run_local_qa.sh` before a release. It includes 23 synthetic unit checks, a **private and unapproved** 50-case template generated in a disposable location, all prior site/API gates and full canonical print-page coverage.
- The scorer rejects unapproved gold, absent or duplicated cases, invalid/missing source metadata, non-HTTPS/noncanonical/external citation URLs, source scope violations, invalid literal quotes, insufficient blinded review coverage, missing adjudication, and private path traversal.
- The benchmark is not an online endpoint. Never send user-supplied text to a paid API, execute it as code, or publish the private evaluation files.
- If source and metadata do not agree, pause scoring and correct the private gold **without changing the canonical book text**. If the agent hallucinates a citation, keep the failure in the evidence ledger rather than fixing the answer on its behalf.

## Future independent pilot

Run one small, genuinely external agent pilot (with explicit model/version and retrieval mode), adjudicate it, then scale to 50 approved questions. The separate 60-case *AI Content Discoverability Campaign* is an optional later study. The current v3.6 package provides the **evaluation infrastructure and unapproved authoring material only**; it does not claim that a model was independently benchmarked.
