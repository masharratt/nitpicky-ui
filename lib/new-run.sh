#!/usr/bin/env bash
# Create a nitpicky run directory scaffold. Implementation: src/nitpicky/scaffold.py.
# Usage: new-run.sh <project-root> <app-url> [--routes-file <file>] [--redact-file <file>]
set -euo pipefail
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
exec python3 -c "import sys; sys.path.insert(0, '$HERE/../src'); from nitpicky.cli import main; sys.exit(main())" init "$@"
