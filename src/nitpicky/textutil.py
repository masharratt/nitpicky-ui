"""Shared text-similarity helpers for merge matching and memory lookup."""
import re
from urllib.parse import urlparse

CLUSTER_JACCARD = 0.6


def norm_tokens(text: str) -> frozenset:
    return frozenset(re.findall(r"[a-z0-9]+", text.lower()))


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def route_of(url: str) -> str:
    try:
        return urlparse(url).path or "/"
    except Exception:
        return "/"
