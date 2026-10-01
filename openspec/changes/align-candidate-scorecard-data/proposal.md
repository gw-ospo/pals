# Proposal

## Why

The first PALS analysis step needs one table per candidate that joins FEC 2026
candidate financials, FEC committee financials, and legislative scorecard scores.
The three sources identify candidates differently: FEC summaries use
`"LAST, FIRST MIDDLE MR."` uppercase names plus a `Cand_Id`, the committee file links
to candidates only by `CAND_ID`, and the HRC scorecard uses `First Last` names with
full state names and a district number. Without aligned names the scorecard scores
cannot be attached to the candidates who receive PAC money.

## What Changes

- Build a reproducible step that reads `data/candidate_summary_2026.csv`,
  `data/committee_summary_2026.csv` and `data/hrc_118th_congress_scorecard.csv`.
- Normalize candidate names and jurisdictions (state, chamber, district) in all three sources.
- Join committees to candidates via `CAND_ID` (exact), then scorecard rows to candidates
  via normalized name + state + chamber (district as a tie-breaker, since 2026 districts
  may differ from 118th Congress districts).
- Emit a combined candidate-level dataset plus a match report listing unmatched and
  ambiguous scorecard rows, so every gap is visible rather than silently dropped.
- Known scope limit: the scorecard covers members of the 118th Congress (2023-24), so
  challengers and open-seat candidates legitimately have no score.

## Capabilities

### New Capabilities
- `candidate-dataset`: Combined candidate-level table from FEC candidate summary, FEC committee summary and the scorecard, with a match report.
- `candidate-name-matching`: Name/jurisdiction normalization and deterministic matching rules across sources.

### Modified Capabilities

## Impact

New Python package module and a Jupyter notebook under the PALS repo; reads from `data/`;
writes to `data/processed/` (git-ignored). Adds pandas (and a fuzzy-match library,
e.g. rapidfuzz) as dependencies via `uv`. Prepares the candidate key that later
money-flow attribution and scorecard-alignment changes build on.
