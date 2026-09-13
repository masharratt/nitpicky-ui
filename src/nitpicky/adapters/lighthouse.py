"""Convert a Lighthouse accessibility report into nitpicky lens findings.

Input: a Lighthouse JSON report (v7+) — uses the accessibility category's
weighted audits that scored below 1. Output: a lens findings doc
(lens: "lighthouse") ready for `nitpicky merge`.

Findings carry no screenshot; the portal marks them proof-broken.
"""
import argparse
import json
import re
import sys
from pathlib import Path

def _severity(score) -> str:
    if score is not None and score <= 0:
        return "high"
    if score is not None and score <= 0.5:
        return "medium"
    return "low"


def _first_sentence(text: str) -> str:
    match = re.match(r"(.+?\.)\s", text or "")
    return (match.group(1) if match else text or "").strip()


def convert(doc: dict, url: str) -> dict:
    audits = doc.get("audits", {})
    refs = {}
    for ref in (doc.get("categories", {}).get("accessibility", {}).get("auditRefs") or []):
        refs[ref.get("id")] = ref.get("weight", 0)

    findings = []
    for audit_id, audit in audits.items():
        score = audit.get("score")
        if score is None or score >= 1:
            continue
        if refs.get(audit_id, 0) <= 0:
            continue  # unweighted/informational audit
        what = audit.get("title") or audit_id
        display = audit.get("displayValue")
        if display:
            what = f"{what} ({display})"
        findings.append({
            "what": what,
            "expected": _first_sentence(audit.get("description", "")) or "Audit passes",
            "url": doc.get("finalDisplayedUrl") or url,
            "severity": _severity(score),
            "area": "lighthouse",
            "steps": f"lighthouse audit '{audit_id}'",
            "screenshot": f"screenshots/lighthouse-{audit_id}.png",
        })
    return {"lens": "lighthouse", "findings": findings}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="nitpicky import-lighthouse")
    ap.add_argument("report")
    ap.add_argument("--url", required=True)
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args(argv)

    doc = json.loads(Path(args.report).read_text())
    out = convert(doc, args.url)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(f"nitpicky-import-lighthouse: {len(out['findings'])} findings -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
