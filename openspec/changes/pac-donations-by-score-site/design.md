## Context

`data/big-AI-spending-2023-2026.csv` (4,954 rows, FEC Schedule B, filing form F3X) covers six corporate PACs: Microsoft, Amazon, SpaceX, Google NetPAC, Meta and Anthropic (Anthropic has one non-direct row, so it will show as zero). Observed facts that shape the design:

- Direct candidate money = `disbursement_type == "24K"` with `candidate_id`: 3,015 rows, about $6.7M net. Other 24K rows (~$5.3M) go to PACs and parties (leadership PACs, NRCC, ...) and are indirect, so out of scope here.
- 88 negative rows (-$196,850) are voids/refunds; the file has amended filings and two duplicated `transaction_id`s (distinct `sub_id`).
- Recipients span 495 candidate ids from both the 2024 and 2026 cycles, and only ~77% of donation rows' candidate ids are in `candidate_summary_2026.csv`. Matching scorecard rows through that file would mislabel many recipients as unscored.
- The HRC score is the 118th Congress (2023-24) record; 2026-cycle donations are paired with a prior-term score.

## Goals / Non-Goals

**Goals:** accurate direct totals per PAC and candidate; score bins as specified; an interactive static site on GitHub Pages; reproducible data step feeding the site.
**Non-Goals:** indirect/leadership-PAC attribution, other scorecards, new PACs, FEC API refresh (all later changes).

## Decisions

- **Candidate dimension built from the donation file** (`candidate_id`, name, office, state, district), then scorecard-matched with the existing `pals.match` layers. Scorecard rows are the left side, as before. The 2026 summary is not required. Alternative (join via 2026 summary) rejected for the coverage gap above.
- **Dedupe by (`committee_id`, `transaction_id`) keeping max `sub_id`**, then sum signed amounts. Reconciliation table proves direct + excluded = total 24K.
- **Bins as an ordered categorical** in a single function, with tests at boundaries (0, 1, 24, 25, 49, 50, 74, 75, 99, 100, null).
- **Precompute small tidy files** (`pac_bin_summary.csv`, `pac_candidate_totals.csv`) in `data/processed/`; the site reads only these. Keeps rendering fast and the pipeline separable for the future multi-company, refreshable pipeline.
- **Python + Altair (Vega-Lite) in Quarto**, with selection/parameter widgets (dropdown, radio) and embedded data so the page is fully static. The drill-down page uses Quarto's built-in Observable JS (`Inputs.select`, `Inputs.search`, `Inputs.table`) over data passed with `ojs_define`, because filtering by PAC and bin needs client-side state that Altair tables lack. Alternative considered: Observable JS in Quarto, which gives lighter pages and richer interactivity but a second language; chosen Altair for consistency with existing notebooks. Revisit if the embedded data exceeds Altair's row limit (here ~hundreds of rows, fine).
- **Deployment with `quarto-dev/quarto-actions`** (`setup-quarto`, `publish` to GitHub Pages), running the data step first. Raw data is committed, so CI can rebuild without external downloads.
- **Palette:** a dark-red scheme anchored on `#780000` (no GW branding). A single-hue sequential ramp from light tint to `#780000` encodes the ordinal score bins (lightness differences keep it color-blind safe and print-friendly), `No score` is neutral gray, and `#780000` is also the accent for headings, links and highlights. PAC comparison uses `#780000` shades plus direct labels or patterns, not hue alone, to separate PACs.

## Risks / Trade-offs

- Score vintage mismatch for 2026-cycle donations -> labelled prominently; cycle filter lets viewers isolate 2024.
- Name-match errors move dollars between bins -> match report, manual overrides, and a tested review list; show match method in drill-down.
- Many recipients are non-incumbents/challengers and legitimately have no score, so `No score` may be the largest bin -> explain in methodology, not hide.
- Some candidates have two FEC ids (e.g. Senate vs House) -> candidates are keyed per FEC id; scoring uses the matched scorecard row, and totals avoid double counting a donation.
- Altair/Vega embed size and accessibility limits -> aggregate data only; add text summaries and tables as non-visual alternatives.

## Decisions on Open Questions

- Branding: no GW OSPO palette or branding; use the dark-red (`#780000`) scheme above.
- Anthropic: included as a selectable PAC. Its charts will currently show zeros; the site shows an explicit "no direct contributions in this period" message instead of an empty chart so the zero state reads as data, not a bug. Its numbers may change with new years of data or once indirect donations are added.

## Open Questions

- Site title and short project description for the landing page.
