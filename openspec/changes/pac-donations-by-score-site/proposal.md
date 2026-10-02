# Proposal

## Why

PALS exists to show how corporate PAC money lines up with legislative scorecards.
The data to start answering that is in hand: the big-AI-spending file holds six
corporate PACs' FEC disbursements, and the HRC scorecard is already aligned to
candidates. There is no way yet to see, for a given PAC such as Google, how much
direct money went to candidates with an HRC score of 0, 100, or somewhere between.
A public interactive site makes the analysis browsable and is the delivery
vehicle later features (indirect money, more scorecards, more PACs) will extend.

## What Changes

- Derive a per-PAC, per-candidate table of **direct** contributions from
  `data/big-AI-spending-2023-2026.csv` (FEC 24K contributions that carry a candidate).
- Attach each recipient's HRC 118th Congress score using the existing name-matching
  logic, so recipients are matched even when they are not in the 2026 candidate summary.
- Aggregate dollars (and candidate counts) by score bin: `0`, `1-24`, `25-49`,
  `50-74`, `75-99`, `100`, and `No score` (candidates without a scorecard score).
- Build a Quarto website with interactive visualizations (PAC selector, dollars vs.
  share of total, cycle filter, drill-down to the candidates behind each bin).
- Publish the site to GitHub Pages via a GitHub Actions workflow.

Out of scope: indirect money through intermediary committees, scorecards other than HRC,
adding PACs beyond those in the data file, refreshing from the FEC API.

## Capabilities

### New Capabilities
- `direct-donations-dataset`: Clean per-PAC, per-candidate direct-contribution totals from the FEC disbursement file.
- `score-bin-analysis`: Assignment of candidates to HRC score bins and aggregation of dollars per PAC and bin.
- `quarto-site`: Quarto website with interactive charts, published to GitHub Pages.

### Modified Capabilities

## Impact

Adds `site/` (Quarto project), an analysis module under `src/pals/`, derived files in
`data/processed/` (consumed by the site), and `.github/workflows/` for Pages. Adds
Quarto, Altair (or similar) and a Pages workflow. Reuses `pals.names`, `pals.jurisdiction`
and `pals.match` from `align-candidate-scorecard-data`.
