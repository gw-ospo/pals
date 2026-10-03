# PALS — PAC Analysis of Legislative Scorecards

PALS traces money from corporate PACs to individual candidates using
[FEC bulk data](https://www.fec.gov/data/browse-data/?tab=bulk-data), then
aligns each candidate with legislative scorecard ratings (e.g. HRC on LGBTQ+
equality, NRA on gun rights) to show how corporate political money lines up
with legislative behavior.

> **Data status: open data curated by Claude; not validated.** The datasets, name matching and aggregations in this
> project are open and were assembled by Claude (an AI assistant). They have not been independently validated
> against the FEC or HRC sources. Verify any figure before relying on it. The same notice appears on every page and
> chart of the website.

## The core problem

Corporate PAC money rarely goes only directly to candidates. Much of it passes
through intermediaries — party committees, leadership PACs, joint fundraising
committees — before reaching a candidate's committee. PALS needs an algorithm
that attributes each dollar a candidate receives back to its originating
corporate PAC, **both directly and indirectly**, without double-counting and
while handling cycles in the committee network. See
[`openspec/changes/pals-foundation/`](openspec/changes/pals-foundation/) for
the design.

## Planned components

1. **Ingestion** — download and cache FEC bulk files (committee master,
   candidate master, committee-to-candidate `pas2`, committee-to-committee `oth`).
2. **Money-flow attribution** — propagate a source PAC's dollars through the
   committee graph to candidates.
3. **Scorecard alignment** — join candidates to scorecard scores (HRC, NRA, ...).
4. **Website** — Quarto site with visualizations, published via GitHub Pages.
5. **Pipeline** — add companies via config and refresh FEC data regularly.

The pilot corporate PAC is **Google**.

## Tech stack

Python (managed with `uv`), Jupyter notebooks, Quarto, GitHub Pages.
Project planning and change management use [OpenSpec](https://github.com/Fission-AI/OpenSpec)
(`openspec/`; start a change with `/opsx:propose`).

## Running the candidate combine step

```bash
uv sync
uv run python -m pals.combine      # writes data/processed/*.csv
uv run pytest
```

Outputs: `candidates_combined.csv` (one row per FEC candidate with committee totals and
HRC score), `scorecard_match_report.csv` (status of every scorecard row),
`committee_orphans.csv`, `match_summary.csv`. Fix mismatches by adding rows to
`data/overrides/scorecard_overrides.csv`. The HRC score is for the 118th Congress
(2023-24), so challengers and non-incumbents have no score.

## Website (Quarto + GitHub Pages)

```bash
uv sync --group site
uv run python -m pals.donations    # builds data/processed/pac_*.csv
uv run quarto render site          # or: uv run quarto preview site
```

The site shows corporate PAC direct contributions by candidate HRC score bin, with dollars and candidate counts, and filters for cycle and office (House, Senate). It is deployed by
`.github/workflows/publish.yml` on every push to `main`. One-time setup: in the GitHub repo go to
**Settings > Pages** and set **Source** to **GitHub Actions**. The site will be at
https://gw-ospo.github.io/pals/.

## Status

Early setup. Exploratory notebooks in the repo root predate the package layout.
