## 1. Direct donations data

- [x] 1.1 Load the spending file with explicit dtypes; implement 24K + `candidate_id` filter in `src/pals/donations.py`
- [x] 1.2 Deduplicate amended transactions (max `sub_id` per `committee_id` + `transaction_id`) and net signed amounts
- [x] 1.3 Build per-PAC, per-candidate, per-cycle totals with candidate name/office/state/district and a PAC short-name map
- [x] 1.4 Write the reconciliation summary (direct, excluded, total 24K per PAC) and tests that it reconciles
- [x] 1.5 Unit tests: refund netting, amendment dedupe, non-candidate 24K exclusion

## 2. Score bins

- [x] 2.1 Build recipient candidate dimension from the donation file and match to scorecard with `pals.match`
- [x] 2.2 Apply manual overrides and write a recipient match report (ambiguous/unmatched)
- [x] 2.3 Implement `score_bin()` with boundary tests (0, 1, 24, 25, 49, 50, 74, 75, 99, 100, null)
- [x] 2.4 Produce `pac_bin_summary.csv` (dollars, candidate count, share; zero-filled bins) and `pac_candidate_totals.csv` in `data/processed/`
- [x] 2.5 Test that each PAC's bin dollars sum to its direct total

## 3. Quarto site

- [x] 3.1 Scaffold `site/` Quarto project (`_quarto.yml`, index, comparison, drill-down, methodology pages) and add the Altair dependency (drill-down uses Observable JS)
- [x] 3.2 Build PAC-by-bin chart (including all-zero state for Anthropic) with PAC selector, dollars/share toggle, cycle filter and tooltips
- [x] 3.3 Build cross-PAC comparison view
- [x] 3.4 Build candidate drill-down table (sortable, searchable) linked to PAC and bin
- [x] 3.5 Write methodology/caveats page (sources, direct-only, dedupe, score vintage, bins, refresh date)
- [x] 3.6 Apply the `#780000` dark-red theme (SCSS variables, Altair theme, gray `No score`), AA contrast, accessible palette, chart text alternatives and phone-width layout; verify locally with `quarto preview`

## 4. Deployment

- [x] 4.1 Add GitHub Actions workflow: set up uv + Quarto, run data step, render, deploy to GitHub Pages
- [x] 4.2 Document enabling Pages (source: GitHub Actions) and local build steps in README
- [ ] 4.3 Verify the published site loads and charts are interactive
