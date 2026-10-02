## ADDED Requirements

### Requirement: Static Quarto website
The system SHALL provide a Quarto project in `site/` that renders to a static website from precomputed data files, requiring no server at view time.

#### Scenario: Local render
- **WHEN** a developer runs `quarto render site/` after the data step
- **THEN** the site builds into `site/_site/` without errors

### Requirement: Interactive PAC-by-score-bin chart
The site SHALL show dollars by score bin for a selected corporate PAC, with a PAC selector, a toggle between dollars and share of the PAC's total, a cycle filter (2024, 2026, both), and tooltips with bin, dollars, candidate count and share.

#### Scenario: Select a PAC
- **WHEN** a viewer selects Google
- **THEN** the chart shows Google's seven bins, in order from `0` to `100` followed by `No score`

#### Scenario: PAC with no direct contributions
- **WHEN** a viewer selects a PAC whose direct total is zero (e.g. Anthropic)
- **THEN** the PAC remains selectable, all seven bins display as zero, and a message states that no direct candidate contributions are recorded for the period

#### Scenario: Toggle share
- **WHEN** a viewer switches to share of total
- **THEN** the bars show percentages that sum to 100% for the PAC

### Requirement: Cross-PAC comparison
The site SHALL include a comparison view of all PACs across bins.

#### Scenario: Compare PACs
- **WHEN** the comparison view loads
- **THEN** each PAC appears with its bin distribution on a common scale

### Requirement: Candidate drill-down
The site SHALL list the candidates behind a selected PAC and bin with name, party, state, office, score and dollars, sortable and searchable.

#### Scenario: Drill into bin
- **WHEN** a viewer selects a bin for a PAC
- **THEN** a table lists candidates in that bin sorted by dollars descending

### Requirement: Methodology and caveats page
The site SHALL document data sources, the direct-only definition (no indirect money), deduplication, score vintage and bin definitions, and the data refresh date.

#### Scenario: Caveats visible
- **WHEN** a viewer opens the methodology page
- **THEN** it states that scores are 118th Congress and that indirect contributions are not included

### Requirement: GitHub Pages deployment
The repository SHALL include a GitHub Actions workflow that builds the data, renders the site, and deploys it to GitHub Pages on push to `main`.

#### Scenario: Push to main
- **WHEN** a commit lands on `main`
- **THEN** the workflow publishes the rendered site to GitHub Pages

### Requirement: Dark red visual theme
The site SHALL use a dark red theme based on `#780000` for accents and as the darkest value of a single-hue sequential ramp for score bins, with `No score` in a neutral gray, and SHALL NOT use GW OSPO branding.

#### Scenario: Theme applied
- **WHEN** a page is rendered
- **THEN** headings, links and chart accents use `#780000`-based colors and score bins are ordered light to dark by score

### Requirement: Accessible and responsive
The site SHALL meet WCAG AA text contrast on the dark red theme, not rely on color alone to distinguish series, provide text alternatives for charts, and use layouts usable at phone width.

#### Scenario: Phone width
- **WHEN** the site is viewed at 375px width
- **THEN** charts and tables remain readable without horizontal page scroll
