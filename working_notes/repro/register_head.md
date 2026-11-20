# 01 Findings register

FreeSense pre-release review at commit `bcaf9f8` (`main`), 2026-09-26. This register consolidates the ten area reports in this folder (`B01` to `B10`) after an independent challenge pass. Codebase map and test/lint baseline: `00-orientation.md`. Owner decisions: `02-decisions.md`. Staged plan: `03-implementation-plan.md`.

## How this register was built

1. **Area reviews.** Ten reviewers (B01 statistics to B10 interface) each wrote a report using the prompt's finding format. Every BLOCKER and HIGH finding cites a reproduction (script, AppTest run or command), and the scripts are kept in the session scratchpad under `agents/B<nn>/`.
2. **Challenge pass.** Three fresh agents that had not seen the reviewers' reasoning were given only the title, location and evidence of every BLOCKER and HIGH finding (24 findings) and asked to reproduce or refute each one with their own code:
   - Pass A: 12 statistics, workflow and import findings. 11 reproduced, 1 partly reproduced (IO-02), 0 refuted.
   - Pass B: 10 testing, security, packaging and documentation findings. 9 reproduced (legal findings: facts only), 1 partly reproduced (DOC-02), 0 refuted.
   - Pass C: the 2 performance BLOCKERs. Both reproduced in the real app.

   **No BLOCKER or HIGH finding was removed.** The two partly reproduced findings keep their surviving parts; the part that failed is stated in their status line.
3. **Severity after challenge.** The challengers recommended severities against the prompt's definitions. I (lead reviewer) accepted most of them and overrode four, with the reason recorded in the status line:
   - Kept HIGH against a MEDIUM recommendation: **STAT-01** (★ significance marks on pure noise with no caveat), **STAT-02** (wrong df; Hedges' g collapses to 0 for small panels), **TEST-02** (B01's statistical defects sit exactly in the paths that lack known-answer tests).
   - Raised MEDIUM to HIGH: **STAT-05** (the segmentation step crashes when any consumer gives every product the same score; pass A reproduced it independently, and straight-lining consumers are common in real data).
   - Downgraded HIGH to MEDIUM on the challengers' recommendation: STAT-03, IO-06, TEST-01, SEC-01 (HIGH if hosted), REL-03 (a licensing decision, D-04), DOC-02.
   - Raised to BLOCKER: FUNC-04, then merged into IO-01 (same root cause).
4. **Deduplication.** 14 findings were merged into the finding with the strongest evidence. They are listed at the end of section 1 and their original text stays in section 2 for traceability.
5. **Conditional severities.** Several findings depend on the deployment decision (D-02). They are shown as, for example, "MEDIUM (HIGH if hosted)", and the plan treats them at the lower severity until D-02 is decided.

## Counts

| Severity | Before challenge (105 findings as filed) | After challenge and consolidation (91 distinct findings) |
|---|---|---|
| BLOCKER | 4 | 4 |
| HIGH | 20 | 12 |
| MEDIUM | 47 | 46 |
| LOW | 34 | 29 |
| Merged into another finding | n/a | 14 |

Conditional: SEC-04 becomes a BLOCKER before the repository or its history is made public. PERF-04, SEC-01 and SEC-05 become HIGH if the app is hosted.

## The four BLOCKERs in one paragraph

All four are silent-wrong-result or crash defects with small fixes:
- **FUNC-01:** Liking LS means are wrong when a product name contains "Var" or "Cov", because parameters are selected by substring.
- **IO-01:** empty rows or blank ID cells become a real product or assessor called "nan". This silently changes DA results and crashes RATA.
- **PERF-01:** Streamlit hashes DataFrames of 50,000 or more rows by sampling 10,000 of them, so a corrected re-upload of a large study can silently return the old statistics.
- **PERF-02:** the optional pingouin ICC confidence-interval block crashes DA on small but valid designs.

None needs more than a day's work including tests.
