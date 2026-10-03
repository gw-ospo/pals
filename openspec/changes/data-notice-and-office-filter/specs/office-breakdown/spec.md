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

### Requirement: Office stacked within score-bin bars
The Explore chart SHALL stack House and Senate segments within each HRC score-bin bar (House at the bottom), with a legend for office, so no separate by-office chart is needed. A total (dollars and candidates) SHALL be labelled above each stack, and the Office filter SHALL narrow the stack to one office.

#### Scenario: Stacked bars
- **WHEN** a viewer selects a PAC with Office set to All
- **THEN** each bin's bar shows a House segment and a Senate segment that add up to the labelled dollar total

#### Scenario: Share measure
- **WHEN** the Share of PAC total measure is selected
- **THEN** segments are shares of the PAC's total across both offices, so the stacks across all bins add up to 100%

#### Scenario: Single office
- **WHEN** a viewer selects Senate
- **THEN** only Senate segments are drawn and the label above each bar shows Senate dollars and candidates
