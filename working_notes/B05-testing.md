# B05 Testing: FreeSense pre-release review

Reviewer: B05 (testing). Commit `bcaf9f8`. Review-only; nothing in the repo was modified apart from this file (the validation emitters rewrote their git-ignored `validation/*/_out/` CSVs when run, which the preamble tolerates).

## Scope and method

Checked: the 31 test files / 366 collected tests, `tests/conftest.py`, `tests/test_validation_pins.py`, all 24 frozen reference CSVs in `validation/*/reference/`, the seven R reference scripts and Python emitters, `requirements.txt`, `pytest.ini`, and the lead's line-coverage report (`scratchpad/coverage.txt`, TOTAL 77%).

Commands run (scratch outputs in `scratchpad/agents/B05/`):

1. **Per-test coverage contexts** (so each function maps to the tests that execute it). I ran this on subsets only, not the full suite in one go:
   - the non-AppTest files: `pytest $(ls tests/test_*.py | grep -v apptest) -n 4 --cov=stats --cov=core --cov=utils --cov-context=test` with `COVERAGE_FILE=.../B05/tests.cov`
   - the AppTest files: same command with `-n 3`, writing `app.cov`
   - each validation emitter under `coverage run --context=validation_pins::<name>`, writing `val.cov`. Emitters run as subprocesses of `test_validation_pins.py`, so the lead's pytest-cov report does not see them. This is why `stats/mdpref.py` shows 12% there even though it is reference-pinned.
2. **Coverage matrix:** `B05/matrix.py` maps every top-level function in `stats/`, `stats/shared/`, `core/data.py` and `utils/export.py` to the tests that execute it. It also labels each test heuristically, from the text of its assertions:
   - `NUM`: asserts a number (approx, isclose, assert_frame_equal, a tolerance, or a numeric literal)
   - `STRUCT`: asserts only shape, keys, strings or flags
   - `REF`: a validation pin
   Output: `B05/matrix_all.txt`. Functions no test ever executes: `B05` function-level listing (reproduced under TEST-06).
3. **Data-dependent tests:** a collection plugin (`B05/fixplug.py`) counted the tests that request an example-data fixture: 94 of 366.
4. **Provenance of the references:** `git log` on each reference CSV, plus a look at how each file is formatted.
5. **How close the pins really are:** the achieved difference for each pinned quantity, compared with the tolerance the test allows (script inline in the evidence below).
6. **Independent checks** of two paths that have no pin:
   - asymptotic McNemar, against scipy and statsmodels
   - DA Type III F on a complete design with unequal replication, against `statsmodels anova_lm(typ=3)` with Sum coding (`B05/t3.py`)

### Coverage matrix (function -> tests; `NUM`/`STRUCT`/`REF` counts are tests executing it)

The ✓ column means a known-answer test exists: an R reference pin, or an independent recomputation inside a test. A pin whose expected value was produced by FreeSense itself does not count.

| Function | Tests | Assertion mix | Known-answer? |
|---|---|---|---|
| **CATA** `shared/frequency.run_cochrans_q` | 9 | NUM 3, STRUCT 5, REF 1 | ✓ (cata::cochranQ, 31 attrs) |
| `run_mcnemar_posthoc` | 5 | NUM 1, STRUCT 3, REF 1 | partial: exact path only (38/465 pairs), see TEST-02 |
| `build_cld_from_mcnemar` | 2 (AppTest) | STRUCT 1, NUM 1 | no |
| `wilson_ci` | 2 (AppTest) | STRUCT | no |
| `proportion_table` | 0 | none | no (unused in production: 0 call sites) |
| `filter_attributes_by_citation`, `build_citation_counts/matrix` | 3-4 | incl. REF | ✓ (indirect via CATA pin) |
| `cata.compute_ca` | 4 | NUM 1, REF 1 | ✓ (FactoMineR::CA) |
| `cata.compute_ca_ellipses` | 2 (AppTest, n_boot monkeypatched to 25) | STRUCT | no |
| `cata.run_cata_contrast` | 2 (AppTest) | STRUCT | no |
| `cata.compute_penalty`, `reassign_penalty_quadrants`, `summarise_liking_overlap` | 2 (AppTest) | STRUCT 1, NUM 1 (thresholds, not statistics) | no |
| **DA** `da_anova.run_da_anova` | 10 | NUM 4, STRUCT 5, REF 1 | ✓ for balanced (aov); ✓ Type II empty-cell (in-test statsmodels); **no** for Type III with unequal replication |
| `da_anova.compute_da_diagnostics` | 2 | STRUCT | no |
| `posthoc.generate_cld` / `generate_pairwise_table` / `resolve_da_error_term` | 18 / 10 / 7 | mostly STRUCT, REF 1 | ✓ (DA CLD partition, RATA paired-t BH + RCBD Tukey) |
| `contrast.compute_contrast` / `cached_compute_contrast` | 10 / 5 | STRUCT 9 / NUM 2 | no (only "adjusted difference < 0.3" on synthetic) |
| `descriptive.*` (3 functions) | 5-7 | incl. REF | ✓ means (DA ref_means) |
| `panel_performance.compute_repeatability` | 6 | incl. REF | ✓ ICC(3,1), 25-cell spot check |
| `panel_performance.compute_discrimination / agreement / scale_usage / pooled_discrimination / summarise_*` | 4-7 | mostly STRUCT; NUM = FreeSense-derived pins on sensochoc | no |
| `panel_performance.assessor_attribute_detail` | 1 (AppTest) | STRUCT | no |
| `multivariate.calculate_pca`, `run_cva`, `calculate_panel_stability`, `incomplete_mean_attributes` | 4 each | **STRUCT only** | no (the DA/RATA PCA is sklearn `PCA` in `calculate_pca`, separate from the PrefMap-pinned `compute_pca_scores`) |
| `multivariate.varimax` | 0 | none | no (reachable from DA and RATA UI) |
| `shared/lsmeans.*` | 2-12 | NUM | ✓ (in-test statsmodels OLS contrast) |
| **RATA** `mixed_models.run_mixed_models` | 7 | NUM 2, STRUCT 4, REF 1 | ✓ (lme4 LRT), but only on sensochoc intensities, never on zero-filled RATA data |
| **Liking** `liking.compute_liking_lmm`, `compute_liking_cld` | 5 / 5 | incl. REF | ✓ (LS means, LRT, CLD, Kendall W) |
| `liking.compute_twoway_anova_demo`, `compute_demographic_overview` | 1 (AppTest) | NUM (wiring) | no (the validation README admits it) |
| `liking.demographic_*`, `acceptance_share`, `filter_sparse_demographic_levels` | 2-3 | NUM (mostly "matches the inline expression" refactor pins) | no |
| `jar_penalty.compute_jar_penalty` | 3 | REF 1 | ✓ (SensoMineR JAR + Welch) |
| `jar_penalty.compute_jar_penalty_long`, `compute_jar_distribution` | 2 (AppTest) | wiring | no |
| `mdpref.compute_preference_map` | 1 | REF only | ✓ (prcomp) |
| `segmentation.compute_kmeans_clusters`, `compute_ahc_clusters`, `recut_clusters` | 2-4 | NUM (ground-truth recovery on synthetic) | partial: recovery of labels, validity indices not checked |
| `segmentation.compute_demographic_association` | 0 | none | no (reachable from Liking step 5) |
| **Fusion** `pls.fit_pls`, `compute_vip`, `compute_correlation_loadings`, `effective_rank`, `hotelling_t2_limit` | 4-8 | incl. REF / closed-form | ✓ (pls::plsr; T² against the F form) |
| `pls.compute_cv_coefficient_stability`, jackknife, permutation | 2 | STRUCT / "p < 0.05" | no |
| `data_fusion.match_samples`, `merge_data_blocks`, `drop_incomplete_attributes`, `autoscale` | 3-5 | mixed | n/a (plumbing) |
| `data_fusion.log_transform`, `sqrt_transform`, `inverse_autoscale` | 0 | none | no (log/sqrt are reachable from the Fusion preprocessing UI) |
| `data_fusion.project_supplementary` | 1 | STRUCT | no |
| **PrefMap** `prefmap.compute_prefmap` | 6 | incl. REF | ✓ (base-R lm AICc) |
| `prefmap.compute_preference_surface` | 2 (AppTest) | wiring | no |
| **core/data** `load_data` | 2 | STRUCT (header dedup, corrupt-file error) | n/a |
| `clean_and_structure_data` | 16 | incl. REF | ✓ indirectly |
| `load_precomputed_means` | **0** | none | every AppTest monkeypatches it |
| `build_cata_liking_long` | 2 (AppTest) | wiring | no |
| **utils/export** `generate_excel_report` (RATA), `generate_da_excel_report`, `build_rata_results_table`, `build_run_parameters_sheet` | 2-12 | NUM (sheet contents vs recorded baseline) | n/a |
| `generate_liking/fusion/prefmap/cata_excel_report` | 1-2 each (AppTest, called directly on a state snapshot) | NUM 1 / STRUCT | n/a; sheet presence and Run_Parameters only |

Totals from the heuristic labels, over the 287 test functions (not the 366 collected tests, which count parametrised cases separately): 133 assert at least one number, 150 only structure or strings, 4 have no bare `assert` (on inspection all 4 use `assert_frame_equal`/`assert_series_equal`, so they are numeric).

## Findings

### TEST-01: The suite protects results only on the maintainer's machine: no CI, no lockfile, one Python version
- Severity: HIGH
- Confidence: VERIFIED (absence); impact SUSPECTED
- Location: repo root (`.github/` absent, no lockfile); `requirements.txt`; `pytest.ini`
- Evidence:
  - `ls .github` returns "No such file". There is no `*.lock`, `constraints.txt` or `pip freeze` output.
  - `requirements.txt` gives floors and major-version caps only: `statsmodels>=0.14.2,<1.0.0`, `scikit-learn>=1.5.0,<2.0.0`, `scipy>=1.13.0,<2.0.0`, `numpy>=2.3.2,<3.0.0`, `pingouin>=0.5.4,<1.0.0`.
  - The only recorded run is on Python 3.14.7 with statsmodels 0.15.0, scikit-learn 1.9.1 and scipy 1.18.1 (00-orientation section 4). The README claims support for Python 3.11 to 3.14.
  - Many numerical pins are version-sensitive:
    - LMM optimiser output: `test_rata_lmm_pin` asserts the sum of LR statistics is `1292.263 ± 1e-3`.
    - KMeans labels and inertia at `random_state=42`.
    - Bootstrap CA ellipses: `default_rng` seeded draws.
    - PLS permutation p-values drawn from `RandomState(seed)`.
    - Excel sheet baselines in `test_export_rata.py` (comment "Recorded from a fresh baseline run").
- Impact:
  - A user who installs today can get library versions nobody has tested against. If a statsmodels or scikit-learn minor release changes an optimiser default, the app's numbers can shift and nothing will notice. Test failures are only seen if the maintainer happens to run pytest locally.
  - The reference pins are the project's main defence of scientific correctness, and they deliver that only when someone runs them.
  - Inferred: the risk is highest for the LMM paths (RATA, Liking), whose statsmodels `MixedLM` fits are the most sensitive to optimiser changes.
- Recommendation:
  1. Add a minimal GitHub Actions workflow: `pip install -r requirements.txt`, then `pytest -n auto -rs`, on the oldest and newest supported Python (3.11 and 3.14).
  2. Add a second job that installs the floor versions (`pip install "statsmodels==0.14.2" "scikit-learn==1.5.0" ...`), or narrow the floors to what was actually tested.
  3. Commit a lockfile or `constraints.txt` from the environment the release is validated in, and tell users to install from it.
- Effort: S (workflow) to M (floor-version job, plus any fixes it surfaces)
- Dependencies: deployment decision (hosted: pin exactly; local install: lockfile plus a supported-range job)

### TEST-02: Nearly half the shipped statistical methods have no known-answer test
- Severity: HIGH
- Confidence: VERIFIED
- Location: coverage matrix above; `validation/README.md` "Not reference-validated (yet)"
- Evidence: every one of these renders results to users and writes them into the Excel export. None has a test that compares against an externally produced number. Their tests either run the function via AppTest and assert only no-exception, wiring or column conventions, or they pin a value FreeSense itself produced:
  - CATA: `run_cata_contrast`, `compute_penalty` (the Welch t machinery is validated only through JAR), `compute_ca_ellipses`, `build_cld_from_mcnemar`, `wilson_ci`.
  - DA/RATA:
    - `multivariate.calculate_pca`, `run_cva`, `calculate_panel_stability`: the matrix labels them "STRUCT only". `calculate_pca` calls sklearn `PCA` directly (`stats/multivariate.py` about line 123); the PrefMap pin covers the separate `compute_pca_scores`.
    - `varimax`: never executed by any test.
    - `contrast.compute_contrast`.
    - Panel-performance discrimination, agreement/RV and scale usage: the sensochoc pins in `test_panel_performance_summary.py` are derived from the current code.
  - DA Type III with unequal replication and no empty cells. The DA pin uses balanced sensochoc, where Type I = II = III, so the Sum-coding Type III path is never distinguished. I checked it by hand (`B05/t3.py`, 8 assessors × 4 products, replication 1 or 3 per cell). FreeSense gives `F_product = 21.246` against the interaction term with df 21. statsmodels `anova_lm(typ=3)` with Sum coding gives MS_Product / MS_Interaction = 21.2455. So it is correct today but unprotected.
  - Liking: `compute_twoway_anova_demo` (the README says it was spot-checked once, but there is no harness), `compute_jar_penalty_long`, `compute_jar_distribution`, and `segmentation.compute_demographic_association` (never executed).
  - PrefMap: `compute_preference_surface`.
  - PLS: jackknife, permutation test and `compute_cv_coefficient_stability`. The only permutation test asserts `p < 0.05` on a synthetic fixture.
  - RATA: the LMM is validated only on DA intensities with no blanks. The RATA-specific zero-filling of unticked cells feeding the LMM is covered only by `test_da_blank_fill.py::test_rata_always_zero_fills`, which checks the fill, not any statistic computed on filled data.
- Impact: these methods could give wrong numbers without any test failing. Several are headline outputs: the DA/RATA PCA and CVA maps, CATA penalty analysis, CATA contrast and panel performance. For a sensory-science audience these figures go into reports.
- Recommendation: add known-answer tests in pure Python where the reference is a closed form or a scipy/statsmodels call, so no R is needed. The priority list is in "Minimum test set" below. For PCA/CVA, reuse the FactoMineR-anchored approach already used for PrefMap.
- Effort: M overall (most tests are S each)
- Dependencies: none

### TEST-03: The CATA McNemar pin checks p-values for only 38 of 465 pairs, and never the adjusted p-values
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `tests/test_validation_pins.py::test_cata_pins` (the `exact = mc[mc["test_used"] == "exact"]` block); `stats/shared/frequency.py:455-485`
- Evidence:
  - In `validation/CATA/_out/fs_mcnemarQ.csv`, 427 pairs use `test_used = asymptotic` and 38 use `exact`. The test compares `p_raw` only for the exact rows. For the asymptotic rows it compares only the discordant counts b and c. No FreeSense `p_adj` or `reject` value is compared against any reference.
  - FreeSense's asymptotic p differs from `cata::mcnemarQ` by up to 0.150, and 11 pairs change significance at 0.05. This is the documented deliberate divergence in `validation/README.md`.
  - My independent check: FreeSense's asymptotic p equals `chi2.sf((b-c)^2/(b+c), 1)` (no continuity correction) to 1.1e-16. It differs from the corrected form and from statsmodels `mcnemar(exact=False, correction=True)` by 0.1496. So the code does what its docstring says (line 456, "no continuity correction").
- Impact: 92% of McNemar p-values in the CATA module are unprotected by any assertion. For example, a regression that switched the correction on, or broke the 25-discordant switch-over, would pass the suite. The CLD letters and BH scope are pinned only by one reject count (`{'A1': 6, 'A5': 0}`) on a synthetic fixture.
- Recommendation: extend `test_cata_pins`:
  - For the asymptotic rows, assert `p_raw` against `scipy.stats.chi2.sf((b-c)**2/(b+c), 1)` computed from the pinned b and c.
  - Recompute BH within each attribute with `statsmodels.stats.multitest.multipletests(method="fdr_bh")` and assert `p_adj` and `reject`.
- Effort: S
- Dependencies: whether the uncorrected χ² is the intended method is a B01 question, not a test question

### TEST-04: Pin tolerances are several orders looser than the agreement achieved, partly because the stats layer rounds test statistics
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `tests/test_validation_pins.py`; `stats/mixed_models.py:119`, `stats/da_anova.py:419-449` (`round(..., 3/4)`); DA ICC (the "FreeSense rounds to 3 dp" comment in `validation/DA/da_reference.R`)
- Evidence: achieved maximum difference against the frozen R references, compared with the tolerance the test allows:

  | Quantity | Achieved | Test tolerance |
  |---|---|---|
  | DA p_product | 1.1e-17 | 1e-3 |
  | DA p_interaction | 3.3e-14 | 1e-3 |
  | DA F | 4.6e-4 (FreeSense rounds F to 3 dp) | 1e-3 |
  | ICC | 4.7e-4 (rounded to 3 dp) | 1e-3 |
  | RATA LR χ² | 4.9e-4 (rounded to 3 dp) | 1e-2 |
  | RATA LR p | 1.0e-12 | 1e-4 |
  | RATA Tukey p_adj | 4.9e-11 | 1e-4 |
  | Liking LRT p | 3.2e-11 | 1e-3 |
  | VIP | 6.5e-5 | 1e-3 |
  | Cochran Q p | 4.6e-8 (the reference is written to 7 dp) | 1e-5 |

  More weak assertions of the same kind:
  - `test_stage_f_smoke.py` pins sums (`sum of F == 414.665`, `sum of LR == 1292.263`), so errors in opposite directions cancel out.
  - `test_fusion_pls_pin` asserts `(status == 'matched').all() or 'status' in columns`, which is always true.
  - Several `test_stats_layer_moves.py` tests compare a function against a copy of the same expression ("matches the inline expression"). These are refactor guards, not correctness tests.
- Impact: an absolute tolerance of 1e-3 on a p-value lets a result move from 0.0495 to 0.0505 and change a significance decision without failing. Rounding test statistics in the stats layer (F, LR, ICC) also means no test can pin them tighter than 5e-4. That is a data-quality choice that belongs to the display layer, the same argument CLAUDE.md already makes for p-values.
- Recommendation:
  1. Tighten p-value tolerances to 1e-8 (DA, RATA, Liking), because they already agree to 1e-11 or better.
  2. Add decision-agreement asserts (`(p_ref < α) == (p_fs < α)`) for DA and Liking.
  3. Stop rounding F, LR and ICC in `stats/`, then tighten those tolerances to 1e-6.
  4. Replace the sum pins with per-attribute pins.
  5. Delete the tautological `or` clause.
- Effort: S (tests); M if the stats-layer rounding is removed (exports and snapshots change)
- Dependencies: B01 (stats-layer rounding)

### TEST-05: The R references are real R output, but several are R re-implementations of FreeSense's own algorithm, and none has been regenerated since July
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `validation/*/reference/*.csv`; `validation/DA/da_reference.R:160-212, 215-258`; `validation/PrefMap/prefmap_reference.R:122-228`; `validation/Fusion/fusion_reference.R:138-156`
- Evidence:
  - **Provenance.** All 24 CSVs have R `write.csv` formatting: quoted headers and strings, 15 significant digits, `NA` for missing. pandas writes unquoted headers and 17 digits. Each file was added once, in `facd712` (CATA) or `46eaec4` (all others), both dated 2026-07-06, and never modified since (`git log -- <file>` shows one commit each). So they are **not** regenerated Python output, and there is no circularity in the literal sense.
  - **Independence varies by quantity.**
    - Independent published engines: `cata::cochranQ`/`mcnemarQ`, `FactoMineR::CA`, base-R `aov` (DA F), `lme4` LRT, `emmeans` Tukey (RATA), `t.test` + `p.adjust`, `pls::plsr` coefficients and fit, `prcomp`, and SensoMineR JAR penalties.
    - **R ports of FreeSense logic:**
      - DA CLD: the frozen `ref_cld.csv` comes from `manual_tk()`, commented as "Manual Tukey-Kramer reproducing FreeSense's algorithm". The independent `emmeans` CLD disagrees on 2 of 14 attributes. That divergence is documented but not frozen.
      - PrefMap: the per-consumer AICc formula and the ">3× product radius" stability override are re-coded in R, fitted on **FreeSense's own PCA coordinates** (`fs_sc`, read from `_out/`), and the frozen `model_type_ref` and `r2_ref` are the override-adjusted values.
      - VIP: hand-coded formula.
      - ICC: hand-coded from `aov` mean squares, 25 randomly sampled cells.
    - These pins confirm that FreeSense's arithmetic matches its specification. They cannot catch a wrong specification.
  - **Staleness.** R is not installed here, and `validation/run_all.sh` has not been run since July as far as git shows. The September changes (`03efed4` unbalanced data handling, `a564616`/`1b43357` panel performance) touched `da_anova`, `posthoc` and `panel_performance`. The pins still pass because sensochoc is balanced and complete, so they never touch the new empty-cell code.
- Impact: the README's "validated against published R engines" is accurate for most headline tests but overstated for DA CLD letters, PrefMap model selection and VIP. Users reading the validation claims may over-trust those outputs.
- Recommendation:
  1. In `validation/README.md`, mark each pinned quantity as "independent engine" or "R port of FreeSense spec".
  2. Freeze the emmeans DA CLD as a second reference and assert the documented 2/14 gap.
  3. Before release, run `validation/run_all.sh` on a machine with R and commit the result (unchanged CSVs are themselves evidence), or record in the release notes the date of the last R run.
- Effort: S (docs and extra asserts); M (R run, if anything moved)
- Dependencies: TEST-01

### TEST-06: Whole user-reachable paths are never executed by any test, including the precomputed-means loader
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `core/data.py:41` (`load_precomputed_means`); functions listed below
- Evidence: after combining the unit, AppTest and emitter coverage contexts, these functions execute on zero lines:
  - `core.data.load_precomputed_means`: every Fusion and PrefMap AppTest replaces it with `_fake_means` (`tests/test_apptest_fusion.py:88`, `tests/test_apptest_prefmap.py:75`).
  - `stats.data_fusion.log_transform`, `sqrt_transform`: Fusion preprocessing options, 3 call sites in `modules/fusion/workflow.py`.
  - `stats.multivariate.varimax`: DA and RATA rotation.
  - `stats.segmentation.compute_demographic_association`: Liking.
  - `stats.liking._failure_return`.
  - Plotters: `plot_consumer_dendrogram`, `plot_cluster_validity_line`, `plot_mdpref_biplot_vectors`, `plot_mdpref_biplot_clusters_ellipses`, `plot_demographic_grouped_bar`, `plot_age_liking_scatter`, `plot_penalty_mean_drop_bar`, `add_cva_assessor_overlay`, `compute_kde_contour_points` (all have production call sites).
  - Dead code: `plot_penalty_bar`, `plot_penalty_bubble` and `stats.shared.frequency.proportion_table` have no production call sites.

  A quick probe of the untested loader: `load_precomputed_means` accepts a CSV with a duplicated product row (`A,3.5,2` / `A,4.0,1`) and returns a non-unique index without warning (`df.index.is_unique == False`). A `;`-separated CSV with decimal commas fails with a misleading "Product column not found. Available columns: product;Sweet;Sour".
- Impact:
  - The Fusion and PrefMap file-upload path, as users run it, has no test at all.
  - Liking segmentation panels and the MDPREF biplots live inside `on_change="rerun"` tabs. The step walk (`assert_render_conventions_across_steps`) never opens those tabs, so a crash there would ship.
- Recommendation:
  1. Unit-test `load_precomputed_means` on real bytes (CSV and XLSX; missing product column; duplicate products; NaN cells; non-numeric column).
  2. Add AppTest cases that open each gated tab (Liking steps 4, 5 and 7; DA/RATA rotation on; Fusion log/sqrt preprocessing).
  3. Delete the three dead functions.
- Effort: S to M
- Dependencies: B03 (duplicate products and delimiter handling are ingestion findings)

### TEST-07: AppTests check wiring and conventions well, but bypass real upload and never check numbers on screen
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `tests/test_apptest_*.py`, `tests/test_apptest_smoke.py:277-305`
- Evidence:
  - **What the AppTests assert:**
    - no exception on each step (every module walks all its steps)
    - persisted widget round-trips across module switch and re-upload
    - that session-state result frames equal a direct stats call (`assert_frame_equal(at.session_state["rata_anova_df"], anova_ref)` in `test_apptest_rata.py:128-133`)
    - Run_Parameters values
    - chart-title and p-value display conventions
    - contrast reference-switch behaviour
  - **What they do not do:**
    - Every module fixture monkeypatches `ui_shell.render_data_upload_section` and `core_data.load_data` (for example `test_apptest_da.py:39-40`), so `st.file_uploader` → `load_data` → column-mapping auto-detection on real bytes is never exercised.
    - Export builders are called directly on a `session_state.to_dict()` snapshot. The deferred `st.download_button(data=callable)` path, which runs on a worker thread with no script context (CLAUDE.md), is not exercised.
    - No AppTest asserts a displayed number (a metric value or a table cell) against a reference.
- Impact:
  - Upload-format regressions would not be caught: header detection, encoding, Excel sheet choice, numeric IDs. These are the most common first-contact failures for users.
  - The worker-thread export path could break (for example if a builder starts reading `st.session_state`) while every test still passes.
- Recommendation: see minimum test set items 6-8.
- Effort: M
- Dependencies: none

### TEST-08: 94 tests (26%) skip without `example_data/`, and the skips are not reported by default
- Severity: LOW
- Confidence: VERIFIED
- Location: `tests/conftest.py::_existing`; `pytest.ini` (`addopts = -q`, no `-rs`)
- Evidence:
  - The collection plugin counted 94 of 366 items that request an example-data fixture. That covers all of `test_apptest_{cata,fusion,prefmap,rata}`, 9/10 DA and 11/12 Liking AppTests, 11/12 panel-performance tests, 8/18 export tests and all 3 stage-F pins.
  - `test_validation_pins.py` (7 tests) would **fail**, not skip, because its emitters `pd.read_excel` the example files.
  - `example_data/` is tracked in git (the `.gitignore` negations), so a normal clone has it.
- Impact: low today. It would matter for a packaged or sdist build that leaves the data out. There, a run would show about 272 passed plus a line of `s` characters, and most numerical pins would be silently absent.
- Recommendation: add `-rs` to `addopts`. In CI, set an env var such as `FREESENSE_REQUIRE_DATA=1` that turns `_existing`'s skip into a failure.
- Effort: S
- Dependencies: TEST-01

## Checked, nothing material found

- **Flakiness from randomness:**
  - Every test RNG uses an explicitly seeded `np.random.default_rng(seed)` (conftest lines 86, 147, 196, 231, 263; `test_pls.py`, `test_stats_layer_moves.py`).
  - Production RNG is seeded too: `multivariate.py:296`, `cata.py:679`, `segmentation.py` `random_state=42`, `pls.py:453,601`.
  - No `time`, `datetime` or `sleep` in tests.
  - Remaining risks: version drift (TEST-01), and AppTest `timeout=300` on a loaded machine. The latter was not observed to fail; the xdist run passed.
- **Circularity of the frozen CSVs:** not regenerated from Python (TEST-05 has the formatting and git evidence).
- **Asymptotic McNemar correctness:** matches the documented formula exactly (TEST-03).
- **DA Type III, unequal replication:** matches statsmodels to rounding (TEST-02).
- **Empty-cell (Type II) path and LS means:** `test_unbalanced_designs.py` recomputes both independently with statsmodels (`test_anova_with_empty_cells_uses_the_additive_model`, `test_lsmean_contrast_matches_statsmodels`). These are good known-answer tests.
- **Parameter wiring in AppTests:** `test_run_analysis_uses_widget_parameters` (RATA, DA, CATA, Liking, Fusion) compares stored frames against direct stats calls with the widget values. This is solid.
- **Cross-test state leakage:** session-scoped fixtures return frames that tests treat as read-only. No mutation of them was spotted, but I did not audit this exhaustively.

## Minimum test set required before release (prioritised)

| # | Test | Asserts | Data | Effort |
|---|---|---|---|---|
| 1 | CI workflow `pytest -n auto -rs` on py3.11 + py3.14, plus a floor-versions job; commit `constraints.txt` | whole suite green on supported range | repo | S-M |
| 2 | `test_cata_pins` extension | asymptotic `p_raw` = `chi2.sf((b-c)²/(b+c),1)`; within-attribute BH `p_adj`/`reject` = `multipletests` | bread (existing emitter) | S |
| 3 | `test_validation_pins` tightening | p tolerances 1e-8; decision agreement for DA/Liking; per-attribute not summed pins | existing | S |
| 4 | `test_da_type3_unequal_replication` | `F_product`, `p_product`, `tested_against` equal `anova_lm(typ=3, Sum)` MS ratios (conditional pooling both branches) | synthetic (`B05/t3.py` pattern) | S |
| 5 | `test_calculate_pca_matches_svd` / `test_run_cva_matches_reference` | eigenvalues, scores up to sign vs `numpy.linalg.svd` of the standardised means; CVA eigenvalues vs a hand `scipy.linalg.eigh(B, W)` | sensochoc means | S-M |
| 6 | `test_load_precomputed_means_*` (real bytes) | CSV/XLSX parse; missing product col error; duplicate product rows rejected or flagged; NaN report | synthetic bytes | S |
| 7 | `test_upload_end_to_end_<module>` (one per module, no `load_data` monkeypatch) | real `UploadedFile` via `at.session_state` / file-uploader injection → auto-mapping → Run → `analysis_complete` | each example file | M |
| 8 | `test_export_download_callable_without_script_context` (per module) | call the exact lambda passed to `render_export_section` on a worker thread; workbook opens, sheet list matches `get_*_export_sheet_list`, Run_Parameters alpha/scale equal widget values | example data | M |
| 9 | `test_cata_penalty_known_answer` | mean drops and Welch p for 2-3 attributes vs `scipy.stats.ttest_ind(equal_var=False)` on the collapsed groups; BH scope within step | bread + companion liking | S |
| 10 | `test_cata_contrast_known_answer` | per-attribute McNemar vs reference product and within-product BH, recomputed with statsmodels | bread | S |
| 11 | `test_rata_zero_fill_lmm` | on a small synthetic RATA frame with blanks, LRT χ² equals a hand statsmodels `MixedLM` ML fit on the zero-filled data | synthetic | S |
| 12 | `test_gated_panels_render` (AppTest) | open every `on_change="rerun"` tab/expander in Liking 4/5/7, DA/RATA varimax on, Fusion log/sqrt; no exception | example data | M |
| 13 | `test_panel_performance_known_answer` | discrimination F per assessor = one-way ANOVA via `scipy.stats.f_oneway`; agreement r = `pearsonr` vs leave-one-out consensus | sensochoc subset | S |
| 14 | Re-run `validation/run_all.sh` with R, commit result | all R `check()` pass; CSVs unchanged or diff reviewed | example data | M (needs R) |

Items 1-8 are the release floor; 9-14 are strongly recommended.

## Decisions raised

- **Supported platform matrix:** which Python versions and dependency ranges are promised? This determines the CI matrix, and whether floors must be tested or narrowed (TEST-01).
- **Deployment:**
  - Hosted: pin exact versions and test that environment.
  - Local install: ship a lockfile or constraints file, and test the declared range.
- **Beta modules:** if Fusion and PrefMap ship, their loader (TEST-06) and export path need items 6-8. If they are held back, those items can drop to Liking, CATA, DA and RATA only.
- **Validation claims:** how strongly should the README and About page claim "validated against R", given TEST-05 (some pins are R ports of the spec) and that R has not been re-run since July?

## Leads for other areas

- B01:
  - `stats/mixed_models.py:119` and `stats/da_anova.py:419-449` round LR, F, SS, MS and ICC in the stats layer. This is the same anti-pattern CLAUDE.md bans for p-values.
  - VIP differs from the R formula by 6.5e-5 while PLS coefficients agree to about 4e-8. This may be a small formula difference (SSY weighting); worth a look.
  - Uncorrected asymptotic McNemar vs `cata::mcnemarQ` changes the decision on 11/465 pairs on the bread data.
- B03:
  - `load_precomputed_means` silently accepts duplicate product rows (non-unique index).
  - It gives a misleading "column not found" error for `;`-delimited CSVs.
- B06: `plot_penalty_bar`, `plot_penalty_bubble` (`utils/plotting.py:2377, 2478`) and `proportion_table` (`stats/shared/frequency.py:289`) are dead code.
- B06: the test run emits a pandas FutureWarning at `stats/panel_performance.py:138` and a SingularMatrixWarning at `stats/da_anova.py:526`. These would become failures under `-W error`.
