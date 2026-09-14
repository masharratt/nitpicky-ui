#!/usr/bin/env bash
# Watch a nitpicky run's submissions.jsonl and emit each Submit event.
#
# Usage: submit-watcher.sh [--once | --follow] <run-dir>
#   --once   exit after emitting the first new submission (use as a background
#            task: its completion re-invokes the Claude session that armed it)
#   --follow keep running, emit every new submission (use with the Monitor tool)
#
# Each event is one JSON line: {"event":"submit","at":...,"ids":[...]}
# Lines are consumed by offset, so restarts never miss or replay events.
set -uo pipefail

MODE="--once"
[ "$1" = "--once" ] || [ "$1" = "--follow" ] && { MODE="$1"; shift; }
[ $# -eq 1 ] || { echo "usage: submit-watcher.sh [--once|--follow] <run-dir>" >&2; exit 2; }
RUN_DIR="$1"
SUBMISSIONS="$RUN_DIR/submissions.jsonl"

SEEN=0
if [ -f "$SUBMISSIONS" ]; then
  SEEN="$(grep -c '' "$SUBMISSIONS" 2>/dev/null || echo 0)"
fi

emit_new() {
  local total now_line
  total="$(grep -c '' "$SUBMISSIONS" 2>/dev/null || echo 0)"
  if [ "$total" -gt "$SEEN" ]; then
    tail -n +"$((SEEN + 1))" "$SUBMISSIONS"
    SEEN="$total"
    return 0   # something was emitted
  fi
  return 1
}

while true; do
  if emit_new; then
    if [ "$MODE" = "--once" ]; then
      exit 0
    fi
  fi
  sleep 2
done
