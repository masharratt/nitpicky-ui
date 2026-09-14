# Changelog

All notable changes to nitpicky.

## 1.6.0 — 2026-09-14

Cross-run decision memory: repeated runs stop re-flagging what you already settled.

- Decisions recorded per app on export/submit to `planning/nitpicky/memory.json`
  (route + finding text + decision + your explanation).
- Merge matches new findings against memory (route + token overlap, same rule as
  clustering) and annotates matches; run summary names the counts.
- Portal hides previously denied/deferred findings by default with a
  "Show N previously decided" toggle; previously fixed findings stay visible with
  an annotation (a re-report after a fix may be a regression signal).

## 1.5.0 — 2026-09-14

Submit-to-agent: the portal can now wake the reviewing session.

- **Submit to agent** button (server mode): hands only new-or-changed decisions
  to the session watching the run — per-finding fingerprints
  (`submit-state.json`) make repeated clicks idempotent, changed decisions
  resubmit, unchanged ones are skipped and counted.
- Each Submit appends an event to `submissions.jsonl`.
- **`lib/submit-watcher.sh`**: session-side wake-up — `--once` as a background
  task (completion notification wakes the session), `--follow` for per-event
  streaming.
- `GET /api/submit/status` reports the pending-new count.

## 1.4.0 — 2026-09-13

## 1.4.0 — 2026-09-13

Standalone product release: the pipeline no longer requires Claude Code.

- **`nitpicky` CLI** (`init` / `merge` / `review` / `export`): the full pipeline on
  any findings folder, installable via pipx.
- **Published findings JSON Schema** (`schema/lens-findings.schema.json`): emit
  findings from any tool or agent; merge consumes them.
- **axe-core adapter** (`nitpicky import-axe`): impact-to-severity mapping.
- **Lighthouse adapter** (`nitpicky import-lighthouse`): weighted failing
  accessibility audits only.
- **`examples/demo-run`**: a complete pre-triaged run — `nitpicky review
  examples/demo-run` for a 60-second tour.
- Implementation moved to `src/nitpicky/` package; `lib/` scripts remain as shims
  so existing skill invocations and relative paths keep working.

## 1.3.0 — 2026-09-13

First live-run feedback (a 172-finding run):

- Mandatory per-agent browser isolation; mechanical duplicate-evidence detection
  (byte-identical screenshots across lens prefixes = contaminated capture).
- Data-path pre-flight before spawning (login + one real surface, not just a
  landing-page 200).
- Coverage manifest: expected routes + per-agent coverage block; merge names
  uncovered routes for targeted re-briefs.
- Cross-lens near-duplicate clustering with apply-to-cluster in the portal.
- Live-target safety stanza for non-localhost targets.
- Mechanical credential redaction at merge and export.
- `suspected_env_cause` findings, portal filter, run-health summary.
- Bulk actions on the filtered set (fix/defer/deny) with confirm + optional note.

## 1.1.0 — 2026-09-12

Decision portal server: decisions write atomically to `decisions.json` per click;
browser draft queue survives outages behind a Retry button; export writes the
checklist directly into the run directory.

## 1.0.0 — 2026-09-12

Initial release: five lens agents, screenshot-proof findings, static triage page,
checklist export.
