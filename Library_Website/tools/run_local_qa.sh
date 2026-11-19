#!/usr/bin/env bash
# Hermetic-ish local release gate: serve a disposable copy so crawler monitoring
# never writes runtime state into the release artifact being validated.
set -euo pipefail
# Keep both working tree and generated archives free of Python bytecode artifacts.
export PYTHONDONTWRITEBYTECODE=1
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/eviulon-release-qa-XXXXXXXX")"
PID=""
cleanup() {
  if [[ -n "$PID" ]]; then kill "$PID" 2>/dev/null || true; wait "$PID" 2>/dev/null || true; fi
  rm -rf "$TMP"
}
trap cleanup EXIT INT TERM
command -v php >/dev/null || { echo 'PHP CLI is required'; exit 1; }
command -v python3 >/dev/null || { echo 'Python 3 is required'; exit 1; }
echo '1/15 Static corpus and content integrity'
php "$ROOT/tools/build_api_snapshots.php" --check
python3 "$ROOT/tools/build_static_delivery_manifest.py" --check
python3 "$ROOT/tools/verify_content_integrity.py" --root "$ROOT"
python3 "$ROOT/tools/validate_release.py" --root "$ROOT"
python3 "$ROOT/tools/validate_discovery.py" --root "$ROOT"
python3 "$ROOT/tools/test_semantic_metadata.py" --root "$ROOT"
echo '2/15 Syntax checking PHP'
while IFS= read -r -d '' file; do php -l "$file" >/dev/null; done < <(find "$ROOT" -type f -name '*.php' -print0)
echo '3/15 IndexNow no-network unit tests'
python3 "$ROOT/tools/test_indexnow.py"
python3 "$ROOT/tools/test_evidence_ledger.py"
python3 "$ROOT/tools/evidence_ledger.py"
echo '4/15 Create isolated HTTP fixture copy'
mkdir -p "$TMP/site"
cp -a "$ROOT/." "$TMP/site/"
PORT="$(python3 - <<'PY'
import socket
with socket.socket() as s:
  s.bind(('127.0.0.1',0))
  print(s.getsockname()[1])
PY
)"
QA_PASSWORD_HASH="$(php -r 'echo password_hash("qa-only-not-for-production-8675309",PASSWORD_DEFAULT);')"
EVIULON_MONITOR_ENABLED=1 EVIULON_MONITOR_PASSWORD_HASH="$QA_PASSWORD_HASH" EVIULON_MONITOR_USER=admin php -S "127.0.0.1:$PORT" -t "$TMP/site" "$TMP/site/router.php" >"$TMP/server.log" 2>&1 &
PID=$!
export EVIULON_QA_URL="http://127.0.0.1:$PORT"
python3 - <<'PY'
import os,time,urllib.request
url=os.environ['EVIULON_QA_URL']
for _ in range(60):
 try:
  with urllib.request.urlopen(url,timeout=2) as response:
   assert response.status==200
  break
 except Exception:time.sleep(.1)
else:raise SystemExit('QA server failed to start')
PY
echo '5/15 Existing search/API/AG-UI contract'
python3 "$ROOT/tools/validate_agent_api.py" --http "$EVIULON_QA_URL"
python3 "$ROOT/tools/test_static_delivery.py" --http "$EVIULON_QA_URL" --all
python3 "$ROOT/tools/test_research_navigation.py" --root "$ROOT" --http "$EVIULON_QA_URL"
echo '6/15 Independent pagination and exact source-filter facets'
python3 "$ROOT/tools/test_independent_search.py" --http "$EVIULON_QA_URL"
python3 "$ROOT/tools/test_faceted_search.py" --http "$EVIULON_QA_URL"
php "$ROOT/tools/test_research_links.php"
python3 "$ROOT/tools/test_research_links_http.py" --http "$EVIULON_QA_URL"
echo '7/15 Discovery/HTTP security + all 1,925 official pages'
python3 "$ROOT/tools/validate_discovery.py" --root "$ROOT" --http "$EVIULON_QA_URL" --full-pages
python3 "$ROOT/tools/test_semantic_metadata.py" --root "$ROOT" --http "$EVIULON_QA_URL"
echo '8/15 Retrieval quality, private gold boundaries, and chapter ranking'
python3 "$ROOT/tools/test_retrieval_quality.py"
python3 "$ROOT/tools/retrieval_quality.py" --http "$EVIULON_QA_URL" --root "$ROOT" --smoke
mkdir -p "$TMP/private"
python3 "$ROOT/tools/generate_private_retrieval_suite.py" --root "$ROOT" --out "$TMP/private/source-probes.json"
python3 "$ROOT/tools/retrieval_quality.py" --http "$EVIULON_QA_URL" --root "$ROOT" \
  --suite "$TMP/private/source-probes.json" --out "$TMP/private/source-probe-results.json"
python3 "$ROOT/tools/test_chapter_relevance.py" --http "$EVIULON_QA_URL" --root "$ROOT"
echo '9/15 Agent answer evaluation rubric, privacy, and private draft suite'
python3 "$ROOT/tools/test_agent_answer_benchmark.py"
python3 "$ROOT/tools/test_agent_pilot.py"
python3 "$ROOT/tools/generate_agent_answer_draft.py" --root "$ROOT" \
  --out "$TMP/private/unapproved-50-cases.json"
python3 "$ROOT/tools/agent_answer_benchmark.py" validate-suite --root "$ROOT" \
  --suite "$TMP/private/unapproved-50-cases.json"
python3 "$ROOT/tools/agent_answer_benchmark.py" prepare --root "$ROOT" \
  --suite "$TMP/private/unapproved-50-cases.json" --out "$TMP/private/blank-responses.json"
python3 "$ROOT/tools/agent_answer_benchmark.py" prepare-reviews --root "$ROOT" \
  --suite "$TMP/private/unapproved-50-cases.json" \
  --answers "$TMP/private/blank-responses.json" --out "$TMP/private/blank-reviews.json"
echo '10/15 Bounded exact source evidence, authority, quote fidelity, AG-UI'
php "$ROOT/tools/test_source_evidence_unit.php"
python3 "$ROOT/tools/test_source_evidence.py" --http "$EVIULON_QA_URL"
echo '11/15 Bounded local read-only agent production readiness'
python3 "$ROOT/tools/live_agent_readiness.py" --base-url "$EVIULON_QA_URL"
echo '12/15 Modern stateless MCP 2026-07-28 protocol, security and retrieval'
python3 "$ROOT/tools/test_mcp.py" --http "$EVIULON_QA_URL"
echo '13/15 Private monitoring and evidence export' 
python3 "$ROOT/tools/validate_observability.py" --http "$EVIULON_QA_URL" --fixture-root "$TMP/site"
echo '14/15 Evidence ledger enforcement and static source integrity'
python3 "$ROOT/tools/verify_content_integrity.py" --root "$ROOT"
echo '15/15 Complete legacy route + static corpus check, release root remains uncontaminated'
python3 "$ROOT/tools/validate_release.py" --root "$ROOT" --http "$EVIULON_QA_URL"
echo 'PASS: All local release gates passed. No HTTP test logs were written to release root.'
