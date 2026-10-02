## ADDED Requirements

### Requirement: Select direct candidate contributions
The system SHALL treat a disbursement as a direct candidate contribution when its disbursement type is `24K` and it carries a `candidate_id`. Disbursements to other committees, parties, or individuals (including type `22Y` refunds) SHALL NOT be counted as direct contributions.

#### Scenario: Contribution to a candidate
- **WHEN** a Google NetPAC row has disbursement type `24K` and candidate id `H2CA37023`
- **THEN** its amount counts toward Google's direct total for that candidate

#### Scenario: Contribution to a leadership PAC
- **WHEN** a row has type `24K` but no `candidate_id` (recipient is a PAC or party committee)
- **THEN** it is excluded from direct contributions and counted in an "excluded" summary

### Requirement: Deduplicate amended transactions
The system SHALL keep only the latest record (highest `sub_id`) for each `committee_id` + `transaction_id`, so amended filings are not double-counted.

#### Scenario: Amended transaction
- **WHEN** two rows share a `committee_id` and `transaction_id` with different `sub_id`
- **THEN** only the row with the higher `sub_id` contributes to totals

### Requirement: Net refunds and voids
The system SHALL sum signed amounts so negative entries (voided or refunded contributions) reduce the total for the PAC and candidate.

#### Scenario: Voided contribution
- **WHEN** a candidate has a +5,000 and a -5,000 contribution from the same PAC
- **THEN** the net direct total for that candidate is 0

### Requirement: Per-PAC candidate totals
The system SHALL output one row per PAC and candidate with net total, contribution count, election cycle(s), and the candidate's name, office, state and district.

#### Scenario: Same candidate across cycles
- **WHEN** a PAC gives to one candidate in both the 2024 and 2026 cycles
- **THEN** the table has a row per cycle and the site can also show the combined total

### Requirement: Reconciliation summary
The system SHALL write a summary reconciling total `24K` dollars into direct, excluded (no candidate), and deduplicated amounts per PAC.

#### Scenario: Totals reconcile
- **WHEN** the summary is produced
- **THEN** direct + excluded equals total deduplicated `24K` dollars for each PAC
