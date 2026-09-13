# Changelog

All notable changes to nitpicky.

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
