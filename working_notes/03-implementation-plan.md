# 03 Staged implementation plan (final, 2026-09-27)

FreeSense pre-release review, commit `bcaf9f8`, 2026-09-26. This plan turns `01-findings-register.md` (91 distinct findings after challenge) and `02-decisions.md` (21 decisions) into staged work. Finding IDs are register IDs; merged findings are fixed with the finding they merged into.

## How to use this plan

- Each stage is written to be handed to a Claude Code session as a self-contained task. The "Brief" in each stage gives the root cause and the intended fix, so the session does not need to re-read the review reports. The full evidence for any finding is in `01-findings-register.md` under its ID, if needed, and the scripts that reproduce it are in `working_notes/repro/` (see its README).
- **Always first, in every stage:** read `CLAUDE.md` and follow its conventions. That means invoking the `developing-with-streamlit` skill before touching `app.py`, `core/state.py`, `core/upload_ui.py`, `modules/*/{ui,workflow}.py` or `utils/ui_shell.py`. It also covers the widget persistence rules, the p-value convention, "never `.get()` a missing statistical parameter", `render_result_table`/`render_chart`, and the layer rule (statistics only in `stats/`).
- One branch per stage, named `stage-<n>-<slug>`. Every stage ends with `python -m pytest tests/ -n auto -rs` green and, from Stage 1 onwards, green CI.
- **Every defect fix lands with a regression test that fails before the fix.** Every fix that touches `stats/` also records a before/after on the sensochoc reference set: `validation/regression/snapshot_replicates.py` and `compare_snapshots.py` already exist for this. Outputs for complete designs must stay bit-identical unless the finding says the number was wrong.
- Update `CHANGELOG.md` under `[Unreleased]` in every stage and delete rows from `docs/open-items.md` as they close. `docs/open-items.md` should first receive the open register items (Stage 1). It currently says "Nothing is open", which this review shows is not true.

## Ordering and why it differs slightly from the default

The default order is safety net, then correctness blockers, then data handling, then docs and packaging, then polish. I kept it, with two adjustments:

1. **The four BLOCKERs are small (each under half a day), silent or crashing, and independent of any decision except D-04.** Stage 1 is deliberately thin (CI plus lockfile), so Stage 2 can start within a day. I did not put the full known-answer test set (TEST-02) in Stage 1: several of those tests target methods that Stage 4 changes, and writing a pin for a number about to change is waste. Known-answer tests for methods Stage 4 does not touch go into Stage 1. Those for methods it does touch are written in Stage 4, alongside the fix.
2. **The release repository (Stage 9) comes last on purpose, after Stage 8.** All other stages work in the current private repository. The history clean-up (SEC-04) happens once, from the finished state (D-03 option 1: a fresh repository). The new repository starts private, goes through private testing (Stage 9B), and is made public only after every check passes (Stage 9C).

---

## Stage 0: Decisions (recorded 2026-09-26 and 2026-09-27; final)

The owner's decisions are recorded in `02-decisions.md` under each "Decided." line. The stage briefs below already apply them; this table is the summary a stage session needs.

| Decision | Outcome | Effect on the plan |
|---|---|---|
| D-01 Version | Option 1: release as **1.0.0**, delete the unpushed local `v1.0.0` tag, adopt the version policy. Builds given to testers are `1.0.0rc1`, `1.0.0rc2` and so on (owner, 2026-09-27) | Stages 6, 9 |
| D-02 Deployment | Option 1: **local install only** | Stage 10 (hosted hardening) removed from the plan. SEC-01 stays MEDIUM; PERF-04, SEC-02, SEC-05 and SEC-06 are treated at their local severity |
| D-03 Repository | Option 1: **fresh repository** named `FreeSense`, with the current private repository renamed out of the way first (see "Answer to the rename question" below). The new repository starts **private**, is shared with testers, and is made public only after all checks pass (owner, 2026-09-27) | Stage 9 (Stage 9A, Stage 9B, Stage 9C) |
| D-04 pingouin | Option 1: **replace** it with a closed-form ICC(3,1) confidence interval and remove the dependency | Stage 2 (with PERF-02); REL-03 and the pingouin half of PERF-03 close there |
| D-05 Example data | Option 1: keep bundling, add `example_data/COPYING`, fix the two examples that do not load | Stages 3 and 7 |
| D-06 Beta modules | Option 1: **ship Fusion and PrefMap as beta**, with STAT-04 and FUNC-07 fixed and the loader tested | Stages 3, 4, 5 |
| D-07 Liking statistics | Option 1 for both: RCBD error df for contrast and CLD; cluster comparison **descriptive only** (no p-values, no ★) | Stage 4 |
| D-08 RATA Tukey | Option 1: pooled assessor-blocked error term for both CLD and contrast | Stage 4 |
| D-09 Input formats | Option 2: **UTF-8 comma CSV and `.xlsx` only**; everything else is refused with a message telling the user how to re-save | Stage 3 (smaller than before: no delimiter or encoding auto-detection, `.xls` removed from uploaders) |
| D-10 Platforms | Option 2: **Python 3.12 to 3.14; Linux and macOS in CI; Windows best effort** | Stage 1 |
| D-11 Privacy | Option 1: local-only "your data never leaves your computer" statement. Exports keep **everything**, including `Raw_Data` with IDs and demographics, so users have a complete data set and can delete what they do not want to keep (owner, 2026-09-26) | Stage 7 (say so in "Your data") |
| D-12 Support | GitHub issues plus a one-line disclaimer. The contact email is added later, but it must exist before any tester without a GitHub account is given the app (Stage 9B) | Stages 7, Stage 9B |
| D-13 Validation claims | Option 2: "cross-checked against R on published datasets", with the exceptions listed | Stage 7 |
| D-14 DA model name | Option 3: **"Mixed-model ANOVA (conditional F-test)"** plus one explanatory sentence | Stage 7 |
| D-15 Palette | Option 3: fix UI-02 and UI-03, and make a corrected colour-blind-safe palette the default (revisit if it looks wrong) | Stage 8 |
| D-16 Landing grouping | Keep the current three-column layout for now. Rename "Trained panel" to **"Profiling"**, giving the sections **Consumer methods**, **Profiling** and **Mapping & integration**. In the consumer column, show Liking first and CATA second. The fuller regrouping is paused and will be worked on separately later (Stage 11) | Stage 8 (rename and reorder), Stage 7 (README/About wording) |
| D-17 Study size | Soft warning above **50 attributes** or above **5,000 data file rows** (evaluations: assessor x product x replicate). Never blocks | Stage 3 |
| D-18 Export precision | Full precision, formatting via Excel number formats only | Stage 6 |
| D-19 Citation | Option 3 now: per-module "how to report this analysis" text in the app and in every export. `CITATION.cff` and the Zenodo DOI are deferred | Stage 6; REL-10 moves to Stage 11 |
| D-20 Penalty independence | Ship as is, with the existing caveat | No work |
| D-21 About page | Short user-facing About, and README cleaned up for release | Stage 7 |

### Answer to the rename question (D-03)

Yes, you can rename a GitHub repository, including to a different name after it was already renamed once (Settings, General, Repository name). The steps for option 1:

1. Rename the current private repository to, for example, `FreeSense-dev`, and keep it private as the development archive.
2. Update your local clone's remote: `git remote set-url origin https://github.com/Sesnor-y/FreeSense-dev.git`.
3. Create a new repository called `FreeSense`, private at first, and push the release state to it as a single commit (Stage 9A). It is made public later (Stage 9C).

GitHub redirects the old name to a renamed repository only until a new repository with the old name is created. After step 3, `github.com/Sesnor-y/FreeSense` points at the new repository. The repository was private, so nobody else depends on that redirect.

Source: GitHub Docs, "Renaming a repository". I have not re-checked that page in this session, so confirm the redirect behaviour there before step 3.

### Follow-up questions (all answered)

- **Q1, D-17 row threshold.** Answered: warn above 50 attributes or above 5,000 data file rows.
- **Q2, D-16 layout.** Answered: keep the layout, rename "Trained panel" to "Profiling", show Liking before CATA; the regrouping is paused.
- **Q3, multi-sheet workbooks (IO-05).** Answered: a sheet picker, with the chosen sheet recorded in `Run_Parameters`.

---

## Stage 1: Safety net (CI, lockfile, visible skips, backlog) — COMPLETE 2026-09-27

**Goal.** Every later change is tested automatically on the supported Pythons, from a reproducible environment, and nothing skips silently.

**Findings.** TEST-01, REL-04, REL-06, TEST-08; plus the part of TEST-02 that covers methods Stage 4 does not change (B05 minimum test set items 2, 3, 4, 5, 9, 10, 11, 13).

**Brief.**
- Add `.github/workflows/ci.yml`. It runs `pip install -r requirements-dev.txt` and then `python -m pytest tests/ -n auto -rs`, on Python 3.12 and 3.14 on Linux (D-10), plus one macOS job on 3.14. Windows is best effort: no CI job, but a manual smoke test is in the release checklist. Also add `ruff check` restricted to rule groups E9 and F821 (real errors only; the 226 cosmetic findings are post-release, see CODE-06, and E712 must not be auto-fixed because the comparisons are on pandas Series).
- Split `requirements-dev.txt` (`-r requirements.txt`, pytest, pytest-xdist, ruff) from `requirements.txt`. Remove pytest from the runtime list. Set `[tool.ruff] target-version = "py312"`, and change README's claim from "3.11 to 3.14" to "3.12 to 3.14; tested on Linux and macOS; Windows best effort" (D-10).
- Generate a lock or constraints file per supported Python (`pip-compile --generate-hashes` or `uv pip compile`). Reference it in README as the reproducible install. Pin `wrapt` to a final release (a fresh install currently resolves `2.4.2rc1` through formulaic's pre-release specifier).
- `pytest.ini`: add `-rs`. Make `tests/conftest.py::_existing` fail instead of skip when `FREESENSE_REQUIRE_DATA=1`, and set that variable in CI (94 tests skip without `example_data/`).
- Known-answer tests for unchanged methods (all pure Python, no R). The data and assertions are described in B05's minimum test set table:
  - CATA McNemar: asymptotic `p_raw` equals `chi2.sf((b-c)^2/(b+c), 1)` on all 465 pairs, and within-attribute BH `p_adj` equals `multipletests` (TEST-03).
  - Tighten `tests/test_validation_pins.py` p-value tolerances to 1e-8 where agreement is already 1e-11 or better, and pin per attribute rather than summed (TEST-04). Do not change the stats-layer rounding of F/LR/ICC here; that is IO-08 in Stage 6.
  - DA Type III with unequal replication against `statsmodels anova_lm(typ=3)` with Sum coding, both branches of the conditional pooling.
  - DA/RATA PCA against `numpy.linalg.svd` of the standardised means (up to sign); CVA eigenvalues against `scipy.linalg.eigh(B, W)`.
  - CATA penalty (Welch t via `scipy.stats.ttest_ind(equal_var=False)`) and CATA contrast (McNemar against reference, within-product BH).
  - RATA zero-filled LMM LRT against a hand `MixedLM` ML fit.
  - Panel performance discrimination F against `scipy.stats.f_oneway`; agreement r against `pearsonr` with leave-one-out consensus.
- Mark each pinned quantity in `validation/README.md` as "independent engine" or "R port of FreeSense spec" (TEST-05). This is text only.
- Copy every open register finding (BLOCKER to LOW, excluding merged ones) into `docs/open-items.md` as one row each, with its register ID.

**Files.** `.github/workflows/ci.yml` (new), `requirements.txt`, `requirements-dev.txt` (new), lock/constraints file(s) (new), `pyproject.toml`, `pytest.ini`, `tests/conftest.py`, `tests/test_validation_pins.py`, new `tests/test_known_answers_*.py`, `validation/README.md`, `docs/open-items.md`, `README.md` (install section).

**Entry criteria.** None (D-10 decided).

**Exit criteria.**
- CI green on Python 3.12 and 3.14 (Linux) and 3.14 (macOS), installed from the lockfile.
- `pytest -rs` shows zero skips when `FREESENSE_REQUIRE_DATA=1`.
- The new known-answer tests pass within 1e-8 (p-values) or 1e-10 (estimates) of their independent references.
- `docs/open-items.md` lists every open register ID.

**Effort.** M (about 2 days).

**Risks.** A fresh CI environment may surface version-sensitive pins (the concern behind TEST-01). If so, pin the version in the lockfile and record which library moved the number. Do not loosen the test.

**Outcome (2026-09-27, branch `stage-1-safety-net`).** Delivered as briefed, and every known-answer test agreed with production. None disagreed.
- **CI result and STAT-13.** The first push ran all three jobs. Both 3.14 jobs passed. Linux 3.12 failed one existing test, `tests/test_unbalanced_designs.py::test_anova_with_empty_cells_uses_the_additive_model`: 376 passed, 1 failed.
  - This was not version drift: the lock is identical, and the test passed on a locally built 3.12 from the same lock. The cause was a production defect, recorded as **STAT-13**. On the DA empty-cell path, the residual and interaction SS came from a rank-deficient `statsmodels` OLS fit, which is inexact and machine-dependent.
  - On the owner's instruction (2026-09-27), STAT-13 was **fixed in Stage 1** rather than in Stage 2, so Stage 1 merges green. `stats/da_anova.py` now takes the pure error from the within-cell SS (`_within_cell_ss`) and the diagnostics from cell means (`_cell_means`); the rank-deficient model is never fitted.
  - The loose `rel=1e-3` test was replaced by exact values, plus a new diagnostics test. Both failed before the fix.
  - The sensochoc snapshot (`validation/regression/snapshot_replicates.py --out stat13_before/stat13_after`, 18 files) is byte-identical.
  - Local run: 378 passed, 0 skipped, ruff clean.
  - CI on the pushed fix commit (`105715a`) is **green on all three jobs**; the owner confirmed on 2026-09-27. TEST-01 and REL-06 are closed.
- **Status: Stage 1 COMPLETE (2026-09-27).** Next: merge `stage-1-safety-net` into `main`, then start Stage 2 on `stage-2-blockers`.
Facts later stages rely on:
- **Locks.** There are six lock files: `requirements/lock-py3.{12,13,14}.txt` (runtime) and `requirements/dev-lock-py3.{12,13,14}.txt` (plus pytest, pytest-xdist and ruff). They are generated with `uv pip compile --universal --generate-hashes --prerelease disallow`; the exact loop is in README. **Any stage that edits `requirements.txt` or `requirements-dev.txt` must regenerate all six in the same commit.** CI installs `dev-lock-py<ver>.txt` with `pip --require-hashes`.
- **Rounded-value pins.** Where the stats layer rounds, several Stage 1 tests assert *equality with the rounded reference* rather than a tolerance. That covers DA `F_*` (3 dp), `full_df` MS and SS (4 dp), panel F and r (3 dp) and RATA `lr_stat` (3 dp), in `tests/test_known_answers_{da,rata}.py` and `tests/test_unbalanced_designs.py`. Removing the rounding (IO-08, Stage 6) makes them fail by design; see Stage 6.
- **Skip helper.** `tests/conftest.py::skip_or_fail(reason)` is the only allowed way to skip a test for missing data. CI sets `FREESENSE_REQUIRE_DATA=1`, which turns such a skip into a failure.
- **Ruff.** `pyproject.toml` selects only E9 and F821 and excludes `working_notes/`. CLAUDE.md no longer says "No linter is configured".
- **Backlog.** `docs/open-items.md` holds 85 rows: the 92 distinct findings (91 from the review plus STAT-13) minus REL-04, TEST-03, TEST-04, TEST-08, STAT-13, TEST-01 and REL-06, which closed here, so 85 rows remain. REL-06's remaining user-facing claims are checked in Stage 7. TEST-02, TEST-05 and CODE-06 stay open with a "Remaining" note.
- **Dependency drift found while locking.** The maintainer's `env/` differed from the lock (`wrapt` 2.4.2rc1 vs 2.5.0, `pingouin` 0.6.1 vs 0.7.0, plus minor bumps to fonttools, pytz and uvicorn). It was re-synced to `requirements/dev-lock-py3.14.txt` on 2026-09-27, so `env/` now equals CI's 3.14 environment.
- **Machine-dependent numerics.** STAT-13 showed that the same lock can give different numbers on different CPUs/BLAS when a computation is ill-conditioned. Treat any test that passes locally but fails on one CI runner as a possible numerical defect first, not as noise. Never loosen the tolerance to get green.

---

## Stage 2: BLOCKERs and crashes — COMPLETE 2026-09-28

**Goal.** No silent wrong result and no crash in a core workflow for any input the app accepts.

**Findings.** FUNC-01, IO-01 (with FUNC-04), PERF-01, PERF-02, STAT-05, STAT-06, PERF-06, FUNC-02.

**Brief.**
- **FUNC-01 (BLOCKER), `stats/liking.py:258-261`.** Fixed-effect parameters are selected with `'Var' not in p and 'Cov' not in p`. Parameter names contain product labels, so a product named "Variety A" is dropped, and every LS mean, SE, letter and contrast built from that matrix is wrong. Fix: select by `result.fe_params.index` (statsmodels exposes it). Test: hedochoc with two products renamed "Variety A"/"Covent B"; LS means must equal those from the unrenamed run (5.3288 and 5.6892, not 5.7658). Grep `stats/` for any other parameter selection by substring and fix it the same way.
- **IO-01 (BLOCKER), `core/data.py:17-37` and `:193-195`.** `load_data` keeps fully empty rows, and `clean_and_structure_data` casts meta columns with `astype(str)`, so NaN becomes the level `'nan'`. DA then analyses a phantom product and assessor (and silently switches to the empty-cell Type II path); RATA crashes with `PatsyError`. Fix: in `load_data`, `dropna(how="all")` on rows and on columns, drop empty `Unnamed: n` columns, and report the counts. In `clean_and_structure_data`, before the `str` cast, reject rows with a missing value in any mapped meta column: block the run and name the rows. Tests: trailing empty rows, a blank product cell and a blank assessor cell, for DA, RATA, CATA and Liking. Results must equal the clean-file results, or the run must be blocked with a message.
- **PERF-01 (BLOCKER), every `@st.cache_data` function that takes `df_long`.** Streamlit 1.64 hashes a DataFrame of 50,000 or more rows by sampling 10,000 rows (plus shape and dtypes). A corrected re-upload of the same shape therefore returns the old cached statistics (reproduced in the app: Cochran's Q p 0.80 instead of 0.012). Fix: pass `hash_funcs={pd.DataFrame: <full content hash>}` on every such cache. A helper in `core/` using `pd.util.hash_pandas_object(df, index=True).values` plus the column names and dtypes costs about 50 ms per million rows. Alternatively, compute a digest once per upload and pass it as an extra argument. Nested caches (`build_citation_matrix` calls `build_citation_counts`) need the same treatment. Test: a frame above 60,000 rows, change one cell outside the sample (use the same seed-0 sample to pick it), and assert that the cached function returns the new value.
- **PERF-02 (BLOCKER), `stats/panel_performance.py:251-264`, together with REL-03 and the pingouin half of PERF-03 (D-04 option 1).** The optional pingouin `intraclass_corr` CI raises `AssertionError` (fewer than 5 values) for valid small designs, for example 2 products x 2 sessions, and the exception is not caught. The loop is also about 75% of DA run time. Fix:
  - Remove pingouin. Compute the ICC(3,1) confidence interval in closed form from the two-way ANOVA mean squares the module already computes (F-based interval, McGraw and Wong 1996, case 3, consistency). Put it in `stats/panel_performance.py` next to the OLS ICC.
  - Where the interval is undefined (too few values, zero error variance), return NaN and give the reason in a column, never raise.
  - Before deleting pingouin, record its CI output on sensochoc and on two small synthetic designs as a frozen reference test (tolerance 1e-8). Record it from the **locked** environment (pingouin 0.7.0); the maintainer's `env/` had 0.6.1 before Stage 1. Check the formula against the paper, not only against pingouin.
  - Remove `pingouin` from `requirements.txt`, all six lock files in `requirements/` (regenerate them with the README loop, which also drops its transitive dependencies) and README (dependency table and licence section). Remove the "degrades gracefully without pingouin" caption and the `PINGOUIN_AVAILABLE` branches. Rename the CI export columns if their names say "approx", and update `utils/export.py` and its tests in the same commit.
  - Test: the six designs in the register evidence all complete; the CI matches the frozen reference; a DA run on sensochoc is at least 50% faster than before.
- **STAT-05, `stats/segmentation.py:27-35`.** Row standardisation divides by zero for a consumer who gives every product the same score, and `compute_ahc_clusters` raises `ValueError` (not finite distances). Fix: exclude zero-variance consumers before standardising, report the count on screen and in the export, and guard the call sites (`modules/liking/workflow.py:1360`, `:1573`).
- **STAT-06, `stats/da_anova.py::run_da_anova` (the replicated branch; line numbers moved in Stage 1).** A mapped replicate column with a single session gives an error row for every attribute. Fix: when every assessor x product cell has one observation, run the non-replicated model and say so in Step 1. Since STAT-13, `_within_cell_ss(sub, ...)` returns the pure-error df (n - number of non-empty cells); df = 0 is exactly this condition, so use it as the test rather than counting sessions. It also covers a design where the replicate column has several values but no cell is actually replicated.
- **PERF-06, `stats/panel_performance.py:130-139`.** A single-attribute DA crashes in `groupby.apply`. Use `groupby('attribute')['neg_log_p'].rank(pct=True)`. This also removes the pandas FutureWarning (CODE-10).
- **FUNC-02, `stats/panel_performance.py:551` via DA Step 1.** When no attribute column is numeric (for example a decimal-comma file), DA shows "N blank cells" and then a `KeyError: 'mean_bias'` traceback. Fix: DA Step 1 detects attribute columns that are mostly non-numeric (RATA already does) and blocks the run with a message naming the cause (see IO-02 in Stage 3 for the wording). `compute_scale_usage` should return an empty frame, not raise, when given no numeric data.

**Findings closed here as well.** REL-03 (pingouin removed), PERF-03 part (a).

**Files.** `stats/liking.py`, `core/data.py`, a new small hashing helper in `core/` (for example `core/cache.py`), every `stats/*.py` with a `df_long` cache, `stats/panel_performance.py`, `stats/segmentation.py`, `stats/da_anova.py`, `modules/descriptive/{ui,workflow}.py`, `modules/liking/workflow.py`, `requirements.txt`, `requirements/*.txt` (regenerated), `README.md` (dependency and licence sections), `utils/export.py`, tests.

**Entry criteria.** Stage 1 merged into `main` with CI green on all three jobs. STAT-13, the first CI failure, was fixed in Stage 1. Branch `stage-2-blockers` from that `main`.

**Exit criteria.**
- One regression test per finding, each failing on the Stage 1 merge commit and passing after the fix.
- CI green on all three jobs. Stage 1 CI logs show warnings that this stage should remove: the pingouin `RuntimeWarning`s (PERF-02) and the pandas `DataFrameGroupBy.apply` `FutureWarning` (PERF-06/CODE-10). Check the warnings summary of the final CI run to confirm.
- sensochoc/hedochoc/bread snapshots are bit-identical to before (none of these fixes should move a complete-design number).
- An AppTest run of each of the six bundled datasets completes every step with no exception element.

**Effort.** M (2 to 3 days).

**How to take the before/after snapshots (as used for STAT-13 in Stage 1).** `env/bin/python validation/regression/snapshot_replicates.py --out <tag>` writes 18 CSVs (RATA and DA on sensochoc) to the git-ignored `validation/regression/_out/<tag>/`. Take `before` on the branch point and `after` on the finished branch, then `cmp` each file. The script covers only sensochoc: hedochoc (Liking; FUNC-01, STAT-05) and bread (CATA; PERF-01) need their own before/after dumps. Add them to the script or write a sibling script in this stage.

**Risks.** The PERF-01 hash adds a little cost to every cached call; measure it on the B06 realistic sizes (it should be under 0.1 s). The ICC CI replacement changes exported values slightly where pingouin's approximation differed from the closed form. Record the before/after in the CHANGELOG.

**Outcome (2026-09-27, branch `stage-2-blockers`; first CI run failed on untracked fixtures and the second on a macOS-only LMM tolerance; both fixed. CI on `9c0d074` is **green on all three jobs** (owner confirmed 2026-09-28)).** All eight findings are fixed, each with a regression test that fails on the Stage 1 merge commit (`8a030b9`). One new defect, FUNC-13, was found and fixed here.

Results:
- **Local run:** 453 passed, 1 xfailed (strict, DOC-06), 0 skipped with `FREESENSE_REQUIRE_DATA=1`; ruff clean.
- **Failing before the fix:** checked on a worktree of `8a030b9`. PERF-01 and PERF-02 were checked in a scratch venv built from that commit's `dev-lock-py3.14.txt` (pingouin 0.7.0):
  - the three register PERF-02 designs raise pingouin's `AssertionError`;
  - the cached Cochran's Q stays at 83.36 after a correction, where the true value is 59.35.
- **DA speed on sensochoc** ("Run full analysis", caching off):
  - FDR, the app default: 4.85 s → 1.46 s (−70 %);
  - Tukey-Kramer: 6.58 s → 3.22 s (−51 %).
- **Snapshots:** the 18 sensochoc RATA/DA files and the hedochoc/bread files are byte-identical, except `da_repeatability.csv`:
  - its CI columns are new;
  - two ICCs round the other way at an exact decimal tie (panelist 13 Acidity −0.113 → −0.112; panelist 26 Astringency −0.063 → −0.062), and eight zeros change sign.
  This comes from one separate commit (`4fff241`), which replaces the per-block statsmodels formula fit with `numpy.linalg.lstsq`. Without it the snapshot is byte-identical, but the Tukey run is only about 31 % faster (6.72 → 4.61 s), so the ≥ 50 % criterion fails. **Decided (owner, 2026-09-27): keep it.** The owner accepted the speed-up on the condition that it does not affect statistical correctness in a meaningful way. It does not:
  - the sums of squares agree with statsmodels to 1.8e-14 relative;
  - the only visible difference is the 3-dp display rounding of two ICCs that sit exactly on a 0.0005 tie, plus eight signed zeros;
  - no F, p-value, interval or assessor flag changes (ICC is context-only);
  - the tie flips vanish when IO-08 (Stage 6) removes the rounding.

- **Status: Stage 2 COMPLETE (2026-09-28).** Next: merge `stage-2-blockers` into `main`, then start Stage 3 on `stage-3-input-integrity`.

Facts later stages rely on:
- **New defect FUNC-13 (fixed here).** A blank liking score made `mixedlm` fail on every optimiser. The Liking module then showed all-NaN results under a "convergence warning", and Step 2 crashed because two equal (empty) charts collided: `render_chart` did not pass its key to `st.plotly_chart`. Found by the new real-upload test on the bundled JAR file. Blank liking rows are now dropped (captioned; `blank_liking_rows_dropped` in `Run_Parameters`), a failed fit shows an error, and `render_chart` passes `key=`. Every `render_chart` key must therefore be unique per page; the download buttons already required that.
- **pingouin 0.7.0 never produced an interval.** It renamed `ICC3` to `ICC(C,1)`, so the old lookup raised `IndexError`, which was caught, on every block. The "before" CI columns in the locked environment were therefore all NaN. pingouin, pandas-flavor, seaborn, tabulate and xarray are gone from the six locks; nothing else moved. The maintainer's `env/` was synced by uninstalling those five.
- **Upload helpers Stage 3 should build on,** in `core/upload_validation.py`:
  - `missing_id_cells`/`missing_id_message`. File row numbers are `index + 2`: `load_data` no longer resets the index after dropping empty rows, so do not add a `reset_index()` there.
  - `non_numeric_attribute_columns`/`non_numeric_message` (FUNC-02). These are used only by DA Step 1 so far. IO-02 should apply them to RATA (whose own check still counts blanks as text), CATA and `load_precomputed_means`, and unify the wording.
  - `load_data` records `df.attrs['dropped_empty_rows'|'dropped_empty_columns']`; `utils.ui_shell.render_load_notes` captions them.
- **FUNC-03 must run before the STAT-06 check.** DA Step 1's "analysed without replicates" warning and the Run handler's decision both count observations per assessor × product cell. A doubled single-session file therefore looks replicated. Stage 3's duplicate check has to block first; its test should include a duplicated single-session file.
- **Result shapes that changed:**
  - `compute_repeatability` returns `ICC_lower`, `ICC_upper` and `ICC_CI_note` (was `ICC_lower_approx`/`ICC_upper_approx`), still rounded to 3 dp. IO-08 (Stage 6) should remove that rounding with the rest; the tie flips above then disappear.
  - Segmentation results carry `zero_variance_consumers` and `n_consumers_zero_variance`.
  - `liking_cluster_run` has `n_zero_variance_excluded`.
  - `da_run_options` has `replicate_column_unused`, and the Run handler sets `da_col_map['replicate']` to None when no cell is replicated.
- **Caching.** Every `@st.cache_data` in `core/data.py` and `stats/` passes `hash_funcs=FULL_CONTENT_HASH` (`core/cache.py`). `tests/test_cache_full_hash.py` fails on a new cache that omits it.
- **Real-upload AppTest.** `tests/test_apptest_bundled_datasets.py` drives the real `st.file_uploader` for every bundled dataset and visits every step. This is a start on Stage 5 item 7. Two follow-ups:
  - PrefMap still uploads the cocktail liking pivoted to wide in the test. Switch it to the shipped wide file when FUNC-07 lands (Stage 3).
  - `test_jar_example_is_detected_as_jar` is a strict xfail for DOC-06 (Stage 7). It will fail, as intended, once a numerically coded JAR example ships; remove the marker then.
- **`.gitignore` drops every `.csv`/`.xlsx`/`.xls`/`.xlsm` outside the negated folders.** The first Stage 2 push failed in CI (4 errors in `test_icc_confidence_interval.py`): `git add tests/fixtures/` had silently skipped the fixture CSVs, and the tests passed locally on the untracked files. `tests/fixtures/**` is now negated for all four extensions. Stage 3's bad-file fixtures live there. Before pushing, run the suite on a clean `git worktree add --detach <dir> HEAD`, not the working tree.
- **Iterative fits are only reproducible to their convergence tolerance across parameterisations and CPUs.** The second push failed on macOS only: the FUNC-01 test compared the Liking LMM before and after a rename that also moved the reference level. That reparameterises the REML fit, and the optimiser then stops at a slightly different point, 7e-15 relative on Linux but 2.3e-9 on the macOS runner, against a 1e-9 test tolerance. This is fit precision, not a defect (STAT-13, by contrast, was a 0.2 % error in F). The test now makes two exact claims: an order-preserving rename must be bit-identical, and the register's rename must reproduce the register's 4-dp values. **Rule for later stages (Stage 4 LMM work especially):** only pin two different optimisation paths at the precision the claim needs, and say why in the test. To show that a change has no effect, compare runs with an identical parameterisation, exactly.
- **Warnings left in the suite** (for the CI warnings check): only numpy's "Degrees of freedom <= 0" / "invalid value in scalar divide" and scipy's `ConstantInputWarning` from `compute_agreement`. The pingouin `RuntimeWarning`s and the `DataFrameGroupBy.apply` `FutureWarning` are gone.
- **Snapshots.** `validation/regression/snapshot_consumer.py` covers hedochoc (Liking LMM, CLD, AHC/k-means with and without standardising), bread (Cochran's Q, citation tables, McNemar, penalty) and sensochoc panel performance, and prints the DA run time. `freeze_icc_ci_pingouin.py` documents how the frozen pingouin reference was made.

---

## Stage 3: Input integrity and export safety — COMPLETE 2026-09-28

**Goal.** The app either reads a file correctly or refuses it with a message a sensory scientist can act on. It never silently turns data into zeros, missing values or duplicates, and it never writes a live formula into an export.

**Findings.** FUNC-03, IO-02 (with FUNC-06), FUNC-05 (with IO-03, IO-04), IO-05, FUNC-07, TEST-06, SEC-01, SEC-07, FUNC-10, FUNC-12, STAT-08, and the D-17 study-size warning (from PERF-04).

**Brief.**
- **FUNC-03, duplicates.** No module checks for rows duplicated on assessor x product x replicate. A doubled DA file makes every interaction significant and changes the error term. Fix: every raw-data module's Step 1 counts such duplicates and blocks the run with the count and example rows. Offer a "they are genuine replicates, map a replicate column" hint.
  - (Stage 2 note) Block duplicates *before* the STAT-06 "analysed without replicates" check in DA Step 1 and the Run handler: both count observations per cell, so a doubled single-session file currently looks replicated. Add that case to the fixture set.
- (Stage 2 note) Start from `core.upload_validation.non_numeric_attribute_columns` / `non_numeric_message` (FUNC-02, DA only so far) and `missing_id_cells`; keep `load_data`'s index un-reset so row numbers stay right.
- **IO-02, decimal commas and text in numeric columns.** RATA zero-fills "7,5", DA drops it, both under a "blank cells" warning, and the means-table loader drops an all-comma column. Fix: before numeric coercion, count non-empty cells that fail `to_numeric`, and report them separately from true blanks, with the column name and example values. Block the run when they match `^\d+,\d+$` and say how to fix the file. Never zero-fill a non-empty cell. Apply this in `clean_and_structure_data` and `load_precomputed_means`.
- **FUNC-05, reader robustness (D-09 option 2: UTF-8 comma-separated CSV and `.xlsx` only).**
  - Compare extensions case-insensitively, so `.CSV` is read as CSV (today it goes to `read_excel`).
  - Remove `xls` from every uploader's `type=` list; do not add `xlrd`. Check `type=` lists everywhere so no uploader still offers `xlsm`/`xls` unless it is really supported (`xlsm` opens with openpyxl, so it can stay if wanted).
  - A CSV that parses to a single column, where that column's header contains `;` or a tab, is refused: "This file uses semicolons (or tabs) as separators. FreeSense reads comma-separated CSV (UTF-8) or .xlsx. In Excel: File, Save As, 'CSV UTF-8 (Comma delimited)', or save as .xlsx."
  - On `UnicodeDecodeError`, refuse with the same instruction. Never show a raw codec error. Note for the message: Excel's plain "CSV" save on Windows uses Windows-1252. Only files with non-ASCII characters (umlauts, accents) fail, so the message should mention special characters.
  - Put the messages in one place (`core/data.py` raising a typed `UnsupportedFileError`, rendered by `utils/ui_shell.render_data_upload_section`). Every uploader then behaves the same.
- **IO-05, multi-sheet workbooks (decided: sheet picker).** When a workbook has more than one sheet, show a sheet selector (persisted widget, per CLAUDE.md) and record the sheet in `Run_Parameters`.
- **D-17 study-size warning (decided).** After mapping, show a soft `st.warning` when the study has more than 50 attributes or more than 5,000 data file rows (evaluations): "Large study: analyses may take several minutes." It never blocks. State the thresholds in README. Put the numbers in `core/config.py` as named constants.
- **FUNC-07, PrefMap example (D-05 option 1).** The shipped `Cocktail_consumer_liking.xlsx` is long format, but PrefMap's raw path needs products x consumers. Detect long format (few numeric columns, repeated product values) and say "this looks like long format; PrefMap needs one row per product and one column per consumer". Ship a wide version of the cocktail liking file as the documented PrefMap example. Accepting long format is post-release (Stage 11).
- **TEST-06, `core/data.load_precomputed_means`.** No test executes it (every AppTest monkeypatches it), and it silently accepts duplicate product rows. Add unit tests on real CSV and XLSX bytes (missing product column, duplicate products rejected, NaN report, non-numeric column) and make duplicates an error.
- **SEC-01, formula injection.** Any exported label starting with `=` is written by openpyxl as a live formula (2,175 formula cells in a test RATA export). Fix: in the final whole-workbook sweep beside `utils.export._format_p_value_cells`, turn every `data_type == 'f'` cell back into a string. The builders write no formulas of their own; confirm that first. Test: a label `=HYPERLINK(...)` round-trips as text.
- **SEC-07.** Column names are interpolated into `st.markdown` unescaped. Wrap user strings in backticks or escape them with a small helper.
- **FUNC-10.** Show the observed min/max next to the DA/RATA scale inputs, and warn when the data use less than half the declared range.
- **FUNC-12.** The bundled CATA example opens with a red error until the liking column is selected. Preselect a single non-binary numeric column named like `liking|hedonic|overall` as the upload-derived default (follow the CLAUDE.md "upload-derived defaults" rules).
- **STAT-08.** MDPREF fills missing consumer x product cells with the column mean without saying so (`modules/liking/workflow.py:3052-3056`, `:3220-3221`). Report the share imputed, and exclude consumers below a completeness threshold. The imputation itself is a statistics change, so move it into `stats/mdpref.py`.

**Files.** `core/data.py`, `core/config.py` (size thresholds), `core/upload_ui.py`, `core/upload_validation.py`, `utils/ui_shell.py` (`render_data_upload_section`), every module's Step 1 and uploader `type=` list, `modules/prefmap/workflow.py`, `modules/liking/workflow.py`, `stats/mdpref.py`, `utils/export.py`, `example_data/05_Fusion_PrefMap/` (wide liking file) and `example_data/README.md`, tests.

**Entry criteria.** Stage 2 merged.

**Exit criteria.**
- A fixture directory of bad files is added under `tests/fixtures/` (decimal comma, semicolon, tab, Latin-1, cp1252 with umlauts, `.CSV`, `.xls`, duplicated rows, multi-sheet, title row, blank IDs, formula labels). Each has a test asserting either correct values (compared against the clean file; `.CSV` and multi-sheet) or a refusal message containing the re-save instruction (everything else). None may produce a traceback.
- The size warning appears at 51 attributes and not at 50 (AppTest).
- Every exported workbook of the six bundled datasets contains zero formula cells.
- `load_precomputed_means` line coverage is above 90%.

**Effort.** M (about 2 days; D-09 option 2 removes the auto-detection work).

**Risks.** European users will be refused more often than before, although they now get a clear instruction instead of silently wrong numbers. Keep the refusal messages short and specific.

**Outcome (2026-09-28, branch `stage-3-input-integrity`; CI **green on all three jobs** on the first push (owner confirmed 2026-09-28)).** All thirteen items are implemented, each with a regression test. Every new behavioural test fails on the Stage 2 merge commit `a8e026f`; the three new unit-test files fail there at import, because the API is new.

Results:
- **Local run:** 528 passed, 1 xfailed (strict, DOC-06), 0 skipped with `FREESENSE_REQUIRE_DATA=1`; ruff clean. The warnings are the same set as at the end of Stage 2.
- **Snapshots:** all 47 files of `snapshot_replicates.py` and `snapshot_consumer.py` are byte-identical before and after (`s3before`/`s3after`). No complete-design number moved. MDPREF is not in the snapshots; `tests/test_mdpref_incomplete.py` pins that a complete matrix passes through unchanged.
- **Exit criteria:**
  - bad-file fixtures: all 16 files in `tests/fixtures/bad_files/`, 32 tests, with none producing a traceback through the real uploader. **met**
  - size warning at 51 attributes and not at 50 (AppTest). **met**
  - zero formula cells in the export of each bundled dataset. **met**, but vacuously before the fix too: no bundled file has a label starting with `=`. The real guard is `test_sheet_picker_and_formula_labels_reach_the_export` plus the bare-workbook sweep test.
  - `load_precomputed_means` line coverage above 90 %. **met**: 100 %, every statement executed (measured with `coverage` 7 from a scratch install; pytest-cov is still Stage 5's to add).

Decisions taken in this stage (the owner may revisit):
- **Missing codes.** Blank cells and exactly the strings pandas reads as NaN in a CSV (`MISSING_CODES`: `NA`, `n/a`, `NULL`, `#N/A`, …) count as blanks, so a workbook and a CSV behave alike. Anything else non-numeric blocks, including `-` and `.`. In RATA such a code is still zero-filled like a blank, as before.
- **Duplicates block in every raw module, RATA included.** RATA used to average duplicate assessor × product rows under a warning when no replicate was mapped. It now blocks, with a hint to map (or add) a replicate column. A user with genuinely repeated but unlabelled evaluations must add a session column.
- **Means tables:** a column with no number at all (a label or comment column) is kept, left out of the analysis and captioned. A column with some text cells blocks.
- **MDPREF completeness floor = 0.5** (`stats.mdpref.MIN_CONSUMER_COMPLETENESS`), so a balanced incomplete-block design where each consumer tastes half the products still contributes. Iterative-PCA imputation is not implemented (noted in the methods doc).
- **Sheet default:** the first sheet with at least two filled columns. The sheet selectbox key includes the uploaded file's id, so a new workbook starts from its own default without an extra pop in every upload handler.

Facts later stages rely on:
- **Where the upload checks live.** Uploading goes through `utils.ui_shell.load_uploaded_table` (sheet picker, refusal rendering, sheet record) and the checks in `core/upload_validation.py`. CLAUDE.md now documents both, including the check order: IDs, then duplicates, then text cells, before anything counts observations per cell. `md_code` lives in `core.upload_validation` and is re-exported by `utils.ui_shell`.
- **Stage 5.** `tests/test_apptest_stage3_inputs.py::capture_exports` patches `st.download_button` and runs each module's deferred builder, **in the script thread**. The bundled-dataset walk uses it. B05 item 8 still needs the worker-thread variant. The real-upload AppTests in `test_bad_file_fixtures.py` and `test_apptest_bundled_datasets.py` (`at.file_uploader(key=…).set_value((name, bytes, mime))`) are the pattern for item 7. TEST-06 stays open for the untested paths other than the loader (see `docs/open-items.md`).
- **Stage 6 (IO-06, CODE-02).** `Run_Parameters` has a new `data_source_sheet[.<role>]` row read from `<prefix>_source_sheets`. The recorded file name still comes from the global `uploaded_file` key (CODE-02, unchanged). Liking has new `mdpref_*` rows. `_finalise_workbook` is the single last-act sweep; add any new whole-workbook pass there.
- **Stage 7 (docs).** README "Data Format" now states the formats, the text-cell and duplicate rules and the D-17 thresholds. `example_data/README.md` documents the wide cocktail file. `Statistical_Methods_README.md` §28 has an "Incomplete designs" paragraph. The About page and any other copy still mentioning `.xls` should be checked (none found by grep in `modules/` or `utils/`).
- **Stage 8 (SEC-07 remainder).** Only the five register sites and the Step 1 upload messages use `md_code`. Result-page captions that interpolate product, attribute or cluster names are the same class and are left for Stage 8's copy pass. The row stays open in `docs/open-items.md`.
- **Surprises worth knowing:**
  - Streamlit's `file_uploader` itself rejects a `.xls` when `type` omits it (AppTest shows `Invalid file extension`), and accepts `.CSV` for `type=["csv"]` (verified in AppTest, not in a browser).
  - `load_data` turned numeric column headers into NaN (`Index.str.strip()` on mixed labels), so a wide liking file with consumer IDs `1…100` as headers could not have worked. Headers are now `str`.
  - A workbook written by pandas/openpyxl with a string starting with `=` holds a formula with no cached value, which reads back as a blank. A file exported that way therefore meets the IO-01 blank-ID block, not a silent phantom. A file saved by Excel carries cached values and is unaffected.

- **Status: Stage 3 COMPLETE (2026-09-28).** Next: merge `stage-3-input-integrity` into `main`, then start Stage 4 on `stage-4-stat-methods`.

---

## Stage 4: Statistical method fixes — COMPLETE 2026-09-28

**Goal.** Every p-value, df and ★ marker the app shows is one a statistician would accept, and the two views of the same comparison (CLD letters and contrast) always agree.

**Findings.** STAT-01, STAT-02, STAT-03, STAT-04, CODE-03 (with STAT-07), CODE-04, CODE-01 (with STAT-12), STAT-09, STAT-11, UI-07, DOC-03 (with STAT-10).

**Brief.**
- **STAT-01, `stats/segmentation.py:57-93` (`_cluster_anova`).** It tests liking differences between clusters that were built from the same liking scores, and marks them ★. On pure noise it flags about 4 of 6 products every time; about 0.3 would be expected. Per D-07 (decided: descriptive only), drop the p-values and ★ and show effect sizes (range, eta²) labelled descriptive, in the UI and the export. Test: 20 seeded noise datasets produce no ★.
- **STAT-02, `stats/liking.py:289-290` and `stats/contrast.py:292-312`.** The Liking contrast uses `df = max(1, n_c - n_p)`, labelled "Satterthwaite", and the CLD uses a per-pair Welch df. For a complete design, the correct df for a product difference is the RCBD error df `(n_c - 1)(n_p - 1)` (45 at 10 x 6, against 4 and about 18). At 7 x 6 the df floors at 1 and Hedges' g becomes 0. Per D-07 (decided: option 1), use one df for CLD and contrast: the RCBD error df for complete data. For incomplete data, flag it and use the containment df from an OLS RCBD fit until Satterthwaite or Kenward-Roger is implemented. Test: contrast and CLD decisions agree on every pair for hedochoc and for a 10 x 6 synthetic set, and Hedges' g is non-zero at 7 x 6.
- **STAT-03, `stats/contrast.py:447-491` against `stats/posthoc.py` `_rcbd_tukey_decisions`.** The RATA "Tukey" contrast uses per-pair paired SEs with a studentized-range quantile; the RATA Tukey CLD uses the pooled assessor-blocked residual MS. On sensochoc they disagree on 16 of 420 pairs, in both directions. Per D-08 (decided: pooled blocked term), make the contrast call the CLD's error MS and df. Add a parametrised test asserting contrast-vs-CLD agreement for every module x post-hoc method (DA and RATA FDR/LSD already agree; keep them pinned).
- **STAT-04, `stats/pls.py:325-331` (Fusion ships as beta per D-06, so this is in scope).** The in-fold scaling guard `x_sd > 0` passes an SD of about 6e-17 for a predictor that is non-zero in one product, and scales it by about 1e16. Q² then falls to between -14.5 and -2.5, where an independent LOO gives 0.53 to 0.89, with no warning. Fix: a relative tolerance (for example `x_sd > 1e-8 * max(1, global_sd)`), or drop constant-in-fold columns from that fold. The permutation test and bootstrap reuse the function, so test all three with a one-product indicator column.
- **CODE-03, `stats/liking.py:227-253`.** The Liking LMM ignores warnings and never checks `.converged`, so a boundary or non-converged fit is reported as fine. Record warnings with `catch_warnings(record=True)`, and set the flag from `.converged` or a recorded `ConvergenceWarning`. Return the optimiser used and a boundary-fit flag, and surface them in the UI and export.
- **CODE-04.** `stats/` warnings reach only the terminal. Rule: anything the user must know goes into the result dict. Concretely, the Fusion permutation caption and export show `n_finite_permutations` of `n_permutations`.
- **CODE-01, `utils/plotting.py:1219`, `:1267`.** Liking's Tukey label is not recognised, so an HSD ribbon is captioned "±LSD zone". Define the Tukey labels once in `core/config.py` (`is_tukey(method)`), replace the nine tuples, and test `plot_spider_with_ribbon` with every module's option list.
- **STAT-09, `stats/posthoc.py`.** The Tukey fallback to uncorrected paired t is called "conservative". Apply Holm and say so. Stop rounding MS/SS to 4 dp in the result frame (display rounding only).
- **STAT-11.** The Kendall's W caption says ties are not corrected, but the code corrects them. Fix the caption.
- **UI-07, `modules/descriptive/workflow.py:1233-1238`.** The DA discrimination heatmap is empty without replicates and always uses α = 0.05. Pass `st.session_state['da_alpha']`, and plot the range score (or hide the chart with a reason) when there are no replicates.
- **DOC-03.** The `run_da_anova` docstring says the interaction pre-test alpha does not affect product p-values. It does, by selecting the error term. Fix the docstring here (the methods doc is Stage 7).

**Files.** `stats/segmentation.py`, `stats/liking.py`, `stats/contrast.py`, `stats/posthoc.py`, `stats/pls.py`, `stats/da_anova.py` (docstring), `core/config.py`, `utils/plotting.py`, `utils/export.py`, `modules/liking/{ui,workflow}.py`, `modules/rata/ui.py`, `modules/descriptive/workflow.py`, `modules/fusion/workflow.py`, tests; `validation/` emitters where a pinned quantity changes.

**Entry criteria.** Stage 2 merged (D-06, D-07 and D-08 are decided).

**Exit criteria.**
- For every module and post-hoc method, a test asserts that CLD letters and contrast decisions agree on every pair of every bundled dataset.
- The noise simulation for STAT-01 shows no ★.
- STAT-04: Q² within 1e-6 of an independent LOO (NumPy re-implementation or `sklearn.cross_val_predict` with in-fold scaling) on the indicator-column case.
- `validation/README.md` and the Stage 1 pins are updated wherever a number changes, with a one-line reason per change in `CHANGELOG.md` (these are corrections; users of earlier builds need to know).
- `method-auditor` agent sign-off on the diff of `stats/`.

**Effort.** M to L (3 to 5 days, mostly STAT-02).

**Risks.** STAT-02 changes published Liking numbers for small panels. Check whether any existing test pinned the old df and update it deliberately. Kenward-Roger is out of scope for this release; the incomplete-design case must be flagged, not guessed.

**Outcome (2026-09-28, branch `stage-4-stat-methods`; CI **green on all three jobs** (owner confirmed 2026-09-28). The first push took 28 minutes because of slow new tests, fixed before merge (below); the second took 8 minutes.)** All eleven findings are fixed (STAT-01, STAT-02, STAT-03, STAT-04, CODE-03 with STAT-07, CODE-04, CODE-01 with STAT-12, STAT-09, STAT-11, UI-07, and the docstring part of DOC-03 with STAT-10), each with a regression test. Every behavioural test was checked against the Stage 3 merge commit `b4d537b` (a worktree with the new test files copied in). Every one fails there, with two expected exceptions:
- the DA (all three methods) and RATA FDR/LSD agreement tests pass on `b4d537b`, because those views already agreed; the brief says to keep them pinned;
- the unit test of the heatmap α passes there too, because the plot function already took `alpha` and the bug was at the call site. Two DA AppTests go through the app, and both fail on `b4d537b`.

Results:
- **Local run:** 624 passed, 1 xfailed (strict, DOC-06), 0 skipped with `FREESENSE_REQUIRE_DATA=1`; ruff clean. The same result on a clean `git worktree` of HEAD (Stage 2 lesson), before the audit follow-up commit.
- **Snapshots (`s4before`/`s4after`):** every CLD, pairwise table, LS mean, LMM summary, RATA/DA summary and panel-performance file is byte-identical. What changed:
  - `da_anova_full.csv`: SS/MS are now unrounded (max change 4.8e-5, the old 4-dp rounding); F and p are identical.
  - `liking_lmm_scalars.csv`: the df column (216 → 1105) and the new keys.
  - The four `liking_*_anova.csv` files are replaced by `liking_*_separation.csv` (STAT-01).
- **Measured, not taken from the register:** 16 of the 420 RATA Tukey contrast rows on significant sensochoc attributes change decision (10 lose significance, 6 gain it), and all now match the letters. The Fusion validation emitter's outputs are byte-identical before and after STAT-04.
- **Exit criteria:**
  - CLD letters and contrast decisions agree on every pair, for every module × post-hoc method, on every bundled dataset: **met**. See `tests/test_cld_contrast_agreement.py`: DA and RATA on sensochoc (3 methods each), Liking on hedochoc and the JAR file (3 methods), ten 10 × 6 synthetic Liking panels, and the Holm fallback in both a trivial and a real (DA) case. CATA is deliberately out of scope: its contrast and McNemar CLD use different correction families by design (CLAUDE.md).
  - No ★ in the STAT-01 noise simulation: **met**. 20 seeds × {AHC, k-means} × {raw, standardised}; the result has no inferential column and the chart has no marker.
  - STAT-04 Q² within 1e-6 of an independent LOO on the indicator-column case: **met** for 20 seeds, and for the permutation test and the bootstrap CI driven by the same draws.
  - `validation/README.md` and the Stage 1 pins updated where a number changes, with a CHANGELOG reason per change: **met**. No frozen reference moved; the README records why for each quantity. The deliberately updated pins are `test_R15` (df 17 → 38), the two SS/MS pins that asserted 4-dp rounding, and the cluster-caption AppTest.
  - `method-auditor` sign-off on the `stats/` diff: **met with conditions, and the conditions are done**. The audit found no critical defect and set four conditions, all fixed in the audit follow-up commit:
    - (a) a stale Hedges' g docstring;
    - (b) blank the CI on Holm-fallback contrast rows, plus a non-trivial DA fallback agreement test;
    - (c) apply the converged check to the LRT null model;
    - (d) soften the "almost every product" copy and say eta² is inflated by selection.

    The audit's other minors (purely relative PLS tolerance, boundary threshold 1e-4, keeping warnings from failed optimisers, a note on the boundary df) are also in that commit. The one pre-existing minor (the DA contrast uses k = all products while the CLD uses the attribute's products) is new backlog row **STAT-14** (LOW, Stage 11) in `docs/open-items.md`.

Decisions taken in this stage (the owner may revisit):
- **One Liking df, computed as the residual df of the OLS block model on consumer × product means.** This is exactly (n_c − 1)(n_p − 1) on complete data. On incomplete data it becomes the containment df, which is flagged, as the brief says. It is renamed `df_pairwise` (was `df_satterthwaite`); `df_pairwise_method` is `rcbd_complete` or `containment_incomplete`.
- **The Tukey fallback is Holm, in both views, over the attribute's full pair family.** Holm-fallback contrast rows carry `p_value_holm` and no CI or ribbon width, because a step-down decision has no single interval.
- **LMM optimiser rule:** take the first optimiser whose REML and ML fits both converge; otherwise keep the first usable fit and flag it. The same rule applies to the LRT null model.
- **Segment separation:** range of segment means plus eta², and the highest and lowest segments. The `alpha` argument of the clustering functions is still recorded but no longer used.

Facts later stages rely on:
- **Result shapes that changed.** The CHANGELOG "Stage 4 result-shape changes" entry lists each:
  - `df_satterthwaite` → `df_pairwise` (+ `df_pairwise_method`);
  - `cluster_anova` → `cluster_separation`;
  - new LMM keys `optimiser_used`, `boundary_fit` and `model_warnings`;
  - `posthoc.rcbd_error_term` and `posthoc.tukey_fallback_message`;
  - `core.config.is_tukey`;
  - `generate_cld` `attrs`;
  - contrast `tested_against` values `rcbd_blocked`, `lmm_rcbd_df` and `paired_ttest_holm`.
- **Stage 5.** The displayed-numbers AppTests should read the new Step 2 df caption, and the segment-separation table has no p-value column to pin. `tests/test_cld_contrast_agreement.py` calls the stats layer directly, not through the app, so it counts towards TEST-02 but not towards B05 item 7.
- **Stage 6 (IO-08, DOC-02).** Rounding still left in results:
  - `run_da_anova` still rounds `F` in `full_df` (4 dp), and `F_*`/`eta2p_product` in the summary (3 dp);
  - `ms_products`/`ms_error` are rounded to 6 dp (these feed the ICC; the Stage 2 tie flips live here);
  - Liking `anova_table.LRT_statistic` is rounded to 4 dp.

  New `Run_Parameters` rows (`pairwise_df`, `pairwise_df_method`, `lmm_optimiser`, `lmm_convergence_warning`, `lmm_boundary_fit`, `lmm_warnings`) and the Fusion row "Permutations with a defined Q²" are what DOC-02's "how to report this analysis" text should cite.
- **Stage 7 (DOC-01, DOC-03).** `Statistical_Methods_README.md` is now further out of date. It still describes:
  - the Liking df as n_c − n_p, and the per-pair Welch df;
  - the cluster ANOVA with ★ (around l.1610);
  - the uncorrected "conservative" Tukey fallback;
  - the RATA Tukey contrast's paired SE;
  - the interaction-alpha sentence (l.728).

  The docstrings of `stats/liking.py`, `stats/contrast.py` and `stats/segmentation.py` hold the corrected text. The Liking post-hoc help text in `modules/liking/workflow.py` was corrected here, because it described the df being changed.
- **Stage 8 (SEC-07).** `posthoc.tukey_fallback_message` and the DA "No residuals for" caption wrap names in backticks / `md_code`.
- **Stage 11.**
  - Kenward-Roger / Satterthwaite for incomplete Liking designs is a new LOW row, STAT-02 (remainder).
  - CODE-04 remainder: `data_fusion.autoscale` and `project_supplementary` warnings are still terminal-only.
  - The two scipy `studentized_range` version probes in the DA/RATA contrast steps (CODE-08) now sit behind `is_tukey`; they are still dead code.
- **Surprises worth knowing:**
  - **L-BFGS REML raises `LinAlgError: Singular matrix` on the bundled hedochoc file**, and on the balanced acceptance fixture. The Liking fit has always fallen back to CG there, silently. The app now says so in a Step 2 note on every hedochoc run. That is honest, but the owner may find it noisy on the flagship example. The alternative is to make CG the default optimiser, which changes no number on hedochoc, because CG is what already runs. Owner's call.
  - **statsmodels' boundary warning is the reliable boundary signal.** On the register's boundary case the estimated consumer variance was 3e-8 of the residual, not 0.
  - A pure-insertion hunk staged with `git apply --cached --unidiff-zero` landed at the wrong line and produced an unparseable file in a local commit. It was caught before any push and the commits were rebuilt. If a later stage splits mixed-file commits, apply hunks by their old-side line numbers onto `git show :file` and write the result with `git update-index`. Then parse every staged `.py` file before committing.

- **Test runtime regression, found by the owner after the first push (CI 28 min, previously 5–6 min).** Locally, measured with `--durations=0` and `-n auto` on 8 cores, the suite went from 243 s on `main` to 860 s on the branch. There was no Git or app cause. Three new tests accounted for about 1,240 of the ~1,425 extra test-seconds:
  - the DA Holm-fallback agreement test, 723 s. It re-ran the full pipeline for 6 references × 14 attributes, once per attribute it broke;
  - the STAT-01 noise simulation with k-means, 280 + 235 s: 20 seeds × a k = 2…8 sweep with 50 initialisations.

  Fixes:
  - the Holm test now covers three fixed attributes, with the ANOVA frame cut to the attribute under test;
  - k-means runs 2 seeds (AHC keeps the 20 the exit criterion names);
  - `compute_contrast` computes each studentized-range critical value once per (df, method, k) instead of once per comparison. This makes a RATA Tukey contrast 0.15 s instead of 4.4 s (3.6 s on `main`). All 2,520 sensochoc DA/RATA contrast rows are bit-identical to before.

  Result: 626 passed, 1 xfailed in **205 s** locally, faster than `main`. CI now prints `--durations=15`. Stage 5's brief has a runtime budget.
- **Superseded after Stage 8 (2026-10, `working_notes/contrast-fix.md`, decision D-C3).** The exit criterion "CLD letters and contrast decisions agree on every pair for every method" no longer holds, on purpose. Letters and contrast still share one error term and df per module, but the contrast is now many-to-one (k − 1 comparisons with the reference): Tukey → Dunnett, FDR → BH over k − 1. Only the unadjusted methods still agree row by row (`tests/test_cld_contrast_agreement.py`), and the page says a borderline pair can differ. STAT-14 closed with that change.
- **Status: Stage 4 COMPLETE (2026-09-28), CI green on all three jobs in 8 minutes.** Next: merge `stage-4-stat-methods` into `main`, then start Stage 5 on `stage-5-release-tests`.

---

## Stage 5: Remaining release-floor tests — COMPLETE 2026-09-29

**Goal.** Close the release-floor items of the minimum test set that Stages 1 to 4 have not already delivered.

**Findings.** TEST-02 (remainder), TEST-07.

**Brief.**
- **End-to-end upload per module (B05 item 7).** One AppTest per module that does not monkeypatch `load_data`: real file bytes through the uploader, automatic mapping, Run, `analysis_complete`, every step rendered. B02 wrote such a harness during the review (`working_notes/repro/B02/harness.py`); reuse the approach, not the file.
- **Deferred download callable (item 8).** For each module, call the exact lambda passed to `render_export_section` on a worker thread with no script context. The workbook must open, its sheet list must match the builder's list, and the `Run_Parameters` alpha and scale must equal the widget values.
- **Gated panels (item 12).** Open every `on_change="rerun"` tab and expander in Liking Steps 4, 5 and 7, DA/RATA with varimax on, and Fusion log/sqrt transforms, and assert that no exception is raised.
- **Displayed numbers.** For each module, one AppTest asserts that at least one number rendered on screen (a metric or table cell) equals the stats-layer value.

**Files.** `tests/test_apptest_*.py`, `tests/conftest.py`, `requirements-dev.txt` and `requirements/dev-lock-py3.*.txt` (add `pytest-cov`, which the coverage exit criterion needs and Stage 1 did not install), `.github/workflows/ci.yml` (coverage report).

**Entry criteria.** Stages 2 to 4 merged (so the tests pin corrected behaviour).

**Exit criteria.** Items 1 to 8 of the B05 minimum test set exist and pass in CI. Line coverage (pytest-cov) is at least 80% overall, and no `stats/` file is below 70% (today `stats/mdpref.py` is 12% and `stats/data_fusion.py` 64%).

**Effort.** M (2 days).

**Risks.** AppTest file-uploader injection may need a helper. Keep it in `tests/conftest.py`.

**Runtime budget (added after Stage 4).** The Stage 4 push took CI from 5–6 minutes to 28 minutes. Locally the suite went from 243 s to 860 s; three new tests caused almost all of it, and they were fixed in `stage-4-stat-methods` before merge (see the Stage 4 outcome). Stage 5 adds end-to-end AppTests, which are the expensive kind, so:
- Measure the full suite's wall time before and after the stage (`/usr/bin/time … pytest tests/ -n auto`), against the Stage 4 figure recorded in its outcome. Keep the increase under about 1 minute locally.
- No single new test may take more than about 60 s. With `-n auto`, one long test blocks a worker, and on the 3-core macOS runner it sets the wall time. CI now prints `--durations=15`, so read that list on every run.
- Cover a property with the fewest cases that exercise it: one dataset per module for end-to-end runs, and seeds only where randomness is what the test is about.

**Outcome (2026-09-29, branch `stage-5-release-tests`; CI **green on all three jobs** on the first push, including the coverage-floor step and the single-thread BLAS setting (owner confirmed 2026-09-29)).** Items 7, 8 and 12 of the B05 minimum test set, the displayed-number checks and the coverage gate are in place. Items 1–6 and 9–13 were already delivered by Stages 1–4. Along the way, the new tests found and fixed one statistical defect (STAT-15) and one wrong piece of copy (the RATA export sheet count). They also showed that the old export capture could not catch the failure item 8 is about. Commits `a14adbf`…`876021c` (13 on top of `41d569f`).

Results, on a clean `git worktree` of `277c225` (the last test-changing commit):
- **Suite:** 661 passed, 1 xfailed (strict, DOC-06), 0 skipped with `FREESENSE_REQUIRE_DATA=1`; ruff clean.
- **Runtime:** 213.8 s wall with coverage and default BLAS threads, against 188.3 s at the branch point without coverage, so +26 s (budget: about +60 s). With one BLAS thread per worker, now set in CI (below), the same suite took 77 s.
- **Snapshots:** `s5before`/`s5after` (`snapshot_replicates.py` + `snapshot_consumer.py`, 47 files) are byte-identical. STAT-15 only changes the demographic permutation path, which no snapshot covers.
- **Exit criteria:**
  - B05 items 1–8 exist and pass in CI: **met**.
    - 1: CI (Stage 1).
    - 2–5: Stage 1 known answers.
    - 6: `load_precomputed_means`, Stage 3.
    - 7 and 8: `tests/test_apptest_bundled_datasets.py`, all six modules, with the worker-thread export via `tests/conftest.py::capture_exports`.
    - Item 12 (not a floor item, but in this brief) is in the same file.
  - Line coverage ≥ 80 % overall and no `stats/` file below 70 %: **met** (locally and in CI). 86.9 % overall, and the lowest `stats/` file is `posthoc.py` at 84.2 %. At the branch point it was 79.6 %, with `data_fusion` at 63.8 % and `segmentation` at 67.3 %; `mdpref` had already reached 74.0 % in Stage 3 (the brief's 12 % is the register's figure). `scripts/check_coverage.py` enforces both floors in CI.
  - Runtime budget: wall **met** (+26 s). The per-test guideline of about 60 s was **not met under default BLAS threading** (`test_sensochoc_descriptive` took 81 s under full load, 9 s of its own work). It **is met with the CI thread setting** (23 s), and no pin moved on any CI runner with one BLAS thread.

Decisions taken in this stage (the owner may revisit):
- **"Automatic mapping" in B05 item 7 does not exist in the app.** No module guesses the ID columns: the mapping boxes open on "Select…" unless the last run's `col_map` is the default. The tests assert that placeholder, set the mapping as a user does, and then assert what the app does derive automatically: the attribute set, CATA's liking preselect (FUNC-12), Liking's scale suggestion (U2), the JAR detection path and the sheet choice. An ID auto-mapper would be a product feature; it is not added here.
- **Sheet lists are checked against what each page advertises**, not against a list copied into the test:
  - DA/RATA: the `- **Name** —` bullets;
  - Liking: the "Your export will contain N sheets" caption;
  - CATA: `get_cata_export_sheet_list`;
  - PrefMap: the "has N sheets" caption.

  Fusion's page advertises no list, so its test checks only that `Run_Parameters` exists.
- **STAT-15 fixed in-stage** (like FUNC-13 and STAT-13 before it): it is a wrong p-value on screen, found by a new test, and the fix is small.
- **Dead code deleted in-stage** (TEST-06 assigned it to Stage 5): the three functions the register named, and four stale duplicate plotters in `utils/plotting.py`.
- **TEST-02 stays open, re-staged to "11 (owner to confirm)".** Every method on the register's list is now executed by a test, but nine still have no independent reference (listed in `docs/open-items.md`). None is on the release floor; since it is a HIGH row, whether it blocks 1.0.0 is the owner's decision.
- **CI runs with `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.** This is a test-environment choice: all tests pass both ways locally. If a pin moves on a CI runner because of it, treat it as a numerical defect (STAT-13 rule); do not revert to hide it.

Facts later stages rely on:
- **Test helpers (`tests/conftest.py`).**
  - `upload_file(at, key, path | name+data)` injects real bytes.
  - `run_deferred_download(fn)` runs a download callable as the server does.
  - `capture_exports` builds every `*_export_download` workbook through it. It used to run the builder in the script thread (the old `test_apptest_stage3_inputs.capture_exports`, now removed), where a builder that read `st.session_state` passed; `tests/test_deferred_download.py` proves the difference.
  - `open_every_gated_panel(at, skip=…)` finds stateful panels from the element tree. It opens each one, and each panel nested inside, re-applying the whole path every run, because AppTest keeps no tab state between runs.
  - CLAUDE.md documents all four.
- **Stage 6 (IO-06, CODE-02, IO-08, DOC-02).**
  - The IO-06 exit test ("every builder's `Run_Parameters` has `exported_at`, versions, SHA-256, own file name") belongs in `tests/test_apptest_bundled_datasets.py`: each module's workbook is already built there on the worker thread, and `_run_parameters(wb)` returns the rows. This is also where a builder that reads `st.session_state` for the new rows will fail, as it should.
  - The CODE-02 AppTest (switch modules, export, never another module's file) can use `upload_file` and `capture_exports` directly.
  - IO-08 removes stats-layer rounding. The displayed-number checks compare the rendered frame with a direct stats call at `atol=0`, and both sides change together, so they should not need editing.
  - DOC-02 adds `Methods_Notes` to DA and Liking. The test compares each workbook with the page's own list, so every new sheet must also be added to:
    - DA: the `- **Name** —` bullets;
    - Liking: `get_liking_export_sheet_list`;
    - CATA: `get_cata_export_sheet_list`;
    - PrefMap: the `_n_sheets` count in `modules/prefmap/workflow.py`.
  - Fusion has no advertised list; DOC-04's "generate sheet lists from the builders" (Stage 7) would be the clean fix for all six.
- **Stage 7 (DOC-06, DOC-01, DOC-04).**
  - When the numerically coded JAR example ships:
    - remove the strict xfail;
    - add the Step 6 JAR tabs (`liking_render_step_6_tabs`) to `test_liking_examples`: select the JAR columns so the walk opens them, and assert they are in the opened set;
    - update the TEST-02 row's JAR entries.
  - B05's "Liking Steps 4, 5 and 7" uses the old step numbering. Today the gated panels are on Steps 2, 3, 4, 5 and 6, and Step 7 needs its "Run preference map" button, which the test presses.
  - `Statistical_Methods_README.md`, demographic association section: state that the permutation p-value counts ties with R's `chisq.test` tolerance (STAT-15), and that Cramér's V for a 2 × 2 table uses the Yates-corrected chi² (as scipy and R report it; pinned in `tests/test_known_answers_demographics.py`).
  - README sheet lists (DOC-04) should match the now-tested in-app lists.
- **Stage 8 (copy).** Rewording an export step's sheet list must keep the formats above, or the end-to-end test fails.
- **Stage 11 / backlog.**
  - CODE-04 row: an extra item. When every Liking LMM optimiser raises, the exception text is discarded and `model_warnings` is empty; the shape is pinned by `test_every_optimiser_failing_returns_an_empty_result_not_a_crash`.
  - Module (not `stats/`) coverage is lowest in PrefMap: `modules/prefmap/ui.py` 43.7 %, `workflow.py` 67.5 %. The KDE density contour needs clusters, which the uploaded-liking path has no source for, so `compute_kde_contour_points` is only exercised through Liking's MDPREF view.
- **Surprises worth knowing:**
  - The old export capture ran builders in the script thread, so B05 item 8's risk was untested even where exports were "tested".
  - Four Liking plotters existed twice. The copies in `utils/plotting.py` were dead and had drifted 88–199 lines from the live ones in `modules/liking/ui.py`, so the register's "never executed" finding was about the dead copies, while the live ones were partly executed all along. Grep for duplicate `def` names before trusting a coverage report by function name.
  - The per-test durations CI prints under `-n auto` were inflated up to 9× by BLAS oversubscription, not by the tests themselves. Read `--durations` together with the thread setting.
  - STAT-15 surfaced only when the permutation test was recomputed with a float64 reference on small designs, where ties are common. A seeded known-answer test on a strong association (no ties) passed on the buggy code.
  - `pd.DataFrame({'a': s1, 'b': s2})` sorts the union index, so `compute_demographic_association` permutes in sorted-ID order. Any external replication of its draws must sort the IDs the same way.

- **Status: Stage 5 COMPLETE (2026-09-29), CI green on all three jobs.** Next: merge `stage-5-release-tests` into `main`, then start Stage 6 on `stage-6-exports-version`.


---

## Stage 6: Reproducible exports and version identity — COMPLETE 2026-09-29

**Goal.** An exported workbook identifies exactly what produced it and can be re-analysed at full precision.

**Findings.** IO-06, REL-05 (with DOC-09), CODE-02 (with IO-07), IO-08, DOC-02, IO-09, IO-12, UI-13.

(Stage 2 note: `compute_repeatability` still rounds `ICC`, `ICC_lower` and `ICC_upper` to 3 dp; remove it with the rest of IO-08. Doing so also removes the two tie flips recorded in the Stage 2 outcome.)

**Brief.**
- **REL-05 / D-01 (decided: option 1).** Keep the version single-sourced in `core/__version__.py`. Builds given to testers are `1.0.0rc1`, `1.0.0rc2` and so on, and the public release is `1.0.0` (see Stage 9, "Versioning during testing"). Set `1.0.0rc1` at the end of this stage. Delete the unpushed local `v1.0.0` tag (`git tag -d v1.0.0`; confirm with the owner at the time, as it is irreversible locally). Candidate tags (`v1.0.0rcN`) and the final `v1.0.0` tag are created in the new release repository in Stage 9. Collapse the three CHANGELOG headings into one release entry. Write the version policy into `CLAUDE.md`: every `stats/` change bumps at least the patch version.
- **IO-06, `utils/export.build_run_parameters_sheet`.** Add rows for:
  - `exported_at` (ISO 8601 with time zone)
  - Python version
  - versions of streamlit, pandas, numpy, scipy, statsmodels, scikit-learn, pingouin and plotly (via `importlib.metadata`)
  - the git commit, when available
  - the input file name, SHA-256, sheet, and rows x columns read
  - the RATA/DA bootstrap count and seed

  Capture everything in the script thread and bind it into the deferred callable (the builders run with no script context; see CLAUDE.md).
- **CODE-02.** A global `uploaded_file` key leaks between modules, so Fusion and PrefMap exports name another module's file. Each module records its own `<prefix>_df_raw_name` storage key (listed in `MODULE_STATE_KEYS`) at Run time, as Liking does. The builder stops reading the global.
- **IO-08 / D-18.** Store full precision everywhere and use Excel `number_format` for display, as p-values already do. Write rates as numbers with a `0.0%` format. Stop rounding F, LR and ICC in the stats layer (`stats/mixed_models.py:119`, `stats/da_anova.py:419-449`, and `stats/panel_performance.py`, where F, r and RV are rounded to 3 dp). Then tighten the corresponding pins from Stage 1:
  - `tests/test_validation_pins.py`: DA `F_product` and ICC (currently 1e-3), and RATA `lr_stat` (currently 1e-3).
  - `tests/test_stage_f_smoke.py`: the per-attribute `RATA_LR_PIN` and `DA_F_PIN` dicts hold 3-dp values. Re-record them at full precision.
  - `tests/test_known_answers_da.py`, `tests/test_known_answers_rata.py` and `tests/test_unbalanced_designs.py::test_anova_with_empty_cells_uses_the_additive_model` (STAT-13) assert **equality with the rounded reference** (`== round(ref, 3)` for F, r and `lr_stat`; `== round(ms, 4)` for `full_df` MS). These fail by design once the rounding goes. Switch them to `abs(... - ref) < 1e-10` (the LRT to about 1e-8, since it compares two optimisers).
- **DOC-02 / D-19 (decided: option 3 now).** Every export gets a `Methods_Notes` sheet, auto-filled from the run with a ready-to-paste "How to report this analysis" paragraph. The same text is shown in-app in a collapsed expander on each module's Results and export step. It covers the model, SS type or estimation method, the error term actually used, the post-hoc method and correction family, alpha, software and version, and the method citations. Liking and DA lack it today.
- **IO-09.** The Word and PowerPoint image presets render text at 3 to 6 pt at page size. Author the presets at physical page width, or scale fonts with a minimum of 8 pt equivalent. Stay consistent with CLAUDE.md's "export never inflates fonts" rule; revise that rule explicitly if needed.
- **IO-12.** The modebar download uses the figure's own size, and file names include the module, chart and dataset stem.
- **UI-13.** Build product colour maps at render time so a palette change applies everywhere without a re-run.

**Files.** `core/__version__.py`, `CHANGELOG.md`, `CLAUDE.md`, `utils/export.py`, `utils/plot_theme.py`, `core/config.py`, `core/state.py` (new storage keys), module Step 1 handlers, `stats/mixed_models.py`, `stats/da_anova.py`, tests.

**Entry criteria.** Stage 4 merged (methods notes must describe the corrected methods).

**Exit criteria.**
- A test for every builder asserts that `Run_Parameters` contains `exported_at`, the package versions, the input SHA-256 and the module's own file name, and that no numeric result column is stored as text. (Stage 5 note: extend `tests/test_apptest_bundled_datasets.py`, which already builds each module's workbook on the worker thread; see the Stage 5 outcome for the sheet-list formats a new `Methods_Notes` sheet must follow.)
- Switching modules and exporting never shows another module's file (AppTest).
- The version appears identically in the About page, sidebar, exports, README, methods document and CHANGELOG.

**Effort.** M (2 days).

**Risks.** Removing stats-layer rounding changes pinned values in the last digits. Update the pins in the same commit and say so in the CHANGELOG.

**Outcome (2026-09-29, branch `stage-6-exports-version` on `1ca0727`; CI **green on all three jobs** (owner confirmed 2026-09-29)).** Every Stage 6 finding is fixed. The local `v1.0.0` tag was deleted with the owner's go-ahead (it was never on the remote).

Results on the branch:
- **Suite:** 697 passed, 1 xfailed (strict, DOC-06), 0 skipped with `FREESENSE_REQUIRE_DATA=1` and one BLAS thread; ruff clean. 75.9 s wall, against 92.7 s at the branch point (same settings), so the runtime budget is met. Coverage 87.2 %; lowest `stats/` file `posthoc.py` at 84.2 %.
- **Snapshots** (`s6before`/`s6after`, 47 files): 30 identical. Changes are only the de-rounded columns, moving in the 4th–7th decimal (DA F/η²p/ICC/r/RV/scale metrics, RATA `lr_stat`, pairwise `Mean Diff`). The exceptions are the within-panel percentile `score` columns of the DA performance frames, which move by up to 5.6 points, and `da_perf_rv` row order, because 3-dp rounding had created ties. No p-value, CLD, flag count or significance call in the snapshots changed.
- **Exit criteria:**
  - Every builder's `Run_Parameters` has `exported_at`, package versions, input SHA-256 and the module's own file name, and no numeric result is stored as text: **met**. Checked for all six modules in `tests/test_apptest_bundled_datasets.py` (`_assert_provenance`, `numbers_stored_as_text`), plus DA F full precision and `0.000` format, and RATA rates as `0.0%` numbers.
  - Switching modules and exporting never shows another module's file (AppTest): **met**. `tests/test_export_provenance.py::test_module_round_trip_keeps_each_modules_own_file` covers CATA → DA upload → CATA export, and a unit test per module covers the register's foreign-`uploaded_file` state.
  - Version identical in About, sidebar, exports, README, methods doc and CHANGELOG: **met** (`tests/test_version_identity.py`, plus `freesense_version` in every bundled export).

Decisions taken in this stage (the owner may revisit):
- **Upload records are written when the uploader is read, not at Run** (CODE-02 brief said "at Run time, as Liking does"). `load_uploaded_table(record=(prefix, role))` already runs for every upload in every module, including companion, demographics and external files. Every uploader's `on_change` resets the analysis, so the record always describes the data the results came from. `<prefix>_source_files` is deliberately **not** in `MODULE_STATE_KEYS`: Liking, Fusion and PrefMap keep the uploaded frame across a parameter reset, and the record must live as long as the frame. The builder prunes roles the run did not use: a CATA companion file only when `liking_mode` is companion, Fusion/PrefMap uploads only when their source is `uploaded`. When the input came from DA/RATA/Liking results, the upstream file is reported as `<role>.upstream`. `<prefix>_source_sheets` is folded into the same record.
- **pingouin is not in the package list** (the brief lists it; D-04 removed it). openpyxl is added, because it writes the workbook.
- **"Full precision" = 16 significant digits**, which is what openpyxl writes. Excel holds 15. The last binary digit of a double does not survive the workbook, and the test says so.
- **Number formats are one whole-workbook sweep** (`_format_number_cells`), not per-column maps: `0.000`, `0.00E+00` below 1e-3, `0` for whole-number floats, `0.0%` for rate columns and sheets. `Raw_Data` is left unformatted. PLS outputs previously rounded to 4 dp now display at 3.
- **IO-08's header-label half** (snake_case vs humanised headers) is **not done**. It is re-staged as a LOW row for Stage 8 in `docs/open-items.md`: renaming headers changes what the p-value and percent sweeps match on and what users' spreadsheets reference, so it should be done once, deliberately.
- **IO-09:** the brief allowed either narrower authoring widths or a font floor; both are applied. Word 960 px → 6.5 in, landscape 1300 px → 9 in, PowerPoint 1280 px → 13.33 in, and an 8 pt floor. CLAUDE.md's "export never inflates fonts" rule is restated as "a floor, never a multiplier". Checked visually on a sensochoc PCA biplot at 2880 px / 443 dpi: legible. The overlapping loading labels there are a pre-existing on-screen issue (UI-11 territory).
- **UI-13:** stored maps are moved to the new palette **by palette position** instead of being rebuilt from each module's products. Fusion and PrefMap inherit the DA/RATA map, and a per-module rebuild would give a shared product two colours. The refresh runs in `app.py` after the sidebar (whose selectbox writes the palette) and before any chart.
- **Methods_Notes wording is generated from run records**, never from widgets, and reads alpha and post-hoc with bracket access: a missing value raises rather than being guessed. The DA model is already called "Mixed-model ANOVA (conditional F-test)" there (D-14), ahead of Stage 7's UI/doc rename.
- **CHANGELOG:** one `[1.0.0rc1] — Unreleased` entry in three dated parts (the former `[Unreleased]`, `[1.1.0]` and `[1.0.0]` headings, demoted one level), plus an empty `[Unreleased]` above it.

Owner actions (both done 2026-09-29):
- Local tag deleted (`git tag -d v1.0.0`; it was `5cefe01`, never pushed). Only `v0.2.0` remains locally; the remote has no tags.
- Branch pushed; CI green on all three jobs, including the tightened pins (DA F and ICC at 1e-10, RATA/Liking LR at 1e-6 against R). If one of them ever moves on a runner, the STAT-13 rule applies: treat it as a numerical finding, do not loosen the pin.

Facts later stages rely on:
- **Stage 7:**
  - `utils/reporting.py` now states each method in one sentence per module. When DOC-01 rewrites a methods section, change the matching sentence in the same commit, and add the "How to report" block to `Statistical_Methods_README.md` (the DOC-02 remainder row).
  - The software citation uses `core.config.REPOSITORY_URL`. Derive UI-08's "Get help" / "Report a bug" URLs from it rather than adding a second constant.
  - `Statistical_Methods_README.md` still says "v1.0" in two prose places (l.1763, l.2264) and the footer mentions "v1.x". These describe the release line, not a version; decide in DOC-07/DOC-09 cleanup whether to keep them.
  - README's export sheet lists (DOC-04) must now include `Methods_Notes` for DA, Liking, Fusion and PrefMap, and the new `Run_Parameters` rows.
  - The About overlay (UI-09) must keep the caption `FreeSense v{VERSION} ·`; `tests/test_version_identity.py` reads it.
  - A version bump now needs README's header and citation line, the methods `**Version:**` line and the CHANGELOG heading changed together (the test fails otherwise).
- **Stage 8:**
  - The palette selectbox's help text now says the change applies at once. UI-01's `persist_state` fix must keep the `app.py` refresh after `render_sidebar()`.
  - D-15's new default palette is the next palette switch, and the refresh maps by position, so a palette of a different length than 11 changes the cycling for studies with more than 11 products. Keep all product palettes at the same length, or rebuild maps from sorted product names when lengths differ.
  - IO-08 remainder: one header label map across builders (see `docs/open-items.md`).
- **Stage 9:**
  - Checklist part A item 5 ("`Run_Parameters` shows the candidate version, the date, package versions and the file hash; `Methods_Notes` is present") is now true for all six modules. `git_commit` reads `-dirty` whenever there are uncommitted tracked changes, and "—" in a `git archive` build without `.git`, which is what testers without GitHub get. The version string is then the only build identifier, so the version policy (every `stats/` change bumps the rc) matters for them.
  - A release archive must include `core/provenance.py` and `utils/reporting.py` (plain modules, no data files).

- **CI trigger note:** GitHub skips a push when the head commit's message contains the skip-ci token *anywhere*, body included. The first re-trigger commit quoted it in its explanation and was skipped too; the one after it ran.

- **Status: Stage 6 COMPLETE (2026-09-29), CI green on all three jobs, local `v1.0.0` tag deleted, merged into `main`.** Next: Stages 7 and 8 (in parallel).

---

## Stage 7: Documentation, licensing and user-facing text — COMPLETE 2026-09-29

**Goal.** A sensory scientist can format their file, run the analysis, and write an accurate methods section from the app's own documentation. The licence position is clear.

**Findings.** DOC-01, DOC-04, DOC-05, DOC-06, DOC-07, DOC-10, DOC-03 (methods doc part), REL-06 (claims; README's Python line was already changed to "3.12 to 3.14" in Stage 1, so check the other documents), REL-07, REL-08, SEC-03, SEC-05, FUNC-09, FUNC-11, UI-08, UI-09 (with DOC-08), UI-10, PERF-07. (REL-03 closes in Stage 2; REL-10 is deferred to Stage 11 per D-19.)

(Stage 2 note: `tests/test_apptest_bundled_datasets.py::test_jar_example_is_detected_as_jar` is a strict xfail for DOC-06; shipping a numerically coded JAR example makes it fail on purpose, so remove the marker in the same commit. pingouin is gone, so the licence text need not discuss a GPL runtime dependency; `Statistical_Methods_README.md` §18b already describes the closed-form ICC interval.)

**Brief.**
- **DOC-01, `Statistical_Methods_README.md`.** Ten passages contradict the code (all ten verified by the challenge pass):
  - §16/§23a (SE counts: the code uses observations)
  - §23c (contrast FDR family: the code uses the full pair family)
  - §24 (the Liking LMM is REML for LS means and ML for the LRT; the df is not Satterthwaite; rewrite after Stage 4)
  - §8 (no `fillna(0)` any more)
  - §15 (formulas show treatment coding, the code uses Sum; Langsrud 2003 recommends Type II, not Type III)
  - §51 (CA bootstrap is 500 with seed 42, not 200 with sliders)
  - §27 (999 permutations, not 10,000)
  - §48 (correction options list)

  Fix them all. Then add `tests/test_documented_defaults.py`, which asserts a table of documented defaults (bootstrap B, seeds, permutation counts, `n_init`, correction option lists, the `alpha_interaction` default) against the constants in code.
- **DOC-03.** The methods doc says the interaction alpha does not affect product p-values. It does; fix the sentence.
- **DOC-04, `README.md`.** Several module sections are stale: the DA post-hoc default is FDR, not Tukey-Kramer; the JAR correction is not configurable; Liking demographics is an LMM with Wald tests; the CATA penalty caveat is a single caption; there is no "20% dropout banner"; the §32 cross-reference is wrong; the export sheet lists are wrong. Generate sheet lists from the builders, or drop them.
- **DOC-05 / D-14 (decided: option 3).** Call the DA model "Mixed-model ANOVA (conditional F-test)" everywhere, with one explanatory sentence: assessor is treated as random, so Product is tested against the Assessor x Product interaction when that interaction is significant, and against the residual otherwise. Apply this (UI strings at `modules/descriptive/workflow.py:5, 199-208, 389, 755, 758-762, 791, 814, 1185` and docs). Rewrite the correction caption (LSD is the most liberal, not BH). Move the DA progress lines so they appear when each stage runs (with PERF-05's status update if done).
- **DOC-06 / D-05.** Add a per-module "File format" section with one small table each, including Liking long format, JAR coding, the demographics key, the CATA companion file and the PrefMap inputs. Recode the JAR example numerically.
- **DOC-07, DOC-10.** Regenerate the methods TOC from the headings and fix the 10 dead in-app anchors. Remove the internal stage codes (69) and stale identifiers from user docs. Add the missing `calculate_panel_stability` docstring and complete the four incomplete ones.
- **UI-09 / D-21 (decided).** Write a short user-facing `ABOUT.md` for the About overlay. It covers:
  - purpose;
  - the modules, in the landing-page grouping (D-16): consumer methods (Liking, CATA), profiling (DA, RATA), mapping & integration (PrefMap, Fusion); RATA is described as a profiling method used with consumer or trained panels;
  - version and a licence summary;
  - the disclaimer (D-12): "Results are provided without warranty; check critical conclusions before reporting them";
  - how to report problems;
  - how to cite (the README citation line, until D-19's DOI exists);
  - data handling (SEC-05).

  Point `utils/docs.ABOUT_README` at it. Then clean up README for release: keep install, data formats, module guides and licence, and move developer and agent notes (project structure, conventions, stage history) into a `CONTRIBUTING.md` or `docs/` file.
- **UI-08 / D-12 (decided: GitHub issues; email later).** Set `st.set_page_config(menu_items=...)` with "Get help" (README on GitHub), "Report a bug" (`https://github.com/Sesnor-y/FreeSense/issues`; while the repository is private this works only for invited collaborators, so the support email is shown beside it once it exists, see Stage 9B) and "About" (one paragraph with version, licence and disclaimer). Add a "Report a problem" tertiary link in the sidebar. Keep the URL in one constant in `core/config.py` so the email address can be added later in one place.
- **SEC-05, FUNC-09 / D-11 (decided: option 1).** Add a "Your data" statement to About and README: "FreeSense runs on your own computer. Your files are processed in memory and are never sent anywhere or stored. Refreshing or closing the browser tab clears your data and results; download the Excel report to keep them." Add a one-line caption with the refresh warning on the landing page and each Step 1. This statement is only true once SEC-03 is fixed, so do SEC-03 in the same PR.
- **SEC-03.** Set `[server] address = "localhost"` in `.streamlit/config.toml`. This stops listening on all interfaces and removes the startup call to `checkip.amazonaws.com`. Verify with `ss -ltn` after launch that the server listens on 127.0.0.1 only, and that no outbound request happens at start.
- **REL-08 / D-05.** Add `example_data/COPYING` (GPL-2.0 text) and reference it from `example_data/README.md` and README's licence section.
- **REL-06, REL-07.** README's Python claim matches D-10 (done in Stage 1; check it). Add a `[project]` table to `pyproject.toml` (name, version, description, MIT licence, `requires-python = ">=3.12"`, URLs including Issues).
- **D-13 (decided: option 2).** Reword validation claims in README, About and the methods doc to "cross-checked against R on published datasets". Link the coverage table in `validation/README.md` and state the exceptions: R ports of FreeSense's own algorithm, balanced reference data only, and the unbalanced-design paths not yet referenced.
- **FUNC-11, UI-10.** Derive step references in messages from `ui_shell.step_title`, and fix the wrong step numbers and nonexistent button names.
- **PERF-07.** Fix the `render_chart` kaleido docstring.

**Files.** `Statistical_Methods_README.md`, `README.md`, `ABOUT.md` (new), `CONTRIBUTING.md` or `docs/` (developer notes moved out of README), `utils/docs.py`, `app.py`, `core/config.py` (support URL), `utils/ui_shell.py`, `.streamlit/config.toml`, `example_data/README.md`, `example_data/COPYING` (new), `example_data/04_JAR/` (recoded file), `pyproject.toml`, `validation/README.md`, module UI strings, `stats/*.py` docstrings, tests.

**Entry criteria.** Stages 4 and 6 merged (docs describe the final methods and exports).

**Exit criteria.**
- `tests/test_documented_defaults.py` passes.
- A script lists every backticked path or function name in the user docs and asserts that each one exists.
- The About overlay has no relative links and no developer sections.
- A fresh reader test: someone who has not used FreeSense formats a file for each module from the README alone. This is a manual check, noted in the PR.

**Effort.** M to L (3 to 4 days; the methods document is large).

**Risks.** The methods document is 257 KB, and edits can introduce new drift. The defaults test and the identifier scanner are the guard.

**Outcome (2026-09-29, branch `stage-7-docs` on `3f6bf28`; 9 commits `1c11d77`…`ade301a`; CI **green on all three jobs** (owner confirmed 2026-09-29)).** Every Stage 7 finding is addressed: DOC-01, DOC-02 (remainder), DOC-03, DOC-04, DOC-05 (except the DA progress lines, which are PERF-05 in Stage 8), DOC-06, DOC-07, DOC-09 (beta notes), DOC-10, REL-06 (no other document claims 3.11), REL-07, REL-08, SEC-03, SEC-05, FUNC-09, FUNC-11, UI-08, UI-09, UI-10, PERF-07. 18 rows deleted from `docs/open-items.md`.

Results on the branch:
- **Suite:** 861 passed, 0 skipped, 0 xfailed (the strict DOC-06 xfail is gone) with `FREESENSE_REQUIRE_DATA=1`, one BLAS thread and coverage; ruff clean. Coverage 88.0 %, lowest `stats/` file `posthoc.py` 84.2 %.
- **Runtime:** 114–119 s wall on this machine; `main` (`3f6bf28`) measured 118 s under the same settings in a clean worktree the same afternoon, so the stage adds nothing measurable. (Stage 6's 75.9 s was taken under different machine load; compare like with like.)
- **Snapshots:** not re-run: nothing under `stats/` changed except docstrings. The version stays `1.0.0rc1` for that reason (see decisions).
- **Exit criteria:**
  - `tests/test_documented_defaults.py` passes: **met** (27 defaults, 11 retired claims).
  - A script lists every backticked path or function name in the user docs and asserts each exists: **met** (`tests/test_doc_identifiers.py` over README, ABOUT, CONTRIBUTING, the methods reference, `example_data/README.md`, `validation/README.md`; a probe proves it catches `cochran_q_per_attribute`).
  - About overlay has no relative links and no developer sections: **met** (`tests/test_help_and_privacy.py::test_about_is_user_facing_with_no_relative_links`).
  - Fresh-reader test: **not met — not done.** It needs a person who has not used FreeSense; note it in the PR.
  - SEC-03 check: `ss -ltnp` after `streamlit run app.py --server.port 8597` showed `LISTEN … 127.0.0.1:8597`, the log printed a single `URL: http://localhost:8597` (no Network/External URL), and `ss -tnp` showed no connection from the process.

Decisions taken in this stage (the owner may revisit):
- **No version bump.** The only `stats/` edits are docstrings (DOC-10); CLAUDE.md's policy says "every change under `stats/`". `1.0.0rc1` has not been tagged or given to anyone (Stage 9A creates the tag), so the numbers an rc1 export carries are unchanged. If you read the policy literally, bump to `rc2` before tagging.
- **JAR example added, not replaced.** `JAR_sensominer_numeric.xlsx` sits beside the French-text original, which `validation/Liking/JAR/` and the R script read. Coding (5-point scale, 5 unused): `*_vmtpasassez`/`fade_bt` = 1, `*_pasassez`/`fade_unpeu` = 2, `jar` = 3, `*_t`/`vive_t` = 4. Collapsed around 3 it is exactly the validation's 3-category recode, so the app's mean drops equal SensoMineR's.
- **Export sheet inventories removed from README** (DOC-04 offered "generate or drop"). The app's own lists are tested; a README copy would drift again.
- **Methods headings renamed rather than anchors hacked.** Streamlit 1.64 builds heading ids with sindresorhus/slugify defaults (read from `StreamlitMarkdown.*.js`): it splits camel case ("McNemar" → `mc-nemar`), letter-digit runs ("PLS1" → `pls-1`) and turns `/` into `-`, while GitHub drops those characters and keeps double hyphens for em dashes. 18 linked headings were renamed; `scripts/methods_toc.py` generates the TOC and reports mismatches. The in-app click was not tried in a browser; the rule is from the bundle source.
- **"Report a problem" opens a prefilled new-issue URL** (version, module, a privacy reminder), not the issues list; the page menu's "Report a bug" goes to the list.
- **The refresh/"Your data" caption sits in `render_step_header` (Step 1)**, one site for all six modules, and in the landing footer.
- **`ABOUT.md` citation uses a `{VERSION}` placeholder** that `app.py` fills, so the version stays single-sourced.

Facts later stages rely on:
- **Stage 8 (starts from `main` after Stage 7; these are the Stage 7 edits it builds on):**
  - `utils/ui_shell.py`: this stage edited the DA landing-card `description`/`methods` (two lines above the RATA card copy Stage 8 rewrites), the landing footer (a `SESSION_NOTE` caption above the version caption), `render_step_header` (Step 1 caption), `_render_about_footer` (new `ui_sb_report` link button), the methods-reference caption in `_render_settings`, a new `step_ref()` beside `step_title()`, and the `render_chart` docstring. `_render_settings(module_key)` no longer uses `module_key`.
  - `tests/test_apptest_shell.py`: the badge→method map says `"Mixed-model ANOVA"`, and the About overlay test compares with `{VERSION}` filled in. `test_theme_config_declares_light_and_dark_variants` still pins `#0d9488`; UI-03 changes it.
  - README and `ABOUT.md` already use D-16's grouping ("Consumer methods" with Liking first, "Profiling", "Mapping & integration") and describe RATA as used with consumer or trained panels. Until Stage 8 merges, the app's landing page still says "Trained panel". `test_about_is_user_facing_with_no_relative_links` checks that order in ABOUT.md.
  - UI-04: the methods reference §29 "Colorscale" paragraph states "RdYlGn — red = low, green = high". Update it with the ramp change; `tests/test_doc_identifiers.py` and `tests/test_methods_reference.py` must stay green (no stage codes in the new text).
  - FUNC-08's "Current data" caption goes near the new Step 1 `SESSION_NOTE` caption; both are Step 1 captions, keep them adjacent.
  - A message that names another step must use `ui_shell.step_ref`; `tests/test_step_references.py` scans `modules/`.
  - DOC-05's "DA progress lines appear when each stage runs" was left to PERF-05.
- **Stage 9:**
  - The release tree must include `ABOUT.md`, `CONTRIBUTING.md`, `scripts/methods_toc.py` and `example_data/COPYING` (checklist B.6 requires the last).
  - 9A step 7's rule ("never merge or cherry-pick from FreeSense-dev") goes into `CONTRIBUTING.md`, which now exists.
  - 9B support email: set `core.config.SUPPORT_EMAIL`; the page menu and the sidebar then show it automatically. README's "Reporting problems" and `ABOUT.md` "Reporting a problem" are prose and must be edited by hand (the tests check the issues URL, not the email).
  - `REPOSITORY_URL`, `pyproject.toml`'s `[project.urls]` and the README/ABOUT citation all say `Sesnor-y/FreeSense`, which is the name the new repository gets; `tests/test_version_identity.py` checks the pyproject URLs against the constant. While the repository is private, the "Report a problem" link works only for invited collaborators.
  - `pyproject.toml` now carries the version too; `test_version_identity.py` fails if a bump misses it (as it does for README, the methods reference and CHANGELOG).
  - `validation/README.md` keeps review codes (TEST-05, STAT-02, …) as a developer record; README links to it. Decide at 9A whether the public repository should carry them.
- **Stage 11 / backlog:**
  - UI-09 / DOC-08's "open the methods reference at the module's chapter" (per-chapter rendering, deep links from steps) was not done; the TOC links now work, which was the blocking half.
  - `compute_jar_penalty_long` and `compute_jar_distribution` still lack an independent reference (TEST-02 row updated).
- **Surprises worth knowing:**
  - The Liking export step never listed `JAR_Distribution`, although the workbook had it whenever JAR ran: no bundled file drove the JAR step, so no test saw it. The first JAR end-to-end run caught it.
  - Two banners were wrong in a way a user would copy: Liking Step 7 said MDPREF uses consumers as observations (it uses products), and DA Step 4 said "FDR-corrected" whatever method was chosen.
  - The methods reference's Chapter 3 still described the pre-Stage-4 contrast (per-pair paired SE for RATA Tukey, a reduced FDR family): the register listed only part of it. Rewritten from `stats/contrast.py`.
  - The app and the JAR validation emitter count JAR frequencies over different rows (139 vs 141): the app drops evaluations with a blank liking score before anything else. Mean drops agree; documented in `validation/Liking/JAR/README.md`.

- **Status: Stage 7 COMPLETE (2026-09-29), CI green on all three jobs, merged into `main`.** Next: Stage 8, started from `main` after this merge (not run in parallel), then 9A.

---

## Stage 8: Presentation and accessibility fixes in the release line — COMPLETE 2026-09-29

**Goal.** Nothing on screen is misleading or unreadable.

**Findings.** UI-01, UI-02, UI-03, UI-04, UI-05, UI-06 (with IO-10), D-16 (landing page rename and reorder), UI-14, FUNC-08, PERF-05, SEC-07 (remainder from Stage 3).

**Brief.**
- **UI-01.** Opening About or Methods resets the colour scheme and export format, because the sidebar settings widgets are not persisted. Add `persist_state="session"` and an AppTest round trip.
- **UI-02.** The significant rows of the Liking penalty table are unreadable on the dark theme (1.13:1), because of the `#ffe0e0` background at `modules/liking/workflow.py:84`. Use a translucent tint, as other modules do.
- **UI-03.** The primary teal `#0D9488` gives 3.74:1 for white button text. Change `primaryColor` to `#0F766E` (5.47:1), keeping the logo teal only in the logo.
- **UI-04.** The preference-surface guide says "green = high, red = low", but the colour-blind ramp makes red high. Use one ramp direction for all palettes, generate the sentence from `describe_liking_ramp`, and say "AICc", not "AIC".
- **UI-05, UI-06 / D-15 (decided: option 3).** Semantic red/green ignores the colour-blind setting, the colour-blind palette contains `#F0E442` (1.32:1 on white), and the default palette has deuteranopia-confusable pairs.
  - Use CVD-safe semantic classes (blue/orange/grey) with a second channel (marker symbol, or a text flag column in the DA detail table).
  - Drop or move the yellow.
  - Make the corrected colour-blind palette the default (`core/state.init_session` seeds `global_colour_palette`), and keep the old default available as an option. The owner may revisit the choice after seeing it.
  - Test: the minimum pairwise ΔE under simulated deuteranopia and protanopia exceeds 10 for the first 8 colours of the default palette.
- **D-16, landing page rename and reorder (decided; layout unchanged).** In `_LANDING_SECTIONS` (`utils/ui_shell.py:42-52`):
  - rename the "Trained panel" section to "Profiling";
  - replace its subtitle "Characterise your products with trained assessors" with wording that does not imply trained assessors, because RATA is used with consumers too (suggested: "Characterise your products by their sensory attributes");
  - in "Consumer methods", reorder the modules to `("Liking", "CATA")`;
  - check the "Consumer methods" subtitle ("Untrained-panel acceptance and characterisation") still fits;
  - update the `render_landing_page` docstring, any card copy that says "trained panel" for RATA, and `tests/test_apptest_shell.py`.

  The fuller regrouping and the narrow-screen fix (UI-12) are paused; see Stage 11.
- **SEC-07 remainder (from Stage 3).** Wrap product, attribute and cluster names interpolated into result-page captions and markdown in `core.upload_validation.md_code` (the Step 1 sites were done in Stage 3).
- **UI-14.** The cluster-size metric shows its share as a green "increase" delta. Set `delta_color="off"` or move the share into the value.
- **FUNC-08.** After a module switch, Step 1 shows an empty uploader while the results remain, and any setting change forces a re-upload. Show "Current data: <file>, uploaded <time>" from module state when the uploader is empty.
- **PERF-05.** DA's progress lines are all printed before the blocking call. Replace them with `status.update()` between real stages (a progress callback from `run_full_da_analysis`).

**Files.** `utils/ui_shell.py`, `.streamlit/config.toml`, `utils/colours.py`, `utils/plotting.py`, `modules/liking/workflow.py`, `modules/descriptive/workflow.py`, module Step 1s, tests.

**Entry criteria.** Stage 6 merged (UI-13 colour maps). Stage 7 is merged too (owner, 2026-09-29: Stage 8 was not run in parallel), so start from current `main` and read the Stage 7 outcome's "Stage 8" notes.

**Exit criteria.**
- WCAG contrast of text on primary buttons is at least 4.5:1 in both themes (computed in a test from `config.toml`).
- The palette ΔE test passes.
- The UI-01 AppTest round trip passes.
- No `#ffe0e0`-style opaque light backgrounds remain in Styler code (grep test).
- The landing page shows "Consumer methods" (Liking, CATA), "Profiling" (DA, RATA) and "Mapping & integration" (PrefMap, Fusion) (AppTest), and before/after screenshots of the landing page and one chart per module are attached to the PR for the owner.

**Effort.** M (1.5 to 2 days).

**Risks.** A palette change alters every chart. Take screenshots (run skill) before and after for the owner to approve.

**Outcome (2026-09-29, branch `stage-8-presentation` on `9a6c5f6`; 13 commits `9bbb2b0`…`75e1322`; CI **green on all three jobs** (owner confirmed 2026-09-29)).** Every Stage 8 finding is addressed: UI-01, UI-02, UI-03, UI-04, UI-05, UI-06, UI-14, D-16 and SEC-07 closed; FUNC-08 and PERF-05 closed as briefed, with their remaining halves re-staged to 11. The optional IO-08 header map was inventoried, not done. Eight rows deleted from `docs/open-items.md`; FUNC-08, PERF-05 and IO-08 rewritten with what remains.

Results on the branch:
- **Suite:** 889 passed, 0 skipped with `FREESENSE_REQUIRE_DATA=1`, one BLAS thread and coverage (105 s wall); ruff clean. Coverage 88.0 %, lowest `stats/` file `posthoc.py` 84.2 %.
- **Snapshots:** not re-run; nothing under `stats/` changed, so the version stays `1.0.0rc1`. Only `run_full_da_analysis` (in `modules/`) gained a progress callback; it computes the same frames.
- **Exit criteria:**
  - Primary-button text ≥ 4.5:1 in both themes, computed from `config.toml`: **met** (`test_primary_colour_meets_wcag_aa_in_both_themes`: light `#0F766E` 5.47:1, dark `#11847B` 4.55:1).
  - Palette ΔE test: **met** (`test_palettes.py`: first eight colours min ΔE 18.5 deuteranopia, 19.2 protanopia, 27.8 normal).
  - UI-01 AppTest round trip: **met** (`test_sidebar_settings_survive_the_about_and_methods_overlays`).
  - No opaque light Styler backgrounds (grep test): **met** (`test_styler_backgrounds.py`, which also proves it catches the old `#ffe0e0`).
  - Landing sections (AppTest): **met** (`test_landing_sections_follow_d16`). Before/after screenshots of the landing page (light and dark), the sidebar and one chart per module (eleven charts): **met** (owner approved 2026-09-29). They are on a private comparison page (https://claude.ai/artifact/4hpPbBxPK2LiZ4SAbCBvLZ); the PNGs were left in the session scratchpad, not committed.
- Every fix landed with a test that fails on the code before it (checked by stashing the fix).

Decisions taken in this stage (the owner may revisit):
- **`primaryColor` is set per theme, not the plan's single `#0F766E`.** Checked in a browser: Streamlit 1.64 draws primary-button text white *and* the active tab label in `primaryColor`. On the dark background no colour gives both 4.5:1 (the best is about 4.2 each). `#0F766E` would have dropped dark-theme tab labels from 4.77:1 to 3.26:1, so dark uses `#11847B`, the lightest teal of that hue with white text at 4.55:1 (tab label 3.92:1, below 4.5:1 for 14 px text). If a WCAG AA claim is ever made (B10 D-5), this is the one known shortfall.
- **The new "Colour-blind safe" palette is not Okabe–Ito.** Okabe–Ito's orange and sky blue are about 2:1 on white, and darkening the orange into a visible band merges it with vermillion under deuteranopia (ΔE 5.7). The palette keeps Okabe–Ito's blue, vermillion and bluish green and fills the rest by a max–min ΔE search over colours with ≥ 3:1 on both backgrounds and ≥ 30° hue separation (method in the `utils/colours.py` comment). The owner said "revisit if it looks wrong": the comparison page shows it.
- **Palette keys:** the old default is `"bold"`; there is no `"default"` key any more, and lookups are strict. The `global_colour_palette` reads that used `.get(…, "default")` now use bracket access, so the hand-built states in six test files carry the seeded global. `Run_Parameters` now reports `palette = colourblind` for a default run.
- **Liking ramp:** red = low, blue = high (`LIKING_RAMP`), for every palette. Greyscale users get the same red–blue ramp (it was red–green before); nothing prints it in grey.
- **UI-05 went wider than the register's list:** the DA panel-performance traffic light (green/amber/red, ΔE 4.4 deuteranopia) and the Fusion block colours (orange/green, ΔE 4.6 protanopia) were also red/green-confusable and changed. The Fusion Q² heatmap's white stop moved from 0.3 to 0.5 of the scale, so Q² = 0 is white rather than faintly green.
- **UI-02:** untestable rows are no longer greyed rather than re-coloured: no fixed grey reaches 4.5:1 on both backgrounds, and the Significant column already says "n too small".
- **SEC-07:** a second helper, `md_escape` (backslash-escapes Markdown punctuation, including `$` and `:`), for headings, expander labels and pre-built sentences where `md_code`'s monospace reads oddly. The end-to-end test covers DA, RATA, CATA and Liking-with-JAR; Fusion and PrefMap sites were swept by an AST scan but have no end-to-end test.
- **FUNC-08** shows the caption whenever the module has results, not only when the uploader is empty: it is true in both cases and needs no uploader-key plumbing.
- **Liking Step 7** now renders the shared preference-surface guide (`ui_shell.render_prefmap_explanation_expander`); its own copy was deleted (a CODE-07 parallel copy).
- **IO-08 remainder not done.** The six bundled exports carry 115 lower-case/snake_case headers against 177 others; about a dozen of the 115 are the user's own attribute names. Relabelling needs the owner's label list first (see the open-items row).

Facts later stages rely on:
- **Stage 9:**
  - The release tree must include `tests/colour_metrics.py` (imported by three test files).
  - A candidate's screenshots in README or release notes, if any, must be retaken: every chart's colours changed.
  - Checklist item: a tester with the dark OS theme sees tab labels at 3.92:1 (see above); decide whether the release claims any WCAG level before 9C.
- **Stage 11 / backlog:**
  - `modules/liking/ui.py::plot_mdpref_heatmap` is dead (nothing imports it; the live one is in `utils/plotting.py`) and still uses `RdYlGn`. Delete it with CODE-08.
  - `utils/plotting.py` still sets the dendrogram "amber branches" and the scale-usage amber/blue bars; both pairs are CVD-safe and were left.
  - The DA detail table's vermillion value text is 3.87:1 on white; the new "Below guideline" column carries the same fact in words.
- **Surprises worth knowing:**
  - The review had no browser; this stage installed Playwright + headless Chromium in the session scratchpad (not a project dependency) to measure the theme. Chart screenshots were taken by driving AppTest on the bundled datasets and rendering the exact Plotly JSON the app sends with kaleido, which is repeatable but shows the export look, not Streamlit's on-screen theme.
  - Stage 3's SEC-07 sweep had missed some Step 1 sites too (the CATA/Liking column lists, the Liking out-of-range cell list); fixed here.
  - The session prompt still described Stage 7 as running in parallel; it had already merged, and this branch starts from `main` after it (`9a6c5f6`), as the plan says.
  - The UI-03 brief assumed `primaryColor` only colours buttons; it also colours the active tab label, which is why the fix is per theme.

- **Status: Stage 8 COMPLETE (2026-09-29), CI green on all three jobs, screenshots approved, merged into `main`.** Next: 9A.

---

## Work done after Stage 8, outside this plan (2026-09-30 to 2026-10-13)

Before 9A, three pieces of work landed that this plan did not schedule. Each has its own notes; the CHANGELOG `[1.0.0rc3]` entry is the user-facing record.

- **Reference-contrast redesign**, Phases A–E (`working_notes/contrast-fix.md`). The contrast is many-to-one in all four modules: Tukey → Dunnett (`stats/shared/dunnett.py`), BH over k − 1, intervals that match the adjusted decision, and one shared renderer, `utils/contrast_view.py`. This supersedes the Stage 4 exit criterion (see the note there) and closes STAT-14. The decisions, intervals and effect sizes it shows changed.
- **Interactive HTML report**, Phases 1–4 (`working_notes/interactive-reports.md`): `modules/<m>/figures.py`, `modules/<m>/report.py`, `utils/report_builder.py`, `utils/report_theme.py`, golden figure specs. No statistic changed.
- **STAT-16, Liking segmentation order stability** (a new finding, not in the register): AHC and k-means are re-run on 20 seeded reorderings, and the result reports the adjusted Rand index. Partitions are unchanged.

What this means for the rest of the plan:
- **Version.** The contrast redesign moved the version to `1.0.0rc2`. Two later `stats/` changes (contrast Phase C, STAT-16) landed without a bump, so on 2026-11-20 the version moved to **`1.0.0rc3`**. rc2 was never tagged. **The first candidate given to testers is therefore rc3, not rc1;** "rc1" in 9A below means "the first tagged candidate".
- **Snapshots.** Checklist A.3's comparison for the first candidate must expect the contrast changes (`contrast-fix.md` Phase B) and the new segmentation `stability` fields.
- **Review on 2026-11-20** (stages 0–8 re-checked against `d66af9d`). Locally: 1,054 tests passed, 0 skipped. Coverage and ruff were not run locally. The checks that would break later stages are fixed in that commit:
  - the version bump above;
  - `.agents/` added to 9A's exclusions (it holds a tracked symlink into `env/`);
  - checklist A.4 reworded;
  - `.claude/settings.local.json` added to `.gitignore`;
  - a pandas `FutureWarning` in `utils/contrast_view.py` fixed.

  Open decisions found only in this plan's notes are now rows in `docs/open-items.md`: UI-03 (WCAG claim), CODE-03 (Liking optimiser default), DOC-06 (fresh-reader check), UI-09 (chapter links), the CODE-08 dead plotter, and a new STAT-17. 
- **TEST-02 decided (owner, 2026-11-20): option 2.** Methods in the four stable modules must have a known-answer test before 1.0.0, while the three beta-module methods (PrefMap surface, PLS jackknife, CV coefficient stability) are deferred to Stage 11. The same day, known-answer tests were added for the demographics mixed model, the JAR distribution and penalty table, and panel stability. **Still blocking 9C:** `compute_ca_ellipses` and `varimax`; both probably need R once (see the TEST-02 row). Writing those tests showed STAT-17's real trigger: blank liking scores. That case is pinned as a strict xfail.
- **STAT-17 and STAT-18 are minor (owner, 2026-11-20).** STAT-18 is the full-panel stability row having no ±1 SD band. Neither defect interferes with meaningful interpretation: no significance call or reported mean is wrong. Both are LOW, in Stage 11, and do not block any candidate.

---


## Stage 9: Release repository, private testing, then public release

The release happens in three steps. The new `FreeSense` repository is created **private** and stays private through a round of private testing. It is made public only when every check has passed (owner, 2026-09-27). There is no target release date; Stage 9C happens when the owner decides the testing is sufficient.

**Findings.** SEC-04 (with REL-02), SEC-08 (with REL-12), REL-01, REL-11 (local channel: the lockfile and README install section are enough).

### Stage 9A: Clean private release repository

**Entry criteria.** Stages 1 to 8 merged. The three third-party files are treated as not redistributable (they are not in the release tree in any case).

**Goal.** A new private repository whose history contains only the release state: no third-party files, no home paths, no private dataset names.

**Brief.** D-03 option 1. The owner performs the GitHub web steps; the session prepares and verifies everything else.

**Owner decisions, 2026-11-20 (before 9A started):**
- **`CLAUDE.md` stays public**; `.claude/`, `.agents/` and `working_notes/` stay private. `CLAUDE.md` now says they are maintainer-local and that the Streamlit skill ships inside the Streamlit package.
- **Pointers to `working_notes/` in public files were reworded** (code comments, docstrings, `CHANGELOG.md`, `docs/open-items.md`, `validation/Contrast/`) on branch `stage-9a-release-prep`. The only references left have a job: `.gitignore`, the ruff exclude, `tests/test_apptest_shell.py`'s excluded folders, and `tests/test_help_and_privacy.py`.
- **Two development machines (Mac primary, Linux secondary).** The private files move between them through a separate private repository, `Sesnor-y/FreeSense-private`, used as a bare-repo overlay on the `FreeSense` working tree (`git --git-dir=$HOME/.freesense-private.git --work-tree=<clone>`, alias `fsp`; `status.showUntrackedFiles no`; new files need `fsp add -f`, because the public `.gitignore` applies too). It tracks `.claude/agents`, `.claude/skills`, `.agents` and `working_notes`, never `.claude/settings.local.json`.
- **Remote switch on both machines before step 5.** After step 1, every clone of the old repository (Mac *and* Linux) runs step 2 before the new `FreeSense` exists. Once it exists, GitHub's redirect stops, and a stale `origin` would push the old history into the repository that goes public.

1. **Owner:** rename the current private repository `Sesnor-y/FreeSense` to `Sesnor-y/FreeSense-dev` (Settings, General, Repository name).
2. **Session:** `git remote set-url origin https://github.com/Sesnor-y/FreeSense-dev.git` in the working clone, then `git fetch` to confirm.
3. **Session:** build the release tree in a temporary directory from `git archive HEAD` of the release commit, excluding `.claude/`, `.agents/` and `working_notes/`. All three are tracked in `FreeSense-dev` (since 2026-09-27 for `working_notes/`, as a backup of the review and plan) but must never enter the new repository:
   - the notes name the SEC-04 files, and the reproduction scripts contain home paths;
   - `.claude/skills/developing-with-streamlit` and `.agents/skills/developing-with-streamlit` are tracked symlinks into `env/lib/python3.14/site-packages/streamlit/…`, which dangle in any other checkout (SEC-08).

   In the release tree's `.gitignore`, add `working_notes/`, `.claude/` and `.agents/` before the first commit, so none of them can be committed later by accident. Run `git init`, make a single commit, and tag it with the current candidate version (`v1.0.0rc3` as of 2026-11-20; see "Work done after Stage 8" and "Versioning during testing").
4. **Session, before any push:** in the new repository, run `git log --all --name-only` and a full-tree grep for:
   - `xlsm`, `pptx`, `PLS.pdf`;
   - `/home/`, `/var/home/`, `Lukas/Projects`;
   - the private dataset names listed in B07 (SEC-08);
   - `working_notes`, `.claude` and `.agents` as paths: `git ls-files | grep -E '^(working_notes|\.claude|\.agents)/'` must print nothing, and `.gitignore` must contain all three entries.

   Every search must return zero hits. Confirm there is no symlink (`find . -type l` is empty) and no `.claude/settings.local.json`. (`FreeSense-dev`'s `.gitignore` has listed `.claude/settings.local.json` since 2026-11-20.)
5. **Owner:** create an empty **private** repository `Sesnor-y/FreeSense` (no README or licence, so the first push is clean), and enable Issues.
6. **Session:** add it as a remote, push `main` and the candidate tag, and check that CI runs there.
7. **From this point, development moves to the new repository, and `FreeSense-dev` is archived read-only** (Settings, Archive). Do not merge, cherry-pick or push from `FreeSense-dev` into `FreeSense`. The two histories are unrelated, so a merge would import the old history, including the SEC-04 files, into the repository that later goes public. Record this rule in `CONTRIBUTING.md`.
8. **Session: keep the working notes available locally.** Copy `working_notes/` from the `FreeSense-dev` clone into the new clone's working directory, where `.gitignore` keeps it untracked. Later stage sessions and the Stage 9B triage can still read the register and plan. From here on, the notes' only backup is the archived `FreeSense-dev` snapshot plus the owner's own copy. Anything worth keeping long-term that is not sensitive (open items, rationale) belongs in `docs/open-items.md`, `CHANGELOG.md` or `Statistical_Methods_README.md`, as `CLAUDE.md` already requires.

**Exit criteria.** The private repository exists; CI is green there; the step 4 searches return zero hits; `.gitignore` in the new repository lists `working_notes/`, `.claude/` and `.agents/`; `FreeSense-dev` is archived.

**Note on CI minutes.** GitHub Actions minutes for private repositories are limited on free accounts, and macOS runners count at a higher rate than Linux. Check your plan's allowance. If it is tight, run the macOS job on tags and on manual dispatch only while the repository is private.

### Stage 9B: Private testing

**Goal.** Real users run the release candidate on their own data before anything is public, and every problem they find is fixed with a regression test.

**Brief.**
- **Giving testers access.** Two routes; use either or both:
  - *GitHub collaborators:* invite testers with the **Read** role. They can clone, install from the lockfile, and open issues in the private repository.
  - *Testers without GitHub:* send a source archive of the tagged candidate (`git archive --format=zip v1.0.0rcN`) with the install instructions. They report by the support email (D-12). The email must exist before this route is used, so creating it moves into this stage.
- **In-app "Report a bug" link.** While the repository is private, the issues URL works only for invited collaborators. Show the support email beside it (one constant in `core/config.py`, as planned in Stage 7), so every tester has a working route.
- **Tester pack** (a short `TESTING.md` in the repository, or a document sent with the archive):
  - how to install;
  - what to try: each module on their own data, and Fusion/PrefMap specifically, since their beta status depends on this;
  - how to report: module, step, a description of the file (not the file itself), the version from the About page, and a screenshot;
  - a privacy note: FreeSense runs locally and sends nothing, and testers must not attach confidential data or identifiable panellist data to issues or emails.
- **Triage.** Every report becomes an issue with a severity label (BLOCKER, HIGH, MEDIUM, LOW, as defined in the review). Each fix follows the usual rule: a regression test that fails first, then the fix. After a round of fixes, cut the next candidate (`v1.0.0rc2`, and so on) and re-run checklist part A.
- **Deciding testing is enough** (agreed by the owner, 2026-09-27):
  - each stable module (CATA, RATA, DA, Liking) has been run by at least two testers on their own data;
  - Fusion and PrefMap have had at least one real-data run each;
  - no open BLOCKER or HIGH issue;
  - the latest candidate has had no new BLOCKER or HIGH report for two weeks.

**Exit criteria.** The owner signs off against the criteria above. Every tester issue is closed, or labelled as post-release and copied into `docs/open-items.md`.

### Stage 9C: Public release

**Goal.** Switch the repository to public, safely.

**Brief.**
1. Set `core/__version__.py` to `1.0.0` (dropping the `rc` suffix), date the CHANGELOG heading, and tag `v1.0.0`.
2. Run checklist part B.
3. **Review every issue, comment and attachment in the repository before switching.** Making the repository public also publishes its issues. Delete or edit anything a tester posted that contains their data, file names, company or product names, or personal details.
4. Re-run the Stage 9A step 4 searches on the full history of the repository as it now stands, including every commit made during testing. Zero hits are required.
5. **Owner:** Settings, Danger zone, Change repository visibility, Public.
6. Create the GitHub release for `v1.0.0` with the CHANGELOG entry as its notes, and check that the README clone command, citation URL and in-app "Report a bug" link work without credentials.

**Exit criteria.**
- Unauthenticated `curl -sI https://github.com/Sesnor-y/FreeSense` returns 200, and `.../issues` is reachable.
- A clean clone on a machine without your credentials installs from the lockfile and passes the tests.
- Checklist part B is complete.

**Risks.** Going public cannot be undone for anything already fetched or indexed. Steps 3 and 4 are the guard; do them twice.

### Versioning during testing

D-01 fixes the public release at `1.0.0`. The candidates given to testers are `1.0.0rc1`, `1.0.0rc2` and so on (PEP 440 pre-release numbers), so every tester report and every exported workbook's `Run_Parameters` names the exact build. The version policy applies from the first candidate: any change under `stats/` produces a new candidate number. Agreed by the owner (2026-09-27) as a refinement of D-01.

**Effort.** Stage 9A: half a day. Stage 9B: depends on the testers; allow about 1 to 3 days of fixing per candidate round. Stage 9C: half a day.

---

## Stage 10: Hosted deployment hardening (not planned)

D-02 decided on local install only, so this stage is out of scope. If a hosted instance is ever planned, the work is:
- upload and decompression limits and hard study-size caps (PERF-04, SEC-02);
- `client.showErrorDetails = "type"` (SEC-06);
- a privacy notice with legal review (SEC-05);
- authentication in front of the app;
- deployment artefacts (REL-11);
- a concurrency load test.

The evidence is in the register under those IDs.

---

## Stage 11: Post-release (point or minor release)

Not required for release. In rough priority:
- **PERF-03 (b):** vectorise the Tukey p-values (`scipy.stats.studentized_range.sf` over an array). This removes about 21 s from a realistic DA Tukey run and 10 to 14 s from RATA; the default FDR path is not affected.
- **REL-10 / D-19 options 1 and 2:** `CITATION.cff`, a Zenodo DOI per release (connect Zenodo to the public repository), and later a software paper.
- **IO-11, REL-09:** add a timeout around `export_figure`, and plan the Plotly 6 / kaleido 1 / pandas 3 migration with the Stage 1 pins as the safety net. Do this sooner if the Windows best-effort smoke test shows the suspected kaleido hang.
- **FUNC-07 follow-up:** let PrefMap and Fusion accept long-format consumer files and pivot them.
- **D-09 option 1:** if European users ask for it, read semicolon/decimal-comma and Windows-1252 CSVs.
- **D-13 option 3:** re-run R with an unbalanced reference dataset; independent (non-port) references for the DA CLD and PrefMap selection (TEST-05).
- **D-20 option 2:** consumer-blocked penalty analysis for CATA and JAR.
- **D-16 follow-up and UI-12:** the landing-page regrouping the owner paused (for example profiling DA, RATA, CATA; consumer acceptance Liking; data fusion and mapping), together with the narrow-screen fix where section headings separate from their cards.
- **UI-11:** coordinate and loading tables under every biplot.
- **CODE-05:** log the swallowed exceptions. **CODE-06:** safe ruff fixes, with E712 ignored (the CLAUDE.md "No linter is configured" line was corrected in Stage 1; widen `select` in `pyproject.toml` rule group by rule group). **CODE-07:** shared contrast-step renderer and ellipse helper. **CODE-08:** delete about 380 lines of dead code. **CODE-09:** extend the layer-rule test to all of `modules/` and move the Fusion Q/leverage limits into `stats/`.
- B05 test set item 14 (re-run `validation/run_all.sh` with R). Items 9, 10, 11 and 13 landed in Stage 1, and item 12 in Stage 5.
- TEST-02 remainder (if the owner defers it here): independent references for the nine methods listed in `docs/open-items.md`.
- PERF-04 and SEC-02 upload limits: low priority for local use, but a `server.maxUploadSize` of about 20 MB in `.streamlit/config.toml` is a one-line safety measure worth adding at any time.

---

## Release line

Order of work: 1, 2, 3, 4, 5, 6, then 7, then 8 (planned in parallel; run one after the other), then the unplanned post-Stage-8 work (contrast redesign, HTML report, STAT-16; see its section), then 9A (private release repository), 9B (private testing, one or more candidate rounds) and 9C (public release). No target date is set.

| Stage | Required for the public release? | Note |
|---|---|---|
| 0 Decisions | Done | All follow-up questions answered |
| 1 Safety net | Yes | |
| 2 BLOCKERs and crashes (plus pingouin removal) | Yes | |
| 3 Input integrity and export safety | Yes | |
| 4 Statistical fixes | Yes | STAT-04 in scope (Fusion ships as beta) |
| 5 Release-floor tests | Yes | |
| 6 Reproducible exports and version | Yes | |
| 7 Documentation, licensing, text | Yes | |
| 8 Presentation, accessibility, landing page | Yes | Testers see these fixes |
| 9A Clean private release repository | Yes | Needed before any tester gets access |
| 9B Private testing | Yes | Ends on the owner's sign-off |
| 9C Public release | This is the release | Owner switches visibility |
| 10 Hosted hardening | No | Local only (D-02) |
| 11 Post-release | No | |

Private testing can start once Stages 1 to 8 are done and 9A is complete. Do not share a build earlier than that: before Stage 2, testers would hit the four BLOCKERs, and before Stage 7, the methods reference contradicts the code.

Estimated effort to the first private candidate (Stages 1 to 8 and 9A): about 16 to 22 working days for one developer with Claude Code, dominated by Stages 4 and 7. Every BLOCKER is fixed by the end of Stage 2, about 4 to 5 days in. Stage 9B depends on the testers. Stage 9C is half a day.

The decisions saved about 2 days against the earlier estimate: D-09 option 2 removes the delimiter and encoding auto-detection, D-19 defers citation metadata, and D-02 removes the hosted work. D-04 option 1 adds about half a day in Stage 2 (the ICC interval and its reference test) but removes a crash, a licence question and most of DA's run time.

---

## Release checklist

### Part A: before every private test candidate (`1.0.0rcN`)

1. `git status` clean. `core/__version__.py` says `1.0.0rcN`, matching the CHANGELOG heading, the About page and the sidebar. The old local `v1.0.0` tag from May has been deleted (first candidate only).
2. CI green on Python 3.12 and 3.14 (Linux) and 3.14 (macOS), installed from the lockfile, with `FREESENSE_REQUIRE_DATA=1` and zero skips (`pytest -rs`).
3. Before/after snapshot (`validation/regression/compare_snapshots.py`) against the previous tagged candidate (against `bcaf9f8` for the first one, rc3): only the changes listed in the CHANGELOG. For rc3 these include the many-to-one contrast and the segmentation `stability` fields.
4. `pip show pingouin` in a fresh install from the lockfile reports "not found", no lock file in `requirements/` names it, and `grep -rn "import pingouin\|from pingouin" --include='*.py' .` (outside `env/`) finds nothing except `validation/regression/freeze_icc_ci_pingouin.py`, the Stage 2 script that records how the frozen ICC reference was made (it runs only in a scratch venv with pingouin 0.7.0, never in the app or CI). Mentions in comments, the methods reference, `tests/test_icc_confidence_interval.py` (the frozen reference) and CHANGELOG are history and stay.
5. Clean-machine install on Linux or macOS: a new venv, `pip install` from the lockfile, `streamlit run app.py`. Walk each module with its bundled example through to export. Open every workbook in Excel and LibreOffice. Check:
   - zero formula cells;
   - `Run_Parameters` shows the candidate version, the date, package versions and the file hash;
   - `Methods_Notes` is present.
6. The bad-file fixture set (Stage 3) run through the app by hand once:
   - `.CSV` files are read correctly;
   - multi-sheet files show the sheet picker;
   - everything else is refused with the re-save instruction;
   - no traceback appears anywhere;
   - the size warning appears on a study with 51 attributes.
7. `.streamlit/config.toml` has `server.address = "localhost"` and `browser.gatherUsageStats = false`. After launch, `ss -ltn` shows the port on 127.0.0.1 only.
8. About page:
   - version, licence summary, disclaimer, "Your data", the "Report a problem" link plus the support email, and the citation are present;
   - no link is broken for an invited collaborator.

   The landing page shows the renamed "Profiling" section and Liking before CATA.
9. The Stage 9A step 4 searches on the release repository return zero hits, including `git ls-files | grep -E '^(working_notes|\.claude|\.agents)/'` printing nothing.
10. The tester pack (`TESTING.md`) matches this candidate.

### Part B: before switching the repository to public (Stage 9C)

1. Every item of part A passes on the final build, versioned `1.0.0` (no `rc`), with the CHANGELOG heading dated.
2. `validation/run_all.sh` passes on a machine with R. Commit any change in `validation/*/reference/*.csv` only after reviewing the diff.
3. Windows best effort: one install and one Word/PowerPoint chart export (kaleido) on Windows. Record the result in the release notes either way.
4. The Stage 9B sign-off criteria are met: no open BLOCKER or HIGH issue.
5. Every issue, comment and attachment has been reviewed for tester data or personal details (Stage 9C step 3).
6. The Stage 9A step 4 searches pass again on the full history, including all testing-phase commits; `working_notes/`, `.claude/` and `.agents/` have never been committed (`git log --all --name-only | grep -E '^(working_notes|\.claude|\.agents)/'` prints nothing). `example_data/COPYING` is present.
7. `docs/open-items.md` lists only post-release items, each with a register ID.
8. After the switch:
   - the GitHub release `v1.0.0` exists on `Sesnor-y/FreeSense`;
   - README's clone command works without credentials;
   - the issues page is reachable without logging in;
   - the in-app "Report a bug" link resolves for an anonymous visitor.
