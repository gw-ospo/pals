# Proposal

## Why

Two gaps in the published site. First, nothing tells viewers that the dataset is open and was
assembled by Claude (an AI) and has not been independently validated, which matters because the
name matching and aggregation are automated. Second, the Explore tab shows only dollars, even
though how many candidates sit behind each bar is essential context, and viewers cannot separate
House and Senate giving.

## What Changes

- State, on every page, in the README, and inside each visualization, that the data is open and
  curated by Claude and has not been validated.
- Add the number of candidates to the Explore chart (labels on bars, a "Candidates" measure, and a
  table with dollars and candidate counts side by side).
- Add an Office filter (All, House, Senate) to Explore, Compare PACs and Candidates, and stack House and
  Senate segments within the Explore bars.
- Extend the data step so summaries are produced per office. Presidential candidates are out of scope and are not
  shown anywhere.

## Capabilities

### New Capabilities
- `data-provenance-notice`: Consistent open-data / Claude-curated / not-validated disclosure across the README, site pages and charts.
- `office-breakdown`: Office dimension (House, Senate) in the data, with candidate counts and office filtering/visualization on the site.

### Modified Capabilities

## Impact

`src/pals/donations.py` (office dimension, output schema), `site/*.qmd`, `site/pals_site.py`,
`site/_quarto.yml`, `README.md`, tests. `pac_bin_summary.csv` gains an `office` column.
