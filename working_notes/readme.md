# FreeSense pre-release review: summary

Review of `main` at `bcaf9f8`, 2026-09-26. Review only: no application code, tests, data or configuration was changed.

## Overall assessment

- **FreeSense is close to releasable, but not yet.** The core statistics are in good shape. The DA ANOVA matches an independent least-squares calculation on all three of its paths, the CATA and RATA test families are as documented, 366 tests pass, and every module completes end to end on its bundled dataset.
- **What stops a release today is four silent-wrong-result or crash defects, all small to fix:**
  - **FUNC-01:** Liking LS means are wrong when a product name contains "Var" or "Cov".
  - **IO-01:** a trailing empty row becomes a phantom product "nan".
  - **PERF-01:** Streamlit's sampled hashing returns stale statistics after a corrected re-upload of a large study.
  - **PERF-02:** DA crashes on small but valid designs.
- **Input handling is the weakest area.** Decimal commas, semicolon or Latin-1 CSVs, duplicated rows and blank IDs are either silently mishandled or rejected with raw errors. European users will hit these on day one.
- **Three statistical outputs contradict themselves or overstate significance:**
  - **STAT-01:** Liking cluster ★ marks appear on pure noise.
  - **STAT-02:** Liking contrasts use the wrong df.
  - **STAT-03:** RATA Tukey contrasts disagree with the letters on 16 of 420 pairs.
- **The methods reference contradicts the code in ten places a user would copy into a paper (DOC-01).** The export's version stamp `1.0.0` does not identify the build (the tag is 146 commits old), so results are hard to report or reproduce.
- **Release engineering is almost absent:**
  - The GitHub repository is private.
  - Its pushed history contains third-party XLSTAT material.
  - There is no CI and no lockfile.
  - A GPL-3.0 dependency (pingouin) sits under an MIT licence without mention.

  None of this is hard; all of it needs your decisions first.
- **Estimate:** about 16 to 22 working days for the release line after the recorded decisions. All BLOCKERs can be closed within the first week.

## Counts

| Severity | Before challenge (105 as filed) | After challenge and consolidation (91 distinct) |
|---|---|---|
| BLOCKER | 4 | 4 |
| HIGH | 20 | 12 |
| MEDIUM | 47 | 46 |
| LOW | 34 | 29 |
| Merged as duplicates | n/a | 14 |

**Challenge pass.** Three fresh agents independently re-ran all 24 BLOCKER and HIGH findings from their titles and evidence alone. 22 were fully reproduced, 2 were partly reproduced, and none was refuted. Severity changes:
- six HIGH findings downgraded to MEDIUM on the challengers' advice;
- three kept at HIGH against their advice (reasons recorded);
- one MEDIUM raised to HIGH (STAT-05, a segmentation crash on straight-lining consumers);
- one merged into a BLOCKER (FUNC-04 into IO-01).

**Conditional severities.** SEC-04 (third-party files in history) becomes a BLOCKER if the repository is made public as is. PERF-04, SEC-01 and SEC-05 become HIGH if the app is hosted.

## Decisions

The owner recorded decisions on 2026-09-26 (see the "Decided." lines in `02-decisions.md`). In short:
- local install only;
- a fresh public repository;
- version 1.0.0;
- ship Fusion and PrefMap as beta;
- replace pingouin;
- UTF-8 CSV and `.xlsx` only;
- Python 3.12 to 3.14.

`03-implementation-plan.md` has been updated to match; its Stage 0 table summarises every decision and its effect. Follow-up answers are recorded there too: warn above 50 attributes or 5,000 data file rows; rename "Trained panel" to "Profiling" and show Liking before CATA, with the regrouping paused; exports keep all data. Multi-sheet uploads get a sheet picker. No questions remain open. The release is staged private first: the new `FreeSense` repository is created private and shared with testers, with candidates `1.0.0rcN`, and is made public only once all checks pass (plan Stages 9A, 9B and 9C, after the presentation fixes in Stage 8, so testers see them). No target date is set. Test builds are numbered `1.0.0rcN`, and the testing sign-off criteria are agreed (plan Stage 9B). **The plan is final as of 2026-09-27.**

## Environment notes

- The review prompt was written for R/Shiny. The app is Python/Streamlit, so the R tooling was mapped to Python equivalents: pytest, `ruff`, `pytest-cov` and Streamlit AppTest (the mapping table is in `00-orientation.md`).
- **R is not installed** on this machine. `validation/run_all.sh` could not be run; the frozen R reference numbers were checked through `tests/test_validation_pins.py` and independent Python calculations.
- Seven of the ten reviewers were interrupted by an API rate limit and resumed from where they stopped. All ten reports are complete.
- Reproduction scripts for every finding are in [`repro/`](repro/README.md), copied from the session scratchpad, without the extracted third-party files, zip bombs or injection test workbooks.
- `.gitignore` now contains `working_notes/`. That was your edit during the session; the review did not touch it.

## Documents

- [`00-orientation.md`](00-orientation.md): codebase map, stack, module inventory, data flow, dependencies and licences, tests (366 passed, 77% line coverage), lint (226 cosmetic findings), git state, and prior reviews found in history.
- [`01-findings-register.md`](01-findings-register.md): consolidated table and full text of all findings, ordered by severity, with the challenge outcome for each.
- [`02-decisions.md`](02-decisions.md): 21 decisions with options, trade-offs, recommendations and what each blocks.
- [`03-implementation-plan.md`](03-implementation-plan.md): Stage 0 (decisions) to Stage 11 (post-release), release line and release checklist. Each stage is a self-contained brief.
- Area reports:
  - [`B01-statistical-correctness.md`](B01-statistical-correctness.md)
  - [`B02-functional-workflow.md`](B02-functional-workflow.md)
  - [`B03-import-export.md`](B03-import-export.md)
  - [`B04-code-quality.md`](B04-code-quality.md)
  - [`B05-testing.md`](B05-testing.md)
  - [`B06-performance.md`](B06-performance.md)
  - [`B07-security-privacy.md`](B07-security-privacy.md)
  - [`B08-packaging-licensing.md`](B08-packaging-licensing.md)
  - [`B09-documentation.md`](B09-documentation.md)
  - [`B10-interface-accessibility.md`](B10-interface-accessibility.md)
- [`release-review-prompt.md`](release-review-prompt.md): the prompt this review followed.

The review stops here. No stage has been started; the next step is Stage 1.
