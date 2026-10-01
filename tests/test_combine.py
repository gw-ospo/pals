from pathlib import Path

import pandas as pd
import pytest

from pals.combine import aggregate_committees, run

DATA = Path(__file__).resolve().parents[1] / "data"


def test_committee_aggregation_multiple_committees():
    cm = pd.DataFrame({
        "CMTE_ID": ["C1", "C2", "C3", "C4"],
        "CMTE_NM": ["a", "b", "c", "d"],
        "CMTE_TP": ["H"] * 4,
        "CMTE_DSGN": ["A", "P", "P", None],
        "CAND_ID": ["H1", "H1", "H2", None],
        "TTL_RECEIPTS": ["5", "10", "7", "1"],
        "TTL_DISB": ["1", "2", "3", "4"],
        "TTL_CONTB": ["5", "10", "7", "1"],
        "OTH_CMTE_CONTB": [None, "4", None, None],
        "COH_COP": ["1", "1", "1", "1"],
    })
    agg, orphans = aggregate_committees(cm, pd.Series(["H1", "H3"]))
    row = agg.set_index("Cand_Id").loc["H1"]
    assert row.cmte_ids == "C1;C2" and row.cmte_count == 2
    assert row.principal_cmte_id == "C2" and row.cmte_total_receipts == 15
    assert list(orphans["CMTE_ID"]) == ["C3"]
    assert "H3" not in set(agg["Cand_Id"])  # candidate without committee stays null after merge


@pytest.mark.skipif(not (DATA / "candidate_summary_2026.csv").exists(), reason="data not present")
def test_pipeline_counts_and_rerun_identical(tmp_path):
    t = run(DATA, tmp_path / "a")
    assert len(t["candidates_combined"]) == 4282
    assert len(t["scorecard_match_report"]) == 540
    assert t["candidates_combined"]["Cand_Id"].is_unique
    # null scorecard scores stay null
    report = t["scorecard_match_report"]
    assert report["hrc_118th_congress_score"].isna().sum() == 13
    run(DATA, tmp_path / "b")
    for f in (tmp_path / "a").iterdir():
        assert f.read_bytes() == (tmp_path / "b" / f.name).read_bytes()
