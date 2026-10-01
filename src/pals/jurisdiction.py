"""Map scorecard jurisdictions onto FEC office/state/district codes."""
from __future__ import annotations

STATES = {
    "alabama": "AL", "alaska": "AK", "american samoa": "AS", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "district of columbia": "DC", "florida": "FL", "georgia": "GA", "guam": "GU", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD", "massachusetts": "MA",
    "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO", "montana": "MT",
    "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ",
    "new mexico": "NM", "new york": "NY", "north carolina": "NC", "north dakota": "ND",
    "northern mariana islands": "MP", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
    "pennsylvania": "PA", "puerto rico": "PR", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virgin islands": "VI", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
}
OFFICES = {"house": "H", "senate": "S"}


def state_code(name: str) -> str:
    try:
        return STATES[name.strip().lower()]
    except KeyError:
        raise ValueError(f"Unknown state or territory: {name!r}") from None


def office_code(chamber: str) -> str:
    try:
        return OFFICES[chamber.strip().lower()]
    except KeyError:
        raise ValueError(f"Unknown chamber: {chamber!r}") from None


def district_code(district: str | None, office: str) -> str:
    """Scorecard district -> FEC district ('' for Senate, '00' at-large, else 2 digits)."""
    if office == "S":
        return ""
    d = (district or "").strip()
    if d.upper() in {"AL", "STATEWIDE", ""}:
        return "00"
    return f"{int(d):02d}"
