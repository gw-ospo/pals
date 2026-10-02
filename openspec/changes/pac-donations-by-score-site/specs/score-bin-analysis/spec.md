## ADDED Requirements

### Requirement: Score bins
The system SHALL assign each candidate to exactly one bin by HRC score: `0` (score = 0), `1-24`, `25-49`, `50-74`, `75-99`, `100` (score = 100), or `No score` when the candidate has no matched score or the score is null.

#### Scenario: Boundary scores
- **WHEN** candidates have scores 0, 1, 24, 25, 99 and 100
- **THEN** they fall in bins `0`, `1-24`, `1-24`, `25-49`, `75-99` and `100`

#### Scenario: Unscored candidate
- **WHEN** a recipient has no matched scorecard row or a null score
- **THEN** the recipient is in `No score`

### Requirement: Score matching for donation recipients
The system SHALL match donation recipients to scorecard rows using the PALS name-matching rules (state, office, normalized name) and SHALL NOT require the recipient to appear in the 2026 candidate summary.

#### Scenario: Recipient not a 2026 candidate
- **WHEN** a donation recipient from the 2024 cycle is absent from the 2026 candidate summary but matches a scorecard row
- **THEN** the recipient receives that scorecard score

#### Scenario: Match report
- **WHEN** matching completes
- **THEN** the system writes each recipient's match status and lists ambiguous or unmatched recipients for review

### Requirement: Aggregation by PAC and bin
The system SHALL compute, for each PAC and bin, the net direct dollars, number of distinct candidates, and share of that PAC's total direct dollars; bins with no activity SHALL appear with zero.

#### Scenario: Google breakdown
- **WHEN** the aggregate is built
- **THEN** Google has seven rows (one per bin) whose dollars sum to Google's total direct contributions

### Requirement: Score vintage disclosure
The system SHALL label outputs as using the 118th Congress (2023-24) HRC score regardless of the donation cycle.

#### Scenario: 2026-cycle donation
- **WHEN** a 2026-cycle donation is binned
- **THEN** the output states the score reflects the 118th Congress record
