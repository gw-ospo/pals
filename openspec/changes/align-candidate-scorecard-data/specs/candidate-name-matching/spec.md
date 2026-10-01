## ADDED Requirements

### Requirement: Normalize candidate names
The system SHALL convert names from every source into a common normalized form (lowercase, ASCII-folded, punctuation and honorifics such as MR./MS./DR. removed, suffixes such as JR./III separated) and expose last name, first name and middle tokens.

#### Scenario: FEC name reordered
- **WHEN** the FEC name `"MCBATH, LUCIA KAY MS."` is normalized
- **THEN** it yields last `mcbath`, first `lucia`, middle `kay`, with no honorific

#### Scenario: Scorecard name
- **WHEN** the scorecard name `Katie Britt` is normalized
- **THEN** it yields last `britt` and first `katie`

### Requirement: Normalize jurisdiction
The system SHALL map scorecard full state names and territories to two-letter USPS codes, chamber `House`/`Senate` to FEC office `H`/`S`, and scorecard districts (`Statewide`, `AL`, numerals) to FEC district codes.

#### Scenario: At-large district
- **WHEN** a scorecard row has state `Alaska` and district `AL`
- **THEN** it is keyed as office `H`, state `AK`, district `00`

### Requirement: Deterministic matching with exact-first fallback
The system SHALL match scorecard rows to FEC candidates by, in order: exact normalized last+first+state+office; exact last+first+state; nickname or first-initial variants with last+state+office; then fuzzy name similarity above a configured threshold within the same state and office. Each scorecard row SHALL match at most one candidate.

#### Scenario: Unique exact match
- **WHEN** exactly one FEC candidate shares normalized last name, first name, state and office with a scorecard row
- **THEN** the row is matched with method `exact`

#### Scenario: Ambiguous match
- **WHEN** more than one FEC candidate is an equally good match
- **THEN** the row is left unmatched and flagged `ambiguous` in the match report

### Requirement: Manual override table
The system SHALL read an optional CSV of manual overrides mapping a scorecard row to a `Cand_Id`, applied before automatic matching.

#### Scenario: Override applied
- **WHEN** an override maps a scorecard name to a specific `Cand_Id`
- **THEN** that mapping is used and recorded with method `manual`
