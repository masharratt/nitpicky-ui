# Contributing

Small project; few rules.

## Dev loop

```bash
bash tests/test-nitpicky.sh
bash tests/test-cli-adapters.sh
shellcheck -x --severity=warning lib/*.sh tests/*.sh
```

CI runs all of it. Keep both suites green.

## Rules

- **Every finding behavior needs a test** in one of the two suites — the project's
  whole point is evidence-backed defects; don't ship unevidenced features.
- **Checks must name their failure**: a failing test says what drifted
  (`missing=[...]`, `expected X got Y`), never a bare boolean.
- Portal/server behavior changes: extend the server tests (validation, atomic
  writes, traversal) before touching `portal.py`.
- Finding ids are content hashes — changes to id derivation are breaking and need
  a CHANGELOG entry under a major bump.
- Python: stdlib only at runtime; dev/CI deps stay in CI.
- Shell: bash 4+, `set -euo pipefail`, env-bash shebang.
