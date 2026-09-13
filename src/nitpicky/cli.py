"""nitpicky command-line interface.

Works standalone on any folder of findings JSON — no agent required to merge,
triage, or export. Lens agents are one (optional) way to produce findings; see
lib/findings-schema.md and schema/lens-findings.schema.json for the contract.
"""
import argparse
import sys
from pathlib import Path

from nitpicky import __version__


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="nitpicky",
        description="Pre-launch visual walkthrough: merge findings, triage in a "
                    "local portal, export a hand-off checklist.")
    ap.add_argument("--version", action="version", version=f"nitpicky {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="scaffold a run directory")
    p_init.add_argument("project_root")
    p_init.add_argument("app_url")
    p_init.add_argument("--routes-file", default=None)
    p_init.add_argument("--redact-file", default=None)

    p_merge = sub.add_parser("merge", help="validate + merge lens findings JSONs")
    p_merge.add_argument("--run-dir", required=True)

    p_review = sub.add_parser("review", help="serve the triage portal")
    p_review.add_argument("run_dir")
    p_review.add_argument("--port", type=int, default=0, help="0 = pick a free port")

    p_export = sub.add_parser("export", help="write CHECKLIST.md from saved decisions")
    p_export.add_argument("run_dir")
    p_export.add_argument("--decisions", default=None,
                          help="decisions JSON file (default: <run-dir>/decisions.json)")
    p_export.add_argument("-o", "--out", default=None)

    p_axe = sub.add_parser("import-axe", help="convert an axe-core report to findings")
    p_axe.add_argument("report")
    p_axe.add_argument("--url", required=True, help="page URL the report was run on")
    p_axe.add_argument("-o", "--out", required=True, help="output lens findings JSON")

    p_lh = sub.add_parser("import-lighthouse",
                          help="convert a Lighthouse accessibility report to findings")
    p_lh.add_argument("report")
    p_lh.add_argument("--url", required=True)
    p_lh.add_argument("-o", "--out", required=True)

    args = ap.parse_args(argv)

    if args.cmd == "init":
        from nitpicky import scaffold
        return scaffold.init([args.project_root, args.app_url,
                              *(["--routes-file", args.routes_file] if args.routes_file else []),
                              *(["--redact-file", args.redact_file] if args.redact_file else [])])
    if args.cmd == "merge":
        from nitpicky import merge
        return merge.main(["--run-dir", args.run_dir])
    if args.cmd == "review":
        from nitpicky import portal
        return portal.main(["--run-dir", args.run_dir, "--port", str(args.port)])
    if args.cmd == "export":
        from nitpicky import checklist
        return checklist.main(["--run-dir", args.run_dir,
                               "--decisions", args.decisions
                               or str(Path(args.run_dir) / "decisions.json"),
                               *(["-o", args.out] if args.out else [])])
    if args.cmd == "import-axe":
        from nitpicky.adapters import axe
        return axe.main([args.report, "--url", args.url, "-o", args.out])
    if args.cmd == "import-lighthouse":
        from nitpicky.adapters import lighthouse
        return lighthouse.main([args.report, "--url", args.url, "-o", args.out])
    return 2


if __name__ == "__main__":
    sys.exit(main())
