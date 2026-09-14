"""Cross-run decision memory: deny/defer/fix decisions outlive individual runs.

Stored per app at <root>/planning/nitpicky/memory.json (sibling of the run
directories). Merge matches new findings against it (same route + token overlap
rule as clustering) so previously-decided defects are annotated instead of
re-litigated; the portal hides previously denied/deferred findings by default.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from nitpicky.textutil import CLUSTER_JACCARD, jaccard, norm_tokens, route_of

MEMORY_NAME = "memory.json"
DECISIONS = ("fix", "defer", "deny")


def memory_path(run_dir: Path) -> Path:
    return run_dir.parent / MEMORY_NAME


def load_entries(run_dir: Path) -> list:
    path = memory_path(run_dir)
    if not path.is_file():
        return []
    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []
    return doc.get("entries", []) if isinstance(doc, dict) else []


def match_for(finding: dict, entries: list):
    """First memory entry matching this finding: same route, token overlap >= 0.6."""
    toks = norm_tokens(finding["what"])
    route = route_of(finding["url"])
    for entry in entries:
        if entry.get("route") != route:
            continue
        if jaccard(toks, frozenset(entry.get("tokens", []))) >= CLUSTER_JACCARD:
            return entry
    return None


def record(run_dir: Path, decisions: dict, findings_by_id: dict) -> int:
    """Record final decisions into memory. Idempotent by content key.
    Returns the number of entries added."""
    path = memory_path(run_dir)
    entries = load_entries(run_dir)
    known = {e.get("key") for e in entries}
    added = 0
    for fid, rec in (decisions or {}).items():
        decision = rec.get("decision")
        if decision not in DECISIONS:
            continue
        finding = findings_by_id.get(fid)
        if not finding:
            continue
        toks = norm_tokens(finding["what"])
        route = route_of(finding["url"])
        key = hashlib.sha256(
            (" ".join(sorted(toks)) + "@" + route).encode("utf-8")).hexdigest()[:16]
        if key in known:
            continue
        entries.append({
            "key": key,
            "route": route,
            "tokens": sorted(toks),
            "what": finding["what"],
            "decision": decision,
            "explanation": rec.get("explanation", ""),
            "lens": finding.get("lens", ""),
            "decided_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        known.add(key)
        added += 1
    if added:
        path.write_text(json.dumps(
            {"version": 1, "entries": entries}, indent=2, ensure_ascii=False) + "\n")
    return added
