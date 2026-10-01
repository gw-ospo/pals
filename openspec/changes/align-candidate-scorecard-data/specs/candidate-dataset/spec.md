## ADDED Requirements

### Requirement: Combined candidate table
The system SHALL produce one row per FEC candidate (`Cand_Id`) containing candidate summary fields, aggregated principal and authorized committee financials, and the scorecard score when matched.

#### Scenario: Candidate with principal committee
- **WHEN** a candidate has committees in the committee summary whose `CAND_ID` equals the candidate's `Cand_Id`
- **THEN** the candidate row includes those committee IDs and summed receipts and disbursements

#### Scenario: Candidate without committee
- **WHEN** no committee summary row carries a candidate's `Cand_Id`
- **THEN** the candidate row is kept with null committee fields

#### Scenario: Candidate with multiple committees
- **WHEN** a candidate has more than one committee (principal and authorized)
- **THEN** all committee IDs are retained and the principal committee (`CMTE_DSGN` = `P`) is identified

### Requirement: Scorecard attachment
The system SHALL attach `hrc_118th_congress_score` and scorecard name to matched candidates and leave the score null for unmatched candidates; a scorecard score of null in the source SHALL remain null, not zero.

#### Scenario: Matched incumbent
- **WHEN** an incumbent is matched to a scorecard row with score 100
- **THEN** the candidate row has score 100 and the match method

### Requirement: Match report
The system SHALL write a report listing every scorecard row with its match status (`exact`, `fuzzy`, `manual`, `ambiguous`, `unmatched`), matched `Cand_Id`, and similarity score, plus summary counts.

#### Scenario: Scorecard member not running
- **WHEN** a 118th Congress member has no 2026 FEC candidate record
- **THEN** the row appears in the report as `unmatched` and the run does not fail

### Requirement: Reproducible outputs
The system SHALL read inputs from `data/`, write outputs to `data/processed/`, and produce identical outputs for identical inputs.

#### Scenario: Rerun
- **WHEN** the step is run twice on unchanged inputs
- **THEN** the output files are identical
