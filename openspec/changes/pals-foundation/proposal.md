## Why

Corporate PAC money reaches candidates directly and indirectly (via party
committees, leadership PACs, joint fundraising committees). No simple FEC
query yields "how much of candidate X's money traces back to Google's PAC".
PALS needs an accurate attribution method, scorecard alignment, and a public site.

## What Changes

- Add FEC bulk-data ingestion with local caching (pilot scope: Google PAC).
- Add a money-flow attribution algorithm (direct + indirect, cycle-safe).
- Add scorecard ingestion/alignment (HRC first, NRA next).
- Add a Quarto website published on GitHub Pages.
- Add a config-driven pipeline to add companies and refresh data.

## Capabilities

### New Capabilities
- `fec-ingestion`: Download, cache, and normalize FEC bulk files.
- `money-flow-attribution`: Compute per-candidate direct and indirect dollars from a source PAC.
- `scorecard-alignment`: Load scorecard scores and join them to candidates.
- `site-publishing`: Quarto visualizations deployed to GitHub Pages.
- `pipeline`: Config-driven multi-company, refreshable runs.

### Modified Capabilities
<!-- none -->

## Impact

New Python package, `data/` layout (raw/interim/processed), `site/` Quarto project,
GitHub Actions workflows. Existing root-level marimo exploration files remain as prototypes.

## Open questions

- Attribution rule for intermediaries: proportional pass-through (share of a committee's
  receipts from the source) vs. time-ordered FIFO. Proposed default: proportional with
  a linear solve (I - M)^-1 over the committee graph, per election cycle.
- Treatment of transfers from individuals/other non-PAC receipts in the denominator.
