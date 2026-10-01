from pals.match import Cand, Score, match_scorecard
from pals.names import parse_fec_name, parse_scorecard_name


def cand(cid, fec, st="GA", office="H", dist="05"):
    return Cand(cid, parse_fec_name(fec), st, office, dist)


def score(rid, name, st="GA", office="H", dist="05"):
    return Score(rid, parse_scorecard_name(name), st, office, dist)


def one(s, cands, **kw):
    return match_scorecard([s], cands, **kw)[0]


def test_exact():
    r = one(score(0, "Lucy McBath"), [cand("A", "MCBATH, LUCY")])
    assert (r.status, r.cand_id) == ("exact", "A")


def test_nickname_and_middle_name():
    r = one(score(0, "Lucy McBath"), [cand("A", "MCBATH, LUCIA KAY MS.")])
    assert (r.status, r.cand_id) == ("nickname", "A")
    r = one(score(0, "Andy Barr"), [cand("B", "BARR, GARLAND ANDY", office="H")])
    assert r.cand_id == "B"


def test_compound_surname():
    r = one(score(0, "Debbie Wasserman Schultz", "FL", "H", "25"),
            [cand("C", "WASSERMAN SCHULTZ, DEBBIE", "FL", "H", "25")])
    assert r.status == "exact"


def test_cross_office():
    r = one(score(0, "Mike Collins"), [cand("D", "COLLINS, MICHAEL A JR", office="S", dist="")])
    assert (r.status, r.cand_id) == ("cross_office", "D")


def test_ambiguous_same_name_same_district():
    r = one(score(0, "Jane Smith"), [cand("E", "SMITH, JANE"), cand("F", "SMITH, JANE")])
    assert r.status == "ambiguous" and r.candidates == ["E", "F"] and r.cand_id is None


def test_district_breaks_tie():
    r = one(score(0, "Jane Smith", dist="07"), [cand("E", "SMITH, JANE", dist="05"), cand("F", "SMITH, JANE", dist="07")])
    assert r.cand_id == "F"


def test_suffix_breaks_tie():
    cs = [cand("E", "MENENDEZ, ROBERT"), cand("F", "MENENDEZ, ROBERT JR.")]
    assert one(score(0, "Robert Menendez Jr."), cs).cand_id == "F"


def test_wrong_state_is_unmatched():
    assert one(score(0, "Jane Smith"), [cand("E", "SMITH, JANE", st="TX")]).status == "unmatched"


def test_manual_override_wins():
    r = one(score(0, "Nick LaLota"), [cand("G", "NICK, LALOTA")], overrides={0: "G"})
    assert (r.status, r.cand_id) == ("manual", "G")


def test_candidate_used_once():
    rs = match_scorecard([score(0, "Jane Smith"), score(1, "Jane Smith")], [cand("E", "SMITH, JANE")])
    assert all(r.status == "ambiguous" for r in rs)
