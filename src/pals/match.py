"""Layered matching of scorecard rows to FEC candidates."""
from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from rapidfuzz import fuzz

from .names import Name

FUZZY_THRESHOLD = 88.0


def _load_nicknames() -> dict[str, set[str]]:
    groups: dict[str, set[str]] = defaultdict(set)
    with open(Path(__file__).with_name("nicknames.csv"), newline="") as fh:
        for nick, formal in csv.reader(fh):
            for a, b in ((nick, formal), (formal, nick)):
                groups[a].add(b)
            groups[nick].add(nick)
            groups[formal].add(formal)
    return groups


NICKNAMES = _load_nicknames()


@dataclass
class Cand:
    cand_id: str
    name: Name
    state: str
    office: str
    district: str


@dataclass
class Score:
    row_id: int
    name: Name
    state: str
    office: str
    district: str


@dataclass
class Result:
    row_id: int
    status: str  # exact | relaxed | nickname | fuzzy | manual | ambiguous | unmatched
    cand_id: str | None = None
    similarity: float | None = None
    candidates: list[str] = field(default_factory=list)


def first_names_compatible(a: str, b: str) -> bool:
    if not a or not b:
        return False
    if a == b or b in NICKNAMES.get(a, ()):
        return True
    if len(a) == 1 or len(b) == 1:
        return a[0] == b[0]
    short, long = sorted((a, b), key=len)
    return len(short) >= 3 and long.startswith(short)


def _first_tokens(n: Name) -> set[str]:
    return {n.first, *n.middle[:1]} - {""}


def _last_ok(s: Score, c: Cand) -> bool:
    return c.name.last == s.name.last or c.name.last in s.name.last_variants


def _layer_exact(s: Score, c: Cand) -> bool:
    return _last_ok(s, c) and s.name.first == c.name.first \
        and s.state == c.state and s.office == c.office


def _layer_relaxed(s: Score, c: Cand) -> bool:
    return _last_ok(s, c) and s.name.first == c.name.first and s.state == c.state


def _first_compat(s: Score, c: Cand) -> bool:
    return any(first_names_compatible(a, b) for a in _first_tokens(s.name) for b in _first_tokens(c.name))


def _layer_nickname(s: Score, c: Cand) -> bool:
    return _last_ok(s, c) and s.state == c.state and s.office == c.office and _first_compat(s, c)


def _layer_crossoffice(s: Score, c: Cand) -> bool:
    """Same person running for the other chamber (e.g. House member running for Senate)."""
    return _last_ok(s, c) and s.state == c.state and _first_compat(s, c)


def _fuzzy_score(s: Score, c: Cand) -> float:
    if s.state != c.state or s.office != c.office:
        return 0.0
    if not _last_ok(s, c) and fuzz.ratio(s.name.last, c.name.last) < 85:
        return 0.0
    full_s = f"{s.name.first} {s.name.last}"
    full_c = f"{c.name.first} {c.name.last}"
    return fuzz.token_sort_ratio(full_s, full_c)


LAYERS = [
    ("exact", _layer_exact),
    ("relaxed", _layer_relaxed),
    ("nickname", _layer_nickname),
    ("cross_office", _layer_crossoffice),
]


def _pick(s: Score, hits: list[tuple[Cand, float]]) -> tuple[str, Cand | None, list[str]]:
    """Return ('ok', cand, []) or ('ambiguous', None, ids) or ('none', None, [])."""
    if not hits:
        return "none", None, []
    best = max(score for _, score in hits)
    top = [c for c, score in hits if score == best]
    if len(top) > 1:
        same_suffix = [c for c in top if c.name.suffix == s.name.suffix]
        if len(same_suffix) == 1:
            return "ok", same_suffix[0], []
        same_dist = [c for c in top if s.office == "H" and c.district == s.district]
        if len(same_dist) == 1:
            return "ok", same_dist[0], []
        return "ambiguous", None, sorted(c.cand_id for c in top)
    return "ok", top[0], []


def match_scorecard(
    scores: list[Score],
    cands: list[Cand],
    overrides: dict[int, str] | None = None,
    threshold: float = FUZZY_THRESHOLD,
) -> list[Result]:
    """Match each scorecard row to at most one candidate; one candidate per row."""
    by_id = {c.cand_id: c for c in cands}
    results: dict[int, Result] = {}
    claimed: dict[str, int] = {}

    for s in scores:
        cid = (overrides or {}).get(s.row_id)
        if cid and cid in by_id:
            results[s.row_id] = Result(s.row_id, "manual", cid, 100.0)
            claimed[cid] = s.row_id

    for status, pred in [*LAYERS, ("fuzzy", None)]:
        pending: dict[int, tuple[str, Cand | None, list[str], float]] = {}
        for s in scores:
            if s.row_id in results:
                continue
            avail = [c for c in cands if c.cand_id not in claimed]
            if pred is not None:
                hits = [(c, 100.0) for c in avail if pred(s, c)]
            else:
                hits = [(c, sc) for c in avail if (sc := _fuzzy_score(s, c)) >= threshold]
            kind, cand, ids = _pick(s, hits)
            if kind != "none":
                pending[s.row_id] = (kind, cand, ids, max((h[1] for h in hits), default=0.0))
        # two scorecard rows wanting the same candidate -> both ambiguous
        wants: dict[str, list[int]] = defaultdict(list)
        for rid, (kind, cand, _, _) in pending.items():
            if kind == "ok":
                wants[cand.cand_id].append(rid)
        for rid, (kind, cand, ids, sim) in sorted(pending.items()):
            if kind == "ok" and len(wants[cand.cand_id]) == 1:
                results[rid] = Result(rid, status, cand.cand_id, sim)
                claimed[cand.cand_id] = rid
            elif kind == "ok":
                results[rid] = Result(rid, "ambiguous", None, None, [cand.cand_id])
            else:
                results[rid] = Result(rid, "ambiguous", None, None, ids)

    return [results.get(s.row_id, Result(s.row_id, "unmatched")) for s in scores]
