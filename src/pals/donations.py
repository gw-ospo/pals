"""Direct corporate-PAC contributions to candidates, binned by HRC score."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .combine import OVERRIDES, SCORECARD
from .jurisdiction import district_code, office_code, state_code
from .match import Cand, Score, first_names_compatible, match_scorecard
from .names import parse_fec_name, parse_scorecard_name

SPENDING = "big-AI-spending-2023-2026.csv"
SCORE_VINTAGE = "118th Congress (2023-24) HRC Congressional Scorecard"

PAC_SHORT_NAMES = {
    "C00227546": "Microsoft",
    "C00360354": "Amazon",
    "C00411116": "SpaceX",
    "C00428623": "Google",
    "C00502906": "Meta",
    "C00946111": "Anthropic",
}

BINS = ["0", "1-24", "25-49", "50-74", "75-99", "100", "No score"]
CYCLES = ["2024", "2026"]


def score_bin(score: float | None) -> str:
    """Assign an HRC score to its display bin; missing scores are `No score`."""
    if score is None or pd.isna(score):
        return "No score"
    if score <= 0:
        return "0"
    if score >= 100:
        return "100"
    for label, upper in (("1-24", 24), ("25-49", 49), ("50-74", 74)):
        if score <= upper:
            return label
    return "75-99"


def load_spending(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df["amount"] = pd.to_numeric(df["disbursement_amount"], errors="coerce").fillna(0.0)
    df["sub_id_num"] = pd.to_numeric(df["sub_id"], errors="coerce")
    df["pac"] = df["committee_id"].map(PAC_SHORT_NAMES).fillna(df["committee_name"])
    df["cycle"] = df["two_year_transaction_period"]
    return df


def dedupe_amendments(df: pd.DataFrame) -> pd.DataFrame:
    """Keep the latest record (max sub_id) per committee + transaction_id."""
    has_id = df["transaction_id"].notna()
    latest = (
        df[has_id].sort_values(["committee_id", "transaction_id", "sub_id_num"])
        .drop_duplicates(["committee_id", "transaction_id"], keep="last")
    )
    return pd.concat([latest, df[~has_id]]).sort_values("sub_id_num").reset_index(drop=True)


def split_direct(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (direct candidate 24K rows, other 24K rows)."""
    k24 = df[df["disbursement_type"] == "24K"]
    direct = k24[k24["candidate_id"].notna()]
    return direct, k24[k24["candidate_id"].isna()]


def candidate_totals(direct: pd.DataFrame, all_pacs: dict[str, str]) -> pd.DataFrame:
    """Net direct dollars per PAC, candidate id and cycle."""
    # Candidate attributes: take the most recent record per id
    attrs = (
        direct.sort_values("sub_id_num")
        .drop_duplicates("candidate_id", keep="last")
        .set_index("candidate_id")[
            ["candidate_name", "candidate_office", "candidate_office_state", "candidate_office_district"]
        ]
        .rename(columns=lambda c: c.replace("candidate_", "").replace("office_", ""))
        .rename(columns={"office": "office"})
    )
    attrs.columns = ["name", "office", "state", "district"]
    totals = (
        direct.groupby(["pac", "candidate_id", "cycle"])
        .agg(dollars=("amount", "sum"), contributions=("amount", "size"), sub_id_latest=("sub_id_num", "max"))
        .reset_index()
    )
    out = totals.merge(attrs, left_on="candidate_id", right_index=True, how="left")
    return out.sort_values(["pac", "cycle", "candidate_id"]).reset_index(drop=True)


def reconcile(deduped: pd.DataFrame, pacs: list[str]) -> pd.DataFrame:
    direct, other = split_direct(deduped)
    rows = []
    for pac in pacs:
        d = direct.loc[direct["pac"] == pac, "amount"].sum()
        o = other.loc[other["pac"] == pac, "amount"].sum()
        t = deduped.loc[(deduped["pac"] == pac) & (deduped["disbursement_type"] == "24K"), "amount"].sum()
        rows.append({"pac": pac, "direct_to_candidates": round(d, 2), "excluded_no_candidate": round(o, 2),
                     "total_24k_deduplicated": round(t, 2)})
    return pd.DataFrame(rows)


def _person_key(state: str, name) -> str:
    return f"{state}|{name.last}|{name.first}"


def score_recipients(
    totals: pd.DataFrame, scorecard: pd.DataFrame, overrides: pd.DataFrame
) -> pd.DataFrame:
    """Match each recipient candidate id to a scorecard row; returns one row per id."""
    sc = scorecard.reset_index(drop=True).copy()
    sc["row_id"] = sc.index
    sc["state_code"] = sc["state"].map(state_code)
    sc["office"] = sc["chamber"].map(office_code)
    sc["district_code"] = [district_code(d, o) for d, o in zip(sc["district"], sc["office"])]
    sc_objs = [Score(r.row_id, parse_scorecard_name(r.name), r.state_code, r.office, r.district_code)
               for r in sc.itertuples()]

    # One FEC id per person is not guaranteed (House then Senate committee, re-registered
    # candidates), so match people, not ids: group ids by state + normalized name.
    recips = totals.sort_values("sub_id_latest").drop_duplicates("candidate_id", keep="last")
    recips = recips[["candidate_id", "name", "office", "state", "district"]].reset_index(drop=True)
    parsed = {r.candidate_id: parse_fec_name(r.name) for r in recips.itertuples()}
    keys = {r.candidate_id: _person_key(r.state, parsed[r.candidate_id]) for r in recips.itertuples()}
    rep_rows = {}
    for r in recips.itertuples():  # later rows (more recent) win
        rep_rows[keys[r.candidate_id]] = r
    cands = [
        Cand(k, parsed[r.candidate_id], r.state, r.office, r.district if r.office == "H" else "")
        for k, r in sorted(rep_rows.items())
    ]

    ov: dict[int, str] = {}
    for r in overrides.itertuples():
        hit = sc[(sc["name"] == r.scorecard_name) & (sc["state_code"] == state_code(r.state))
                 & (sc["office"] == office_code(r.chamber))]
        for rid in hit["row_id"]:
            ov[int(rid)] = keys.get(r.cand_id, "")

    results = match_scorecard(sc_objs, cands, ov)
    by_person = {r.cand_id: (r, sc.loc[r.row_id]) for r in results if r.cand_id}

    # Persons whose names differ only by nickname (jim/james) share a score with the matched one.
    names = {k: parsed[r.candidate_id] for k, r in rep_rows.items()}
    alias_of: dict[str, str] = {}
    for k, r in rep_rows.items():
        if k in by_person:
            continue
        for k2, r2 in rep_rows.items():
            if k2 in by_person and r2.state == r.state and names[k2].last == names[k].last \
                    and first_names_compatible(names[k2].first, names[k].first):
                alias_of[k] = k2
                break

    rows = []
    for r in recips.itertuples():
        k = keys[r.candidate_id]
        src = alias_of.get(k, k)
        if src in by_person:
            res, row = by_person[src]
            method = "alias" if src != k else res.status
            rows.append({"candidate_id": r.candidate_id, "person_key": k,
                         "score": row["hrc_118th_congress_score"], "scorecard_name": row["name"],
                         "party": row["party"], "match_method": method})
        else:
            rows.append({"candidate_id": r.candidate_id, "person_key": k, "score": pd.NA,
                         "scorecard_name": None, "party": None, "match_method": "unmatched"})
    out = pd.DataFrame(rows)
    out["score"] = out["score"].astype("Float64")
    out["score_bin"] = out["score"].map(score_bin)
    return out


def bin_summary(cand_totals: pd.DataFrame, pacs: list[str]) -> pd.DataFrame:
    """Dollars, distinct candidates and share per PAC x cycle x bin (zero-filled)."""
    parts = []
    scopes = [(c, cand_totals[cand_totals["cycle"] == c]) for c in CYCLES] + [("All", cand_totals)]
    for cycle, scope in scopes:
        per_cand = scope.groupby(["pac", "person_key", "score_bin"], as_index=False)["dollars"].sum()
        g = per_cand.groupby(["pac", "score_bin"]).agg(
            dollars=("dollars", "sum"), candidates=("person_key", lambda s: int((per_cand.loc[s.index, "dollars"] != 0).sum()))
        )
        full = pd.MultiIndex.from_product([pacs, BINS], names=["pac", "score_bin"])
        g = g.reindex(full, fill_value=0).reset_index()
        total = g.groupby("pac")["dollars"].transform("sum")
        g["share"] = (g["dollars"] / total.where(total != 0)).fillna(0.0)
        g.insert(1, "cycle", cycle)
        parts.append(g)
    out = pd.concat(parts, ignore_index=True)
    out["score_bin"] = pd.Categorical(out["score_bin"], BINS, ordered=True)
    out["dollars"] = out["dollars"].round(2)
    return out.sort_values(["pac", "cycle", "score_bin"]).reset_index(drop=True)


def build(data_dir: Path) -> dict[str, pd.DataFrame]:
    spending = load_spending(data_dir / SPENDING)
    deduped = dedupe_amendments(spending)
    pacs = [PAC_SHORT_NAMES[c] for c in PAC_SHORT_NAMES if c in set(spending["committee_id"])]
    direct, _ = split_direct(deduped)

    totals = candidate_totals(direct, PAC_SHORT_NAMES)
    scorecard = pd.read_csv(data_dir / SCORECARD, dtype={"district": str, "hrc_118th_congress_score": "Float64"})
    ov_path = data_dir / OVERRIDES
    overrides = pd.read_csv(ov_path, dtype=str) if ov_path.exists() else pd.DataFrame(
        columns=["scorecard_name", "state", "chamber", "cand_id", "note"])
    recipients = score_recipients(totals, scorecard, overrides)
    totals = totals.merge(recipients, on="candidate_id", how="left")
    totals["score_vintage"] = SCORE_VINTAGE

    # Distinct-candidate count uses persons, so alias ids are not double counted.
    summary = bin_summary(totals, pacs)
    match_report = recipients.merge(
        totals.drop_duplicates("candidate_id")[["candidate_id", "name", "office", "state"]], on="candidate_id"
    )
    match_report = match_report[["candidate_id", "name", "office", "state", "match_method", "scorecard_name",
                                 "score", "score_bin"]].sort_values(["match_method", "state", "name"])
    totals = totals.drop(columns=["person_key", "sub_id_latest"]).rename(columns={"name": "candidate_name"})
    return {
        "pac_candidate_totals": totals,
        "pac_bin_summary": summary,
        "donation_reconciliation": reconcile(deduped, pacs),
        "recipient_match_report": match_report,
    }


def run(data_dir: Path, out_dir: Path) -> dict[str, pd.DataFrame]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = build(data_dir)
    for name, df in tables.items():
        df.to_csv(out_dir / f"{name}.csv", index=False)
    return tables


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=Path("data"))
    ap.add_argument("--out-dir", type=Path, default=Path("data/processed"))
    args = ap.parse_args()
    t = run(args.data_dir, args.out_dir)
    print(t["donation_reconciliation"].to_string(index=False))
    print(t["recipient_match_report"]["match_method"].value_counts().to_string())


if __name__ == "__main__":
    main()
