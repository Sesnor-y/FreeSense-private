# B04 Code quality and architecture

Reviewer: B04 (lead-dev lens). Commit `bcaf9f8`. Review only; no application code changed.
Scratch scripts: `/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B04/`.

## Scope and method

What was checked, and how:

- **Rerun model / recomputation.** `scripts/streamlit_review_counts.sh` (read-only metric script) plus an AST scan of every `with st.expander(...)` block in production code that is not gated by `on_change="rerun"`, looking for calls to `render_chart`, `plot_*`, `compute_*`, `build_*`, `run_*`, `fit_*`, `go.Figure`, `make_subplots` inside the body. Checked all `@st.cache_data` sites for `max_entries` and for `st.*` / session-state use inside cached functions. Listed every `st.rerun()` site.
- **Session-state leaks.** Wrote `keys.py` (AST): collects every constant key written to `st.session_state` via subscript assignment, attribute assignment, local aliases (`ss = st.session_state`), `.setdefault` and `.update({...})` across `app.py`, `core/`, `modules/`, `utils/`, and compares with `MODULE_STATE_KEYS`, widget `key=` values and the global keys seeded by `init_session`. Read the existing guard `tests/test_state.py::test_every_storage_key_a_module_writes_is_listed` to see what it misses.
- **Layer separation.** grep/AST for `scipy`, `statsmodels`, `sklearn`, `np.linalg`, `np.cov`, `ppf`, `percentile` in `modules/` and `utils/`; read `tests/test_stats_layer_moves.py`.
- **Dead code / deps.** `vulture` (installed to scratch) over `app.py core modules stats utils` at 60 % confidence; cross-checked each hit with grep over `tests/` and `validation/`. Compared `requirements.txt` against imports.
- **Error handling.** Every `except Exception` / bare `except` in production code (34 sites), each read in context. All `warnings.warn` sites in `stats/` and whether any caller captures them. `logging` configuration in `app.py` and every logger call.
- **Lint.** ruff (scratch binary) with the repo `pyproject.toml`: statistics per rule, per file; E712 and F811 read individually; ran the E712 unsafe fix on a scratch copy of `stats/prefmap.py`; ran the normally-ignored F841 plus B023/B018 to look for hidden bugs.
- **File size.** AST function-length census; import time of the four largest modules; statement coverage from the lead's run (`scratchpad/coverage.txt`).
- **Duplication.** `difflib` similarity of the four contrast-step renderers; grep for repeated ellipse, ideal-point and post-hoc-label logic.

Headless experiments (commands and output are quoted in the findings): `conv.py` (Liking LMM convergence flag), `runparams.py` (Run_Parameters data source), a direct call of `utils.plotting.plot_spider_with_ribbon` with each Tukey label.

## Findings

### CODE-01: Liking's Tukey label is not recognised by the spider plot, so an HSD ribbon is captioned "±LSD zone"
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `utils/plotting.py:1219-1220` and `1267-1272` (`plot_spider_with_ribbon`); label defined at `modules/liking/workflow.py:52-54` (`"Tukey HSD (Studentized Range)"`); consumed at `modules/liking/ui.py:1279-1292`; root cause is three labels for one method: `modules/rata/ui.py:50` (`"Tukey HSD"`), `modules/descriptive/workflow.py:2496` (`"Tukey-Kramer HSD"`), Liking (`"Tukey HSD (Studentized Range)"`).
- Evidence: `stats/contrast.py:181-183` accepts all three labels and sets `use_hsd=True`, so for Liking the ribbon half-width is the HSD. The plotter only tests `post_hoc_method in ('Tukey HSD', 'Tukey-Kramer HSD')`. Direct call:
  ```
  'Tukey HSD'                     ['±HSD zone'] | Shaded ribbon = ±HSD zone
  'Tukey-Kramer HSD'              ['±HSD zone'] | Shaded ribbon = ±HSD zone
  'Tukey HSD (Studentized Range)' ['±LSD zone'] | Shaded ribbon = ±LSD zone
  ```
  The alias tuple is restated at about nine sites (`stats/posthoc.py:337, 594, 642, 691, 762`, `stats/contrast.py:182`, `utils/plotting.py:1219, 1267`, `modules/descriptive/workflow.py:1013`); the plotting ones are the two that missed the third label.
- Impact: Liking users who choose Tukey get a chart (on screen and in the Word/PowerPoint export) whose legend and subtitle call the band an LSD zone. The numbers are right, the label is wrong. Any future site that copies one of the two-label tuples will repeat the bug.
- Recommendation: define the labels once in `core/config.py` (e.g. `TUKEY_LABELS = frozenset({...})` and `is_tukey(method)`), replace the nine tuples with it, and add a test that calls `plot_spider_with_ribbon` with every module's option list. Unifying the visible labels is a UX choice and can wait; the helper is the release fix.
- Effort: S
- Dependencies: none

### CODE-02: Global `uploaded_file` key leaks between modules and puts the wrong file name in Fusion/PrefMap `Run_Parameters`
- Severity: MEDIUM
- Confidence: VERIFIED for Fusion and PrefMap; SUSPECTED for CATA/DA/RATA after a module round-trip
- Location: writes at `modules/cata/ui.py:379`, `modules/descriptive/workflow.py:114`, `modules/rata/ui.py:113`; read at `utils/export.py:366-373` (`build_run_parameters_sheet`); not in `init_session`, not in `MODULE_STATE_KEYS`.
- Evidence: `keys.py` found `uploaded_file` as the only non-global, non-listed key written by more than one module. Fusion and PrefMap never write `uploaded_file`, `fusion_df_raw_name` or `prefmap_df_raw_name` (grep), so the builder falls back to whatever CATA/DA/RATA last stored. `runparams.py` with state `{'uploaded_file': <name 'panel_DA_2025.csv'>}`:
  ```
  Fusion  [['data_source_file', 'panel_DA_2025.csv', 'fusion_df_raw_name / uploaded_file']]
  PrefMap [['data_source_file', 'panel_DA_2025.csv', 'prefmap_df_raw_name / uploaded_file']]
  ```
  Inferred (not run end to end): for CATA/DA/RATA the key is rewritten on every Step 1 render from an uploader that has no `persist_state`, so after visiting another module and coming back (results are restored by `_select_module`) it holds `None` or another module's file.
- Impact: the provenance sheet, whose purpose is to document which file produced the results, names a different module's file. A reader of an archived Fusion or PrefMap workbook would be misled.
- Recommendation: each module records its own `<prefix>_df_raw_name` (storage key, listed in `MODULE_STATE_KEYS`) at "Run analysis" time, as Liking already does (`modules/liking/workflow.py:325`); Fusion records both sensory and external file names; the builder drops the `uploaded_file` fallback and writes "—" when a module has no record. Remove the three `uploaded_file` writes. Add a `Run_Parameters` test per module that seeds a foreign `uploaded_file` and asserts it is not reported.
- Effort: S
- Dependencies: none

### CODE-03: Liking LMM never raises its convergence warning on a successful fit; optimiser fallback and boundary fits are silent
- Severity: MEDIUM
- Confidence: VERIFIED (code path and one demonstrated case); SUSPECTED for real-data frequency
- Location: `stats/liking.py:227-253` (`compute_liking_lmm`), flag read at `modules/liking/workflow.py:1021`.
- Evidence: `convergence_warning = False` at line 227 is never set to `True` except in `_failure_return()` (all three optimisers raised). The fits run under `warnings.simplefilter('ignore')`, `result_reml.converged` is never read, and the optimiser actually used (`_successful_method`, which can be `cg` or `nm` after `lbfgs` raised) is not returned. Compare `stats/mixed_models.py` (RATA), which returns `converged` and `optimiser_used` per attribute. `conv.py` found synthetic designs (12 consumers × 4 products, small consumer variance) where statsmodels emits `ConvergenceWarning: The MLE may be on the boundary of the parameter space` and `SingularMatrixWarning`, and FreeSense returns `convergence_warning=False`, e.g. seed 11: `statsmodels converged= True ['ConvergenceWarning','SingularMatrixWarning'] -> FreeSense convergence_warning= False [['LRT', 3.15e-07]]`. I did not find a case with `converged=False` in 60 seeds.
- Impact: the "Model convergence warning" in Step 2 is effectively dead code. A boundary or non-converged fit is reported with no caveat. For the fixed-effect product test a boundary random-effect variance is usually benign, so results are not shown to be wrong; the defect is that the safety net the UI advertises does not exist.
- Recommendation: record warnings with `catch_warnings(record=True)` instead of ignoring them; set `convergence_warning` from `not result_reml.converged or not result_ml.converged` or a recorded `ConvergenceWarning`; return `optimiser_used` and a `boundary_fit` flag; surface them as a caption, and add them to `Run_Parameters`. Hand to B01/B02 for the wording of the boundary case.
- Effort: S
- Dependencies: none

### CODE-04: Stats-layer warnings reach only the terminal; the Fusion permutation caption reports the requested, not the used, permutation count
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `stats/pls.py:470-486` (`_permutation_test`), `stats/pls.py:964` (`n_finite_permutations` returned), `modules/fusion/workflow.py:1818-1825` (caption); other `warnings.warn` sites `stats/pls.py:120, 359`, `stats/data_fusion.py:565, 601`, `stats/da_anova.py:532`; `app.py:21-24` (logging to terminal).
- Evidence: no module wraps a stats call in `warnings.catch_warnings(record=True)` (grep returns nothing), so `warnings.warn` messages go to the server's stderr. The permutation test excludes non-finite Q² draws and warns "The reported p-value is conditional on the finite draws"; the result dict carries `n_finite_permutations` "so the UI can" show it (`stats/pls.py:450`), but grep finds no reader in `modules/` or `utils/`, and the caption prints `int(config['n_permutations'])`. Because every stats function is `@st.cache_data`, a warning fires only on a cache miss, so even a terminal user sees it once. Some PLS messages are surfaced independently through result flags (`n_components_rank_capped`, `n_components_effective_rank_capped`, `modules/fusion/workflow.py:2313-2319`), which is the right pattern; the permutation count and the DA diagnostics skip (`stats/da_anova.py:532`) are not.
- Impact: Fusion (beta) users can receive a permutation p-value computed on fewer draws than stated. In a hosted deployment the operator sees the terminal and the user does not.
- Recommendation: before release, show `n_finite_permutations of n_permutations_requested` in the caption and export when they differ. As a rule for `stats/`: anything the user must know goes into the result dict (as the rank-cap flags do), not only into `warnings.warn`.
- Effort: S
- Dependencies: Decision D1 (beta modules in scope)

### CODE-05: A few broad `except Exception` blocks silently drop a result in UI paths
- Severity: LOW
- Confidence: VERIFIED (code); impact SUSPECTED
- Location: `modules/liking/workflow.py:3092-3101` (PREFMAP fit in Step 7: `except Exception: pop('liking_prefmap_results')`, no message, no log); `utils/plotting.py:3074-3075` and `modules/liking/ui.py:450-451` (`except Exception: pass`); `utils/plotting.py:2935-2936` (KDE contour returns `None`).
- Evidence: 34 broad handlers in production code were read. Most are acceptable: file loaders re-raise as `ValueError` with the message (`core/data.py:22, 91`) or show `st.error`; `stats/` per-attribute handlers convert a failure into a NaN row with a `status`/`test` column (`stats/da_anova.py:460`, `stats/shared/frequency.py:105`, `stats/cata.py:1353`); `stats/liking.py:341-356` falls back to Wald and labels it in the `test` column; Fusion's PLS fit clears state and shows `st.error` (`modules/fusion/workflow.py:2338`); Liking's segmentation view logs with `_logger.exception` and shows a sanitised error (`:1993`). Streamlit's `RerunException`/`StopException` derive from `BaseException` (`streamlit/runtime/scriptrunner_utils/exceptions.py:22`), so none of these swallow `st.rerun()`/`st.stop()`. The four listed sites are the exceptions: the Liking PREFMAP failure removes the ideal-point markers and surface options with no explanation.
- Impact: a failure looks like a missing feature rather than an error. No wrong numbers are produced.
- Recommendation: in the Liking PREFMAP handler, `_logger.exception(...)` plus a one-line `st.caption` saying the per-consumer models could not be fitted. Leave the drawing-only `pass` blocks, but log at debug as `modules/prefmap/ui.py:229` does.
- Effort: S
- Dependencies: none

### CODE-06: Lint backlog is cosmetic, but E712 must not be auto-fixed, and the project claims no linter is configured
- Severity: LOW
- Confidence: VERIFIED
- Location: repo-wide; `pyproject.toml [tool.ruff]`; `CLAUDE.md` ("No linter is configured").
- Evidence: `ruff check . --exclude env --statistics`: 226 findings (I001 75, F401 35, E701 34, E702 32, W293 23, E712 18, W292 4, E401 2, F541 1, F811 1, W291 1); 183 in production dirs. By file, E701/E702/I001/W293 cluster in `utils/export.py` (32), `modules/rata/ui.py` (24), `utils/plotting.py` (19).
  - **E712 (18):** every hit compares a pandas Series (`ideal_point_external`, `out_of_spec`, `converged`, `numerical_warning`). `ideal_point_external` holds `True/False/NaN` (`stats/prefmap.py:161, 184, 289`), so `== True` is the correct, NaN-safe test. `ruff --unsafe-fixes` rewrites `(s == False).sum()` to `(not s).sum()` (checked on a scratch copy of `stats/prefmap.py`), which raises `ValueError: The truth value of a Series is ambiguous`. Plain `ruff --fix` leaves E712 alone.
  - **F811 (1):** `modules/descriptive/ui.py:92`: a local list named `warnings` shadows an unused module-level `import warnings` (line 15). The function never calls the `warnings` module. No bug.
  - **F401 (35):** unused imports, 9 in `modules/descriptive/ui.py`; `core/config.py:9` imports `__version__` as `VERSION`, which ruff flags only for the unused `numpy` beside it. No F401 is a re-export that tests rely on (grep of `tests/`).
  - **F841 (ignored by config), run separately:** 21 unused locals; all read, none hides a bug (for example `modules/prefmap/workflow.py:1268` `n_degenerate` is computed but not displayed). B023 at `modules/fusion/workflow.py:817-820` is a false positive (the closure is called in the same iteration).
- Impact: none on results. The risk is a well-meaning pre-release "lint clean-up" using `--unsafe-fixes`, which would break PREFMAP counts and the RATA convergence banner.
- Recommendation: do not run a lint clean-up before release. Afterwards: `ruff check --fix` (safe fixes only) and a test run; add `"E712"` to `ignore` with a comment ("pandas Series comparisons are NaN-aware"), or rewrite as `.eq(True)`; add ruff to dev requirements; correct the CLAUDE.md sentence.
- Effort: S
- Dependencies: none

### CODE-07: Parallel copies of the contrast step, ideal-point overlay and confidence ellipse
- Severity: LOW
- Confidence: VERIFIED
- Location: contrast renderers `modules/rata/ui.py` `render_contrast_step` (313 lines), `modules/descriptive/workflow.py` `render_contrast_step` (320), `modules/liking/ui.py` `render_contrast_step` (329), `modules/cata/ui.py` `render_step_5` (371). Ideal-point markers and model counts: `modules/prefmap/workflow.py:1233-1270` and `1591-1600` ("mirrors Step 2"), `modules/liking/workflow.py:3312-3320, 3370-3380`, and the counts again in `stats/prefmap.py:299-306`. Ellipses: `stats/cata.py:713` `_fit_confidence_ellipse`, `utils/plotting.py:301` `_ellipse_points`, `utils/plotting.py:2849` `compute_ellipse_points` (hard-codes 0.95 although `core/config.DEFAULT_ELLIPSE_CONFIDENCE` exists for exactly these overlays); the cluster-boundary block (ellipse/KDE fallback) is duplicated in `utils/plotting.py:3057-3075` and `modules/prefmap/ui.py:210-235`.
- Evidence: `difflib.SequenceMatcher` on stripped lines, RATA vs DA contrast renderer: 0.81 similarity. CODE-01 is a concrete case of this duplication drifting.
- Impact: maintenance cost and divergence risk. There is no present defect beyond CODE-01.
- Recommendation: after release, extract a shared contrast-step renderer parameterised by module config, a single `add_ideal_point_markers(fig, consumer_results, show_external)` helper, and route all 2-D χ² ellipses through one `stats/` function that takes the confidence. Do not do this before release.
- Effort: M
- Dependencies: none

### CODE-08: About 380 lines of dead functions and two obsolete scipy version probes
- Severity: LOW
- Confidence: VERIFIED
- Location: `utils/plotting.py:2377` `plot_penalty_bar` (99 lines), `:2478` `plot_penalty_bubble` (108); `modules/fusion/ui.py:336` `plot_q2_rmsecv` (78), `:420` `plot_correlation_loadings` (69); `stats/shared/frequency.py:289` `proportion_table` (21); `stats/data_fusion.py:611` `inverse_autoscale` (5). Probes: `modules/rata/ui.py:790-797`, `modules/descriptive/workflow.py:1013-1019`.
- Evidence: vulture at 60 % reported these; none is referenced in `app.py`, `core/`, `modules/`, `utils/`, `tests/` or `validation/` (grep). The other vulture hits (`render_*_module`) are false positives, resolved by string through `MODULES[...]["render"]`. The probes guard against scipy < 1.7, but `requirements.txt` pins `scipy>=1.13.0`. Every package in `requirements.txt` is imported by production code (matplotlib at one site, `utils/plotting.py:2894`; kaleido indirectly).
- Impact: none at runtime; it inflates the largest file and the coverage denominator.
- Recommendation: delete after release.
- Effort: S
- Dependencies: none

### CODE-09: Layer-rule test covers one file; a few statistics still live in `modules/` and `utils/`
- Severity: LOW
- Confidence: VERIFIED
- Location: `tests/test_stats_layer_moves.py:302-338` (scans only `modules/fusion/ui.py`); `modules/fusion/ui.py:588, 604` (Q-residual and leverage limits as `np.percentile(..., 95)` of the plotted products); `utils/plotting.py:327, 336` (Hotelling F / χ² ellipse quantiles), `:2341` (`stats.linregress` trend line), `:2849-2936` (χ² ellipse and KDE contour); `modules/liking/ui.py:436` (`np.polyfit`).
- Evidence: grep and reading. The `stats/` side is clean: no `st.*` other than the decorator, no session-state access, every cache bounded (`@st.cache_data without max_entries: 0 / 44`).
- Impact: small. The two Fusion control limits are statistical decisions made in the UI layer, outside the "only place" rule CLAUDE.md sets for the T² limit (F6), and they are untested.
- Recommendation: extend the AST scan to every file under `modules/` (allow `scipy.cluster.hierarchy.dendrogram` as a drawing helper). Move the Q/leverage limits next to `stats.pls.hotelling_t2_limit` when their method is reviewed (lead for B01).
- Effort: S
- Dependencies: none

### CODE-10: Pandas `DataFrameGroupBy.apply` FutureWarning in panel performance
- Severity: LOW
- Confidence: VERIFIED
- Location: `stats/panel_performance.py:138`
- Evidence: `_rank_column` reads only `neg_log_p` and `range_score`, so `include_groups=False` would give identical output. `requirements.txt` caps `pandas<3.0.0`, so the behaviour change cannot arrive through a normal install.
- Impact: noise in test output; a future pandas 3 upgrade would need it.
- Recommendation: add `include_groups=False` when pandas 3 is adopted.
- Effort: S
- Dependencies: none

## Checked, nothing material found

- **Figures in closed tabs/expanders:** all 11 `st.tabs` are gated (`on_change="rerun"`). The AST scan of the 114 ungated `with st.expander(...)` blocks found none whose body calls a plot, compute, build or `render_chart` function; the 7 heavy ones are gated.
- **Caching:** 44/44 production `@st.cache_data` have `max_entries` (8 in `stats/`, 4 in loaders, 2 in `utils/docs.py`); no cached function calls `st.error/warning/info/...` or touches session state. `stats/jar_penalty.py` is deliberately uncached (documented at line 23). Hashing cost of large frames is not material at sensory data sizes (cached arguments are long frames of about 10^4 to 10^5 rows).
- **`st.rerun()`:** 4 code sites (`modules/rata/ui.py:447`, `modules/descriptive/workflow.py:420`, `modules/cata/ui.py:1060, 1240`), all after a script-body computation with a justifying comment. Navigation and module switching are `on_click` callbacks.
- **`analysis_complete`:** written only inside `core/state.py` (lines 269, 299).
- **`MODULE_STATE_KEYS` coverage:** apart from `uploaded_file` (CODE-02), every constant storage key written in `app.py`, `core/`, `modules/`, `utils/` (including alias, `setdefault` and `update` writes the existing test does not parse) is listed, is a widget key, is a seeded global, or is a documented exception (`fusion_preprocessing`, `_pingouin_notice_shown`, `_scroll_to_top`, `PLOTLY_CONFIG`). Dynamic keys (`f'{sig_only_key}_prev'`, Fusion `_clear_results`, `st.session_state.update(results)` in DA) were read; all are module-prefixed and listed.
- **`.get(key, default)` on statistical parameters:** the remaining numeric-default `.get`s on slider keys (`liking_k_ahc`, `liking_k_kmeans`, `liking_penalty_threshold`, `cata_penalty_drop_threshold`, `fusion_pls_biplot_vip_threshold`) are pre-instantiation clamps, not substitutes for a missing user value.
- **Uncaught pipeline errors:** RATA/DA "Run analysis" does not catch exceptions; they reach Streamlit's error box. Results are written with one `session_state.update` after the pipeline returns, so a failure cannot leave half a result set.
- **Dependencies:** no unused runtime dependency.
- **F811:** benign (see CODE-06).
- **File size as a release risk:** import times of the largest modules are 0.4 to 0.7 s and modules load lazily, so there is no runtime cost. 31 functions exceed 300 lines (largest: `modules/fusion/workflow.py:1407 render_step_3`, 748 lines; `modules/prefmap/workflow.py:759 render_step_2`, 720; `modules/cata/ui.py:360 render_step_1`, 706). Size is a maintenance cost, not a release risk in itself. The release-relevant signal is coverage, which is lowest exactly in the large files: `utils/plotting.py` 61 %, `modules/prefmap/workflow.py` 65 %, `modules/liking/ui.py` 66 %, `modules/liking/workflow.py` 67 %, `modules/fusion/workflow.py` 75 % (statement coverage from the lead's run). Splitting files before release would add risk without reducing it.

### Structural changes that reduce release risk (do before release)
1. One Tukey-label helper in `core/config.py` used by every site (CODE-01). Small and mechanical, with a test.
2. Per-module data-source records and removal of the global `uploaded_file` fallback (CODE-02).
3. Put the user-relevant stats warnings into result dicts and captions: Liking LMM convergence/optimiser/boundary (CODE-03), Fusion finite-permutation count (CODE-04).

Everything else (CODE-05 to CODE-10: dedup, dead code, lint, file splits, layer-test widening) is post-release work. Refactoring the large renderers now would touch the least-tested code.

## Decisions raised

- **D1 Beta modules in scope?** CODE-04 matters only if Fusion ships; if it ships as beta, the permutation-count fix is still cheap.
- **D2 Local vs hosted deployment.** Local: terminal logging and Streamlit's full traceback box (`client.showErrorDetails` resolves to `full`, since `.streamlit/config.toml` does not set it) are adequate, and the user sees both. Hosted: users see neither the log nor stats `warnings.warn`, and tracebacks expose server paths. The priority of CODE-04/CODE-05 and a `showErrorDetails` setting depend on this.
- **D3 Enforce ruff?** Whether ruff (with E712 ignored) becomes a CI or pre-commit gate. There is no CI today.
- **D4 One visible post-hoc vocabulary.** Whether the three Tukey labels are unified in the UI (UX/docs choice), beyond the internal helper in CODE-01.

## Leads for other areas

- B09/docs: CLAUDE.md says `reset_analysis_state()` "clears only the active module's keys on module switch" (also the header comment in `core/state.py:5-6`); it is not called on switch (`utils/ui_shell._select_module` restores results by design). Documentation drift.
- B09/docs: CLAUDE.md "No linter is configured" is false (`pyproject.toml [tool.ruff]`).
- B01: Fusion Step 4 Q-residual and leverage "control limits" are the empirical 95th percentile of the n plotted products (`modules/fusion/ui.py:588, 604`), so by construction about 5 % of products (at least the maximum when n < 20) sit on or above the line. Check this is intended.
- B01/B02: Liking LMM runs under `warnings.simplefilter('ignore')` and the Wald fallback triggers when the LRT is exactly 0.0 (`stats/liking.py:347`), which also fires on a genuinely null effect. Probably harmless; worth a look.
- B07: `client.showErrorDetails` resolves to `full`; in a hosted deployment uncaught exceptions show tracebacks with server paths.
- B05/UX: the Liking contrast "spider" is drawn with a single axis (`attribute='liking'`, `modules/liking/ui.py:1273-1277`); a one-axis radar is an odd chart.
- B06: the pandas FutureWarning (CODE-10) is noise only while `pandas<3` holds.
