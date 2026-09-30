# PALS — PAC Analysis of Legislative Scorecards

PALS traces money from corporate PACs to individual candidates using
[FEC bulk data](https://www.fec.gov/data/browse-data/?tab=bulk-data), then
aligns each candidate with legislative scorecard ratings (e.g. HRC on LGBTQ+
equality, NRA on gun rights) to show how corporate political money lines up
with legislative behavior.

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

## Status

Early setup. Exploratory notebooks in the repo root predate the package layout.
