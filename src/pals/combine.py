"""Combine FEC candidate summary, committee summary and HRC scorecard."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .jurisdiction import district_code, office_code, state_code
from .match import Cand, Score, match_scorecard
from .names import parse_fec_name, parse_scorecard_name

CANDIDATES = "candidate_summary_2026.csv"
COMMITTEES = "committee_summary_2026.csv"
SCORECARD = "hrc_118th_congress_scorecard.csv"
OVERRIDES = "overrides/scorecard_overrides.csv"

COMMITTEE_SUMS = {
    "TTL_RECEIPTS": "cmte_total_receipts",
    "TTL_DISB": "cmte_total_disbursements",
    "TTL_CONTB": "cmte_total_contributions",
    "OTH_CMTE_CONTB": "cmte_other_committee_contributions",
    "COH_COP": "cmte_cash_on_hand",
}


def load(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cands = pd.read_csv(data_dir / CANDIDATES, dtype=str)
    cmtes = pd.read_csv(data_dir / COMMITTEES, dtype=str)
    score = pd.read_csv(data_dir / SCORECARD, dtype={"district": str, "hrc_118th_congress_score": "Float64"})
    ov_path = data_dir / OVERRIDES
    if ov_path.exists():
        ov = pd.read_csv(ov_path, dtype=str)
    else:
        ov = pd.DataFrame(columns=["scorecard_name", "state", "chamber", "cand_id", "note"])
    return cands, cmtes, score, ov


def aggregate_committees(cmtes: pd.DataFrame, cand_ids: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    linked = cmtes[cmtes["CAND_ID"].notna()].copy()
    for col in COMMITTEE_SUMS:
        linked[col] = pd.to_numeric(linked[col], errors="coerce")
    orphans = linked[~linked["CAND_ID"].isin(cand_ids)][["CMTE_ID", "CMTE_NM", "CMTE_TP", "CMTE_DSGN", "CAND_ID"]]
    linked = linked[linked["CAND_ID"].isin(cand_ids)]
    # principal committee: designation P, largest receipts, then id for determinism
    ordered = linked.sort_values(["CAND_ID", "TTL_RECEIPTS", "CMTE_ID"], ascending=[True, False, True])
    ordered["_p"] = (ordered["CMTE_DSGN"] == "P").astype(int)
    principal = (
        ordered.sort_values(["CAND_ID", "_p", "TTL_RECEIPTS", "CMTE_ID"], ascending=[True, False, False, True])
        .drop_duplicates("CAND_ID")
        .set_index("CAND_ID")["CMTE_ID"]
        .where(lambda s: s.index.isin(ordered.loc[ordered["_p"] == 1, "CAND_ID"]))
    )
    agg = linked.groupby("CAND_ID").agg(
        cmte_ids=("CMTE_ID", lambda s: ";".join(sorted(s))),
        cmte_count=("CMTE_ID", "count"),
        **{new: (old, lambda s: s.sum(min_count=1)) for old, new in COMMITTEE_SUMS.items()},
    )
    agg["principal_cmte_id"] = principal
    return agg.reset_index().rename(columns={"CAND_ID": "Cand_Id"}), orphans.sort_values("CMTE_ID")


def build(data_dir: Path) -> dict[str, pd.DataFrame]:
    cands, cmtes, score, ov = load(data_dir)
    agg, orphans = aggregate_committees(cmtes, cands["Cand_Id"])

    # Scorecard rows -> matching keys
    score = score.reset_index(drop=True)
    score["row_id"] = score.index
    score["state_code"] = score["state"].map(state_code)
    score["office"] = score["chamber"].map(office_code)
    score["district_code"] = [district_code(d, o) for d, o in zip(score["district"], score["office"])]
    sc_objs = [
        Score(r.row_id, parse_scorecard_name(r.name), r.state_code, r.office, r.district_code)
        for r in score.itertuples()
    ]

    congress = cands[cands["Cand_Office"].isin(["H", "S"])]
    cand_objs = [
        Cand(r.Cand_Id, parse_fec_name(r.Cand_Name), r.Cand_Office_St, r.Cand_Office,
             r.Cand_Office_Dist if r.Cand_Office == "H" else "")
        for r in congress.itertuples()
    ]

    overrides: dict[int, str] = {}
    for r in ov.itertuples():
        hit = score[(score["name"] == r.scorecard_name) & (score["state_code"] == state_code(r.state))
                    & (score["office"] == office_code(r.chamber))]
        for rid in hit["row_id"]:
            overrides[int(rid)] = r.cand_id

    results = match_scorecard(sc_objs, cand_objs, overrides)
    report = score.merge(
        pd.DataFrame(
            {
                "row_id": [r.row_id for r in results],
                "match_status": [r.status for r in results],
                "matched_cand_id": [r.cand_id for r in results],
                "similarity": [r.similarity for r in results],
                "ambiguous_candidates": [";".join(r.candidates) for r in results],
            }
        ),
        on="row_id",
    ).drop(columns=["row_id"])
    name_by_id = cands.set_index("Cand_Id")["Cand_Name"]
    report["matched_fec_name"] = report["matched_cand_id"].map(name_by_id)

    matched = report[report["matched_cand_id"].notna()][
        ["matched_cand_id", "name", "hrc_118th_congress_score", "match_status"]
    ].rename(columns={"matched_cand_id": "Cand_Id", "name": "scorecard_name", "match_status": "scorecard_match_method"})
    combined = (
        cands.merge(agg, on="Cand_Id", how="left")
        .merge(matched, on="Cand_Id", how="left", validate="one_to_one")
        .sort_values("Cand_Id")
        .reset_index(drop=True)
    )
    summary = report["match_status"].value_counts().rename_axis("match_status").reset_index(name="rows")
    return {
        "candidates_combined": combined,
        "scorecard_match_report": report.sort_values(["state_code", "office", "district_code", "name"]),
        "committee_orphans": orphans,
        "match_summary": summary.sort_values("match_status"),
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
    tables = run(args.data_dir, args.out_dir)
    print(tables["match_summary"].to_string(index=False))
    print(f"candidates: {len(tables['candidates_combined'])}; orphan committees: {len(tables['committee_orphans'])}")


if __name__ == "__main__":
    main()
