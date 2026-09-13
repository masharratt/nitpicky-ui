#!/usr/bin/env bash
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=python3
NIT="env PYTHONPATH=$REPO/src $PY -m nitpicky.cli"
TMP="$(mktemp -d)"
mkdir -p "$TMP/proj"
RUN_A="$("$NIT" init "$TMP/proj" 'http://localhost:3000')"
echo "CAPTURED=[$RUN_A]"
