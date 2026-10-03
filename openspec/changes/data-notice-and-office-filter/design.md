## Context

The site reads `data/processed/pac_bin_summary.csv` (PAC x cycle x bin) and `pac_candidate_totals.csv`. The source file contains only House (H) and Senate (S) direct recipients, and presidential candidates are excluded from the site; three rows carry an office that differs from the candidate id prefix (a candidate who changed chambers).

## Decisions

- **Office per contribution**, from `candidate_office` on the row (the race the money was given for), falling back to the id prefix. Totals are grouped by PAC, candidate id, cycle and office, so a candidate who ran for both chambers contributes to each. Distinct-candidate counts use the person key within each office scope, and `All` offices counts a person once.
- **Summary schema:** add `office` (`All`, `House`, `Senate`); keep the existing `cycle` and `All` conventions. Zero-filled for every PAC, cycle, office and bin.
- **Candidate counts on Explore:** a third measure ("Candidates") and bar labels that show the count with dollars regardless of the measure, plus a values table with dollars and candidates. A text layer over the bars carries the labels.
- **Office filter** as a Vega-Lite radio param shared by Explore and Compare; an `Inputs.select` on Candidates. House and Senate are stacked within the Explore bars (office as the color encoding, House at the bottom, labels above each stack), instead of a separate by-office chart. Share is relative to the PAC's total across both offices so stacks sum correctly.
- **Provenance statement:** single source for the wording in `site/pals_site.py` (`NOTICE`), rendered as a banner include on each page, the `page-footer`, chart subtitles and the table caption. Core wording: "Open data curated by Claude; not validated."
- **Empty states** reuse the pattern already used for Anthropic.

## Risks / Trade-offs

- Chart subtitles add vertical space; kept to one line at phone width.
- Per-office counts do not sum to the All count when a person ran for both chambers; the table notes this.
