"""Convert an axe-core results JSON into nitpicky lens findings.

Input: the JSON produced by axe.run() / axe-core CLI / webdriver axe export —
any object with a `violations` array of {id, impact, help, description, nodes}.
Output: a lens findings doc (lens: "axe") ready for `nitpicky merge`.

Findings carry no screenshot; the portal marks them proof-broken. Capture the
page yourself (or run the axe scan through a nitpicky walkthrough agent) for
visual evidence.
"""
import argparse
import json
import sys
from pathlib import Path

IMPACT_SEVERITY = {
    "critical": "high",
    "serious": "high",
    "moderate": "medium",
    "minor": "low",
    None: "medium",
    "": "medium",
}


def convert(doc: dict, url: str) -> dict:
    findings = []
    for v in doc.get("violations", []):
        nodes = v.get("nodes") or []
        what = v.get("help") or v.get("id") or "accessibility violation"
        if nodes:
            what = f"{what} ({len(nodes)} element(s))"
        expected = v.get("description") or v.get("help") or "No axe violations"
        findings.append({
            "what": what,
            "expected": expected,
            "url": url,
            "severity": IMPACT_SEVERITY.get(v.get("impact"), "medium"),
            "area": "axe-core",
            "steps": f"axe rule '{v.get('id')}'; targets: "
                     + "; ".join((n.get("target") and " ".join(map(str, n["target"])) or "")
                                 for n in nodes[:3]),
            "screenshot": f"screenshots/axe-{v.get('id', 'violation')}.png",
        })
    return {"lens": "axe", "findings": findings}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="nitpicky import-axe")
    ap.add_argument("report")
    ap.add_argument("--url", required=True)
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args(argv)

    doc = json.loads(Path(args.report).read_text())
    out = convert(doc, args.url)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(f"nitpicky-import-axe: {len(out['findings'])} findings -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
