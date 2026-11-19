# Zero-Cost Independent Agent Pilot — v3.7

## Purpose and evidence boundaries

This phase makes it possible to run **real, independently observed external agent evaluations** without a paid model API or external service. **It does not itself run an external agent, approve gold answers, perform blinded reviews or establish model training.** The existing v3.6 private scorer remains the authority for structural citation and two-reviewer evaluation. The books are approved authored Eviulon content; the research archive is supplemental and not official doctrine.

## Prerequisite: verify the actual deployed site

On any owner-controlled computer with Python 3.10+, after the website release is deployed:

```bash
python3 tools/live_agent_readiness.py --base-url https://library.eviulon.com \
  --report-out /secure/operator/readiness-2026-11-18.json
```

The output report is a private, local, mode-0600 JSON document. The tool uses bounded **GET only** requests and accepts only the canonical production HTTPS host or an explicit loopback development server. It rejects external redirects, exposed internal paths and inconsistent book/research defaults. It does not fetch IPs, log user search queries, query external search indices or send data to model providers. A passing check proves only that the listed public endpoints and protections behaved as expected at that moment. A red result is a **deployment stop** until investigated.

You may run `--base-url http://127.0.0.1:PORT` to validate a local PHP development server. It is not a substitute for production Apache, TLS, proxy, indexing or crawler verification.

## Private question approval

The separate private v3.6 package contains **50 unapproved draft questions**, ten in each of five categories. An owner/reviewer must examine the original page(s), correct any unsupported question premises, write a source-backed explanation, and explicitly approve the selected questions before pilot generation. **Do not simply flip all 50 approval flags.** A heading is a navigation anchor, not a verified answer.

## Prepare a 10-question independent pilot

The pilot command selects **two approved questions from each of five categories** (direct fact, misattribution, false premise, chapter citation and uncertainty). The selected questions' gold notes must have been reviewed. Unused draft cases may remain unapproved. All outputs are confined to a new private directory outside the website/document root:

```bash
python3 tools/agent_pilot_operator.py \
  --suite /secure/operator/PRIVATE_50_APPROVED_AS_REVIEWED.json \
  --out-dir /secure/operator/pilot-001 --per-category 2
```

The generated files are:

- `AGENT_QUESTIONS_ONLY.md`: questions and public agent instructions; **no gold notes, expected citations or answer keys**. Give only one question at a time to the tested agent.
- `PRIVATE_GOLD_SUBSET.json`: source identity and approved gold; **never upload this**.
- `agent_answers.json`: blank transcript. Fill only from actual agent responses; record client, model/version, UTC run timestamp, retrieval mode (`enabled` / `disabled` / `unknown`), literal answer and exact citations. Research opt-in is false for the default books-only questions.
- `PRIVATE_OPERATOR_GUIDE.md`: handling instructions and a digest tying this subset to its original private source.

Run the questions in a genuinely external agent client (web browsing if available), without showing the private gold. If it cannot retrieve the website, record that failure. Do not repair its answers or invent missing citations. A human operator should record the agent client's identity, exact model/version if disclosed, and retrieval capabilities actually observed, not guessed.

## Reviewer workflow

Once real answers are collected, prepare the separate blinded review form:

```bash
python3 tools/agent_answer_benchmark.py prepare-reviews \
  --suite /secure/operator/pilot-001/PRIVATE_GOLD_SUBSET.json \
  --answers /secure/operator/pilot-001/agent_answers.json \
  --out /secure/operator/pilot-001/reviews.json
```

Two **actual independent humans** review the answers with citations against the original books. They must enter distinct reviewer IDs, source-grounded explanations and all applicable 0/1/2 rubric dimensions. Disagreements require a third adjudication entry before an aggregate can be reported. A synthetic unit test or two entries filled by the same person do not count as independent review.

```bash
python3 tools/agent_answer_benchmark.py score \
  --suite /secure/operator/pilot-001/PRIVATE_GOLD_SUBSET.json \
  --answers /secure/operator/pilot-001/agent_answers.json \
  --reviews /secure/operator/pilot-001/reviews.json \
  --out /secure/operator/pilot-001/scored-report.json
```

## Interpretation and release gate

A passing citation URL check means the linked original book page exists; a quoted-text check means the literal quotation matches. Neither alone proves a complete philosophical argument is supported. Human grading supplies the independent semantic judgment. Do not publish private questions, transcripts, gold notes or identities without explicit review. A strong benchmark score does **not** establish inclusion in training data or foundation-model parameters.

Do not alter source books, print-page URL identity or research classifications in response to a low score. Treat model errors as measured results, and improve retrieval/navigation interfaces in a separately tested release if they are actually at fault.
