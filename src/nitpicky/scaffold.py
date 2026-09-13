"""Scaffold a nitpicky run directory (port of the original new-run.sh)."""
import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path


def _lines(path: str | None) -> list:
    if not path:
        return []
    return [line.strip() for line in Path(path).read_text().splitlines() if line.strip()]


def init(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(prog="nitpicky init",
                                 description="Create a run directory scaffold")
    ap.add_argument("project_root")
    ap.add_argument("app_url")
    ap.add_argument("--routes-file", default=None,
                    help="one route per line; becomes coverage.expected")
    ap.add_argument("--redact-file", default=None,
                    help="one secret per line; merge + export scrub these")
    args = ap.parse_args(argv)

    root = Path(args.project_root)
    if not root.is_dir():
        print(f"nitpicky init: not a directory: {root}", file=sys.stderr)
        return 2

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = root / "planning" / "nitpicky" / run_id
    if run_dir.exists():
        run_dir = Path(f"{run_dir}-{random.randint(0, 99999)}")
    (run_dir / "findings").mkdir(parents=True)
    (run_dir / "screenshots").mkdir()

    doc = {
        "run_id": run_dir.name,
        "app_url": args.app_url,
        "created": datetime.now(timezone.utc).isoformat(),
        "coverage": {"expected": _lines(args.routes_file)},
        "redactions": _lines(args.redact_file),
    }
    (run_dir / "run.json").write_text(json.dumps(doc, indent=2) + "\n")
    print(run_dir)
    return 0
