from pathlib import Path

import pandas as pd
import pytest

from pals.donations import (BINS, PAC_SHORT_NAMES, bin_summary, candidate_totals, dedupe_amendments,
                            reconcile, run, score_bin, split_direct)

DATA = Path(__file__).resolve().parents[1] / "data"


DEFAULTS = {"committee_name": "x", "transaction_id": None, "disbursement_type": "24K", "candidate_id": "H1",
            "candidate_name": "SMITH, JANE", "candidate_office": "H", "candidate_office_state": "GA",
            "candidate_office_district": "05", "cycle": "2024", "pac": "Google", "committee_id": "C00428623"}


def rows(*items):
    return pd.DataFrame([{**DEFAULTS, **item} for item in items]).astype({"sub_id_num": float})


def test_score_bin_exact():
    assert [score_bin(s) for s in (0, 1, 24, 25, 49, 50, 74, 75, 99, 100)] == \
        ["0", "1-24", "1-24", "25-49", "25-49", "50-74", "50-74", "75-99", "75-99", "100"]
    assert all(score_bin(s) == "No score" for s in (None, float("nan"), pd.NA))


def test_amendment_dedupe_keeps_latest():
    df = rows({"sub_id_num": 1, "amount": 5000.0, "transaction_id": "T1"},
              {"sub_id_num": 2, "amount": 5000.0, "transaction_id": "T1"},
              {"sub_id_num": 3, "amount": 100.0, "transaction_id": None},
              {"sub_id_num": 4, "amount": 200.0, "transaction_id": None})
    out = dedupe_amendments(df)
    assert out["amount"].sum() == 5300.0 and len(out) == 3


def test_refund_netting_and_cycles():
    df = rows({"sub_id_num": 1, "amount": 5000.0}, {"sub_id_num": 2, "amount": -5000.0},
              {"sub_id_num": 3, "amount": 1000.0, "cycle": "2026"})
    t = candidate_totals(split_direct(df)[0], PAC_SHORT_NAMES)
    assert dict(zip(t["cycle"], t["dollars"])) == {"2024": 0.0, "2026": 1000.0}


def test_non_candidate_and_refund_types_excluded():
    df = rows({"sub_id_num": 1, "amount": 100.0},
              {"sub_id_num": 2, "amount": 200.0, "candidate_id": None},
              {"sub_id_num": 3, "amount": 300.0, "disbursement_type": "22Y"})
    direct, other = split_direct(df)
    assert direct["amount"].sum() == 100.0 and other["amount"].sum() == 200.0
    rec = reconcile(df, ["Google"]).iloc[0]
    assert rec.direct_to_candidates + rec.excluded_no_candidate == rec.total_24k_deduplicated


def test_bin_summary_zero_filled_and_sums():
    t = pd.DataFrame({"pac": ["Google", "Google"], "person_key": ["a", "b"], "cycle": ["2024", "2026"],
                      "dollars": [100.0, 300.0], "score_bin": ["0", "100"], "race": ["House", "Senate"]})
    s = bin_summary(t, ["Google", "Anthropic"])
    g = s[(s.pac == "Google") & (s.cycle == "All") & (s.office == "All")]
    assert list(g["score_bin"]) == BINS and g["dollars"].sum() == 400.0 and g["share"].sum() == pytest.approx(1)
    a = s[(s.pac == "Anthropic") & (s.cycle == "All") & (s.office == "All")]
    assert len(a) == 7 and a["dollars"].sum() == 0 and a["share"].sum() == 0


@pytest.mark.skipif(not (DATA / "big-AI-spending-2023-2026.csv").exists(), reason="data not present")
def test_pipeline_invariants(tmp_path):
    t = run(DATA, tmp_path)
    totals, summ = t["pac_candidate_totals"], t["pac_bin_summary"]
    direct = totals.groupby("pac")["dollars"].sum().round(2)
    allsum = summ[(summ.cycle == "All") & (summ.office == "All")].groupby("pac", observed=True)["dollars"].sum().round(2)
    for pac in direct.index:
        assert allsum[pac] == direct[pac]
    assert (allsum.drop(direct.index) == 0).all()  # Anthropic present with zeros
    assert set(summ["pac"]) >= {"Google", "Anthropic"}
    # office slices add up to the All view
    by_office = (summ[summ.cycle == "All"].groupby(["pac", "office"], observed=True)["dollars"].sum().unstack())
    assert ((by_office[["House", "Senate"]].sum(axis=1) - by_office["All"]).abs() < 0.01).all()
    rec = t["donation_reconciliation"]
    assert ((rec.direct_to_candidates + rec.excluded_no_candidate - rec.total_24k_deduplicated).abs() < 0.01).all()


def test_office_split_and_person_counted_once():
    # one person gives to two races: counted once under All, once per office otherwise
    t = pd.DataFrame({"pac": ["Google"] * 3, "person_key": ["a", "a", "b"], "cycle": ["2024"] * 3,
                      "dollars": [100.0, 200.0, 50.0], "score_bin": ["0", "0", "100"],
                      "race": ["House", "Senate", "House"]})
    s = bin_summary(t, ["Google"])
    s = s[(s.cycle == "All")].set_index(["office", "score_bin"])
    assert s.loc[("All", "0"), "candidates"] == 1 and s.loc[("All", "0"), "dollars"] == 300.0
    assert s.loc[("House", "0"), "candidates"] == 1 and s.loc[("Senate", "0"), "candidates"] == 1
    for b in ("0", "100"):
        parts = sum(s.loc[(o, b), "dollars"] for o in ("House", "Senate"))
        assert parts == s.loc[("All", b), "dollars"]


def test_contribution_office_fallback():
    from pals.donations import contribution_office
    got = contribution_office(pd.Series(["S", None, None]), pd.Series(["H1", "H2", "S3"]))
    assert list(got) == ["Senate", "House", "Senate"]
