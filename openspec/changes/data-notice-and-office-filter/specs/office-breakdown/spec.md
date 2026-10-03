## ADDED Requirements

### Requirement: Office dimension
The data step SHALL assign each direct contribution an office of `House` or `Senate` from the contribution's FEC candidate office (falling back to the candidate id prefix H or S), and SHALL output summaries per PAC, cycle, office and score bin.

#### Scenario: Office totals reconcile
- **WHEN** summaries are built
- **THEN** for each PAC and cycle, House + Senate dollars equal the `All` office dollars

#### Scenario: Presidential excluded
- **WHEN** summaries are built
- **THEN** only House and Senate offices appear; presidential candidates are not part of the data or the site

### Requirement: Candidate counts on Explore
The Explore page SHALL show the number of candidates alongside dollars: counts labelled on each bar, a "Candidates" measure option, and a table listing dollars and candidate counts per bin.

#### Scenario: Count labels
- **WHEN** a viewer selects Google and Both cycles
- **THEN** each bin shows its candidate count on or above its bar

#### Scenario: Candidates measure
- **WHEN** the viewer selects the "Candidates" measure
- **THEN** bar heights equal the number of distinct candidates per bin

### Requirement: Office filter
Explore, Compare PACs and Candidates SHALL provide an Office filter with options All, House and Senate that applies together with the PAC and cycle filters.

#### Scenario: Senate only
- **WHEN** a viewer selects Senate
- **THEN** charts and tables include only Senate contributions

#### Scenario: Empty office
- **WHEN** the selected PAC, cycle and office have no contributions (for example Anthropic)
- **THEN** a message states that none are recorded and the bins show zero

### Requirement: By-office view
The Explore page SHALL include a chart of the selected PAC's direct dollars and candidate counts by office, broken down by score bin.

#### Scenario: Compare chambers
- **WHEN** a viewer selects a PAC
- **THEN** the chart shows House and Senate bars with dollars and candidate counts
