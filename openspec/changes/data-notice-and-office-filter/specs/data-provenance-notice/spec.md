## ADDED Requirements

### Requirement: Provenance statement
The project SHALL state that the data is open and was curated by Claude (an AI assistant) and has not been validated, using the same core wording everywhere it appears.

#### Scenario: README
- **WHEN** a reader opens `README.md`
- **THEN** it contains the statement near the top

#### Scenario: Every site page
- **WHEN** any page of the site is rendered
- **THEN** the page shows the statement in a visible notice and in the footer

### Requirement: Statement inside visualizations
Each chart SHALL carry the statement in its subtitle, and the candidate table SHALL show it in a caption, so the notice travels with a screenshot or embed.

#### Scenario: Chart screenshot
- **WHEN** a viewer exports or screenshots a chart
- **THEN** the subtitle reading "Open data curated by Claude; not validated" is part of the image

### Requirement: Methodology disclosure
The methodology page SHALL explain what "not validated" means: matching and aggregation are automated, results have not been independently checked against the FEC or HRC sources, and users should verify before relying on them.

#### Scenario: Methodology page
- **WHEN** a viewer opens the methodology page
- **THEN** a "Data status" section describes these limits
