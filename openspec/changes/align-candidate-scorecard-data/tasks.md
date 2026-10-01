## 1. Project setup

- [x] 1.1 Create `pyproject.toml` (uv) with pandas, rapidfuzz, pytest, jupyter; add `src/pals/` package
- [x] 1.2 Add `data/processed/` and `data/overrides/` conventions (processed git-ignored)

## 2. Normalization

- [x] 2.1 Implement name normalization (case, accents, honorifics, suffixes, token split) in `src/pals/names.py`
- [x] 2.2 Implement state/territory, chamber and district mapping in `src/pals/jurisdiction.py`
- [x] 2.3 Add unit tests for the scenarios in `candidate-name-matching` (e.g. `MCBATH, LUCIA KAY MS.`, `AL` districts)

## 3. Loading and committee join

- [x] 3.1 Load the three CSVs with explicit dtypes (IDs as strings, null-preserving scores)
- [x] 3.2 Aggregate committee summary per `CAND_ID`, retaining committee IDs and principal committee
- [x] 3.3 Left-join committees onto candidates; report committee rows whose `CAND_ID` is missing from candidates

## 4. Scorecard matching

- [x] 4.1 Implement layered matcher (exact, relaxed, nickname/initial, fuzzy) with configurable threshold
- [x] 4.2 Add manual override CSV support applied before automatic matching
- [x] 4.3 Flag ambiguous matches and enforce one candidate per scorecard row
- [x] 4.4 Tests for exact, ambiguous, override and unmatched cases

## 5. Outputs

- [x] 5.1 Write combined candidate table to `data/processed/` and `match_report.csv` with summary counts
- [x] 5.2 Verify reruns are identical and check counts against profiled inputs (4,282 candidates, 540 scorecard rows)
- [x] 5.3 Add exploratory notebook that runs the pipeline and reviews unmatched/ambiguous rows
- [x] 5.4 Update README with how to run the step
