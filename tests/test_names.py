import pytest

from pals.jurisdiction import district_code, office_code, state_code
from pals.names import display_name, parse_fec_name, parse_scorecard_name


def test_fec_name_reordered():
    n = parse_fec_name("MCBATH, LUCIA KAY MS.")
    assert (n.last, n.first, n.middle) == ("mcbath", "lucia", ("kay",))


def test_fec_suffix_and_apostrophe():
    n = parse_fec_name("SALERNO-O'DONNELL, JORDAN JR.")
    assert n.last == "salernoodonnell" and n.first == "jordan" and n.suffix == "jr"


def test_scorecard_name():
    n = parse_scorecard_name("Katie Britt")
    assert (n.last, n.first) == ("britt", "katie")


def test_scorecard_particle_last_name():
    assert parse_scorecard_name("Catherine Cortez Masto").last == "masto"
    assert parse_scorecard_name("Chris Van Hollen").last == "vanhollen"


def test_hyphen_equivalence():
    assert parse_fec_name("WASSERMAN SCHULTZ, DEBBIE").last == parse_scorecard_name("Debbie Wasserman-Schultz").last


def test_blank():
    assert parse_fec_name(None).last == ""


def test_jurisdiction():
    assert state_code("Alaska") == "AK"
    assert office_code("House") == "H"
    assert district_code("AL", "H") == "00"
    assert district_code("7", "H") == "07"
    assert district_code("Statewide", "S") == ""
    with pytest.raises(ValueError):
        state_code("Atlantis")


def test_display_name():
    assert display_name("CORNYN, JOHN SEN. III") == "John Cornyn III"
    assert display_name("MCBATH, LUCIA KAY MS.") == "Lucia Kay McBath"
    assert display_name("CARTER, EARL L. B.") == "Earl L. B. Carter"
    assert display_name("SALERNO-O'DONNELL, JORDAN JR.") == "Jordan Salerno-O'Donnell Jr."
    assert display_name(None) == ""
