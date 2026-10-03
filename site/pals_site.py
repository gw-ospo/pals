"""Shared data loading and chart styling for the PALS site."""
from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd

PROCESSED = Path("..") / "data" / "processed"
BINS = ["0", "1-24", "25-49", "50-74", "75-99", "100", "No score"]
# single-hue ramp ending at the brand colour; gray for "No score"
BIN_COLORS = ["#f6dfdb", "#e8b4ac", "#d4857c", "#b8514c", "#9a2325", "#780000", "#8a8a8a"]
ACCENT = "#780000"

# One wording everywhere: README, page banner, footer, chart subtitles, table caption.
NOTICE = "Open data curated by Claude; not validated."
OFFICE_OPTIONS = ["All", "House", "Senate"]


def load() -> dict[str, pd.DataFrame]:
    summary = pd.read_csv(PROCESSED / "pac_bin_summary.csv", dtype={"cycle": str})
    totals = pd.read_csv(PROCESSED / "pac_candidate_totals.csv", dtype={"cycle": str, "district": str})
    recon = pd.read_csv(PROCESSED / "donation_reconciliation.csv")
    return {"summary": summary, "totals": totals, "recon": recon}


def _theme():
    return {
        "config": {
            "view": {"stroke": None},
            "font": "Helvetica Neue, Helvetica, Arial, sans-serif",
            "axis": {"labelColor": "#222", "titleColor": "#222", "gridColor": "#e6e6e6", "labelFontSize": 12,
                     "titleFontSize": 13},
            "legend": {"labelFontSize": 12, "titleFontSize": 13},
            "bar": {"stroke": "#4a0000", "strokeWidth": 0.6},
        }
    }


alt.themes.register("pals", _theme)
alt.themes.enable("pals")


def bin_color(title: str | None = None, legend: bool = True) -> alt.Color:
    return alt.Color(
        "score_bin:N",
        scale=alt.Scale(domain=BINS, range=BIN_COLORS),
        legend=alt.Legend(title=title or "HRC score bin", orient="bottom") if legend else None,
    )


CYCLE_LABELS = {"All": "Both cycles", "2024": "2024 cycle", "2026": "2026 cycle"}
