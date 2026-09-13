# nitpicky

A pre-launch visual walkthrough skill for [Claude Code](https://claude.com/claude-code):
parallel review agents walk your entire running app — one concern each — screenshot
every page and state, and report the little defects that get normalized during a build.
You triage the findings in a local decision portal (fix / deny / defer, with your
explanation), and the export is a checklist an implementation team can execute.

## How it works

1. **Walk** — five lens agents (consistency, friction, verbose language, visual polish,
   accessibility) each walk the whole app in their own isolated browser, screenshotting
   proof for every finding. Contracts: [`lib/lenses.md`](lib/lenses.md),
   [`lib/findings-schema.md`](lib/findings-schema.md).
2. **Merge** — findings are validated, assigned content-hash ids (stable across
   re-merges), cross-lens near-duplicates are clustered, byte-identical screenshots
   across lenses are flagged as contaminated evidence, route coverage is aggregated,
   configured secrets are scrubbed, and a run-health summary names suspected
   server-side noise. [`lib/merge-findings.py`](lib/merge-findings.py)
3. **Triage** — a local portal server serves a review page; every decision writes
   atomically to `decisions.json` on disk. A browser draft queue survives server
   outages behind a Retry button. Bulk actions apply one decision to the whole
   filtered set; clustered duplicates take one click. Export writes `CHECKLIST.md`
   into the run directory. ([`lib/server.py`](lib/server.py),
   [`review/template.html`](review/template.html))
4. **Hand off** — the checklist carries each accepted finding's evidence, expected
   behavior, and your verbatim context, grouped Fix / Deferred / Denied.

## Install

```bash
git clone https://github.com/masharratt/nitpicky.git ~/projects/nitpicky
ln -s ~/projects/nitpicky ~/.claude/skills/nitpicky
```

Requires: `python3` (stdlib only), bash 4+, and a Playwright-capable browser for the
walkthrough agents. The portal is loopback-only by design — single reviewer, local
files.

## Usage

In Claude Code, invoke the skill:

```
/nitpicky <app-url-or-project-dir>
```

The coordinator resolves the app URL, verifies the data path, scaffolds a run
directory at `<project>/planning/nitpicky/<timestamp>/`, spawns the lens agents,
merges, and opens the portal in your browser.

## Development

```bash
bash tests/test-nitpicky.sh   # 70 assertions: merge, ids, server, validation, export
```

CI runs shellcheck and the test suite on every push.

## License

[MIT](LICENSE)
