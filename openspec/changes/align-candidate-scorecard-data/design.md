## Context

Inputs (profiled): `candidate_summary_2026.csv` has 4,282 candidates (unique `Cand_Id`; 398 incumbents, 2,603 challengers, 1,031 open-seat); `committee_summary_2026.csv` has ~13.5k committees of which 2,747 carry a `CAND_ID` (2,657 principal `P`, 90 authorized `A`; 79 duplicates, i.e. candidates with multiple committees; 78 reference candidates absent from the candidate file); the scorecard has 540 rows (100 senators, 440 House/delegate rows, 13 with null score). A naive last-name check matches ~76% of scorecard rows to some 2026 candidate, ~64% to an incumbent, so many 118th Congress members are not 2026 candidates (retired, not up for re-election, or lost). Name formats differ as described in the proposal.

## Goals / Non-Goals

**Goals:** one auditable candidate table; deterministic, explainable name matching; visible match report.
**Non-Goals:** PAC money-flow attribution, other scorecards (NRA), downloading FEC data, website. Matching to other cycles or historical candidate IDs is out of scope.

## Decisions

- **Committee join by `CAND_ID`, not by name.** It is exact in the FEC data; names are only needed for the scorecard. Committee metrics are summed per candidate; principal committee kept as a separate field.
- **Match scorecard to candidates by layered rules** (exact -> relaxed -> nickname -> fuzzy) on normalized last/first name within state and office. District is a tie-breaker only, because redistricting and cycle changes make it unreliable.
- **pandas + rapidfuzz, stdlib `unicodedata`** for normalization; nickname map kept as a small CSV in the repo. Alternative considered: polars/duckdb; pandas chosen for notebook friendliness at this data size.
- **Ambiguity is never auto-resolved.** Ambiguous and low-score matches go to the report and a manual override CSV (`data/overrides/`) resolves them.
- **Scorecard is the left side of matching** (each scorecard row maps to at most one candidate), then the result is left-joined onto candidates, so non-incumbents correctly get null scores.
- **Outputs** as Parquet/CSV in `data/processed/` (git-ignored) plus `match_report.csv`; logic in a package module (`src/pals/`) called from a notebook so it is testable.

## Risks / Trade-offs

- Fuzzy matching can produce false positives (common surnames, family members in one state) -> require same state+office, threshold configurable, report for review, tests with known tricky names.
- The 118th scorecard predates 2026; score reflects prior-term behavior -> documented in the output field name.
- Territories/delegates and null scores are edge cases -> explicit mapping and null preservation.
- Committee file `CAND_ID` orphans (78) -> reported, not dropped silently.

## Open Questions

- Should the combined table also include candidates from `weball26.txt` (FEC bulk all-candidates summary) for cross-checking? Assumed no for now.
