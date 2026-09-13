#!/usr/bin/env bash
# Tests for the nitpicky CLI (init/merge/review/export) and the axe/lighthouse adapters.
# Run: bash tests/test-cli-adapters.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=python3
nit() { PYTHONPATH="$REPO/src" $PY -m nitpicky.cli "$@"; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0
ok() { PASS=$((PASS + 1)); }
fail() { FAIL=$((FAIL + 1)); echo "FAIL: $*"; }
assert_eq() {
  if [[ "$1" == "$2" ]]; then ok; else fail "$3: expected [$2], got [$1]"; fi
}
assert_contains() {
  if grep -qF -- "$2" <<<"$1"; then ok; else fail "$3: missing [$2]"; fi
}

# A1: cli init scaffolds a run dir (the pip-installed code path)
mkdir -p "$TMP/proj"
RUN_A="$(nit init "$TMP/proj" 'http://localhost:3000')"
[ -n "$RUN_A" ] && [ -d "$RUN_A/findings" ] && ok || fail "A1 init did not scaffold"
grep -q '"app_url": "http://localhost:3000"' "$RUN_A/run.json" && ok || fail "A1 run.json missing app_url"

# A2: axe adapter output merges cleanly
nit import-axe tests/fixtures/axe-sample.json --url 'http://localhost:3000/signup' -o "$RUN_A/findings/axe.json" >/dev/null
MERGE_A="$(nit merge --run-dir "$RUN_A" 2>&1)"
assert_eq "$?" "0" "A2 merge exit with axe findings"
assert_contains "$MERGE_A" "axe=3" "A2 three axe findings counted"
assert_contains "$MERGE_A" "missing-screenshots=[" "A2 missing axe screenshots named"
"$PY" - "$RUN_A" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1] + "/findings.json"))
sev = sorted(f["severity"] for f in d["findings"] if f["lens"] == "axe")
assert sev == ["high", "low", "medium"], sev  # critical->high, moderate->medium, minor->low
EOF
[ $? = 0 ] && ok || fail "A2 severity mapping wrong"

# A3: lighthouse adapter — weighted failing audits only, null-score skipped
nit import-lighthouse tests/fixtures/lighthouse-sample.json --url 'http://localhost:3000/signup' -o "$RUN_A/findings/lighthouse.json" >/dev/null
"$PY" - "$RUN_A" <<'EOF'
import json, sys
doc = json.load(open(sys.argv[1] + "/findings/lighthouse.json"))
ids = sorted(f["what"] for f in doc["findings"])
assert len(doc["findings"]) == 2, ids            # passing + notApplicable audits excluded
assert any("2 elements found" in w for w in ids), ids
assert all(f["severity"] in ("high", "medium") for f in doc["findings"])
EOF
[ $? = 0 ] && ok || fail "A3 lighthouse mapping wrong"

# A4: cli export writes the checklist from decisions
DEC="$RUN_A/decisions.json"
IDS="$("$PY" -c "import json;d=json.load(open('$RUN_A/findings.json'));print(' '.join(f['id'] for f in d['findings'] if f['lens']=='axe'))" | tr ' ' '\n' | head -2 | tr '\n' ' ')"
read -r ID1 ID2 _ <<<"$IDS"
"$PY" - "$DEC" "$ID1" "$ID2" <<'EOF'
import json, sys
i1, i2 = sys.argv[2], sys.argv[3]
json.dump({i1: {"decision": "fix", "explanation": "ship blocker"},
           i2: {"decision": "deny", "explanation": "by design"}},
          open(sys.argv[1], "w"))
EOF
nit export "$RUN_A" >/dev/null && ok || fail "A4 export command failed"
grep -q '^## Fix (1)' "$RUN_A/CHECKLIST.md" && ok || fail "A4 checklist missing Fix"
grep -q 'ship blocker' "$RUN_A/CHECKLIST.md" && ok || fail "A4 explanation lost"

# A5: examples demo run validates against the published schema (jsonschema optional)
if "$PY" -c "import jsonschema" 2>/dev/null; then
  "$PY" - <<'EOF'
import json, glob
from jsonschema import validate
schema = json.load(open("schema/lens-findings.schema.json"))
for path in glob.glob("examples/demo-run/findings/*.json"):
    validate(json.load(open(path)), schema)
print("examples validated")
EOF
  [ $? = 0 ] && ok || fail "A5 examples failed schema validation"
else
  echo "A5 skipped (jsonschema not installed)"
fi

echo ""
echo "passed=$PASS failed=$FAIL"
[ "$FAIL" = "0" ]
