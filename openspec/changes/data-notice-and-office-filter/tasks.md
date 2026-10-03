## 1. Data

- [x] 1.1 Add contribution office (row office, id-prefix fallback) to `candidate_totals` and group by office
- [x] 1.2 Extend `bin_summary` with an `office` dimension (All/House/Senate), zero-filled
- [x] 1.3 Tests: office reconciliation, person counted once in All

## 2. Provenance notice

- [x] 2.1 Add `NOTICE` wording and a banner helper to `site/pals_site.py`; show the banner on every page and in `page-footer`
- [x] 2.2 Add the notice as a subtitle on every chart and a caption on the candidate table
- [x] 2.3 Add a "Data status" section to the methodology page and the statement to `README.md`

## 3. Office breakdown and counts

- [x] 3.1 Explore: candidate count labels on bars, "Candidates" measure, values table with dollars and candidates
- [x] 3.2 Explore: Office filter and House/Senate stacked within the bars
- [x] 3.3 Compare PACs: Office filter
- [x] 3.4 Candidates: Office filter and office column
- [x] 3.5 Update methodology (office definition)

## 4. Verify and publish

- [x] 4.1 Render locally and check interactions, empty states, and phone width
- [ ] 4.2 Run tests, commit and push
