# 00 Orientation: FreeSense pre-release review

Review date: 2026-09-26. Reviewer: Claude (lead reviewer), read-only session.
Commit reviewed: `bcaf9f8` on `main` (in sync with `origin/main`; only `working_notes/` untracked).

## Flags on the release context (read first)

1. **Section 0 of the review prompt was not filled in.** Every context field (version, release type, audience, deployment, licence/IP, platforms, date, scope, prior work) is therefore treated as an open decision and carried into `02-decisions.md`. Nothing below assumes an answer.
2. **The prompt assumes an R/Shiny package. The app is Python/Streamlit.** Observed: no `DESCRIPTION`, `NAMESPACE` or `R/`; `app.py` is a Streamlit entry point; `requirements.txt` lists Python packages. R appears only in `validation/*.R` (reference scripts). All R-specific checks in the prompt are mapped to Python equivalents in this review:

   | Prompt asks for | Used here instead |
   |---|---|
   | `R CMD check --as-cran` | No package build exists. Replaced by: pytest, `ruff check` against the repo's own `pyproject.toml` rule set, import check of every module, dependency/licence audit |
   | `devtools::test()` | `python -m pytest tests/` |
   | `covr::package_coverage()` | `coverage` via `pytest-cov` (installed to the session scratchpad, not the project venv) |
   | `lintr` | `ruff` (config already in `pyproject.toml`) |
   | `shinytest2` | Streamlit `AppTest` (already used by the `tests/test_apptest_*.py` files) |
   | `roxygen2` | Python docstrings |
   | `DESCRIPTION` / `NEWS.md` / `renv` | `requirements.txt`, `pyproject.toml`, `CHANGELOG.md`, `core/__version__.py`; there is no lockfile |
3. **R is not installed on this machine** (`which R Rscript` returns nothing). `validation/run_all.sh` cannot run its R half here. The Python half is exercised through `tests/test_validation_pins.py`, which compares production output against R reference numbers frozen in `validation/*/reference/*.csv`. The frozen numbers themselves could not be regenerated in this session.
4. **Version state is ambiguous.** Observed: `core/__version__.py` says `1.0.0`; a local tag `v1.0.0` exists on `a4c3eb2` (2026-05-18) (correction from B08: it is not on `origin`, authenticated `git ls-remote` shows no tags; the GitHub repo is private); `HEAD` is 146 commits later; `CHANGELOG.md` has three headings, `[Unreleased]`, `[1.1.0] — Unreleased` and `[1.0.0] — Unreleased`. Inferred: the code on `main` today differs materially from the tagged `v1.0.0` but still reports itself (in the About page and in every export's `Run_Parameters` sheet) as `1.0.0`. Whether this is the "first release" or a follow-up is a decision.
5. **Two modules are self-declared beta** (`core/config.py` `MODULES["Fusion"|"PrefMap"]["status"] = "beta"`, commit `bcaf9f8`). Whether beta modules ship in this release is a scope decision.

## 1. Technology stack and repository structure

- **Language/runtime:** Python. Venv at `env/` runs Python 3.14.7. README states "Python 3.11 to 3.14"; `pyproject.toml` `[tool.ruff] target-version = "py310"`. No CI tests any version other than whatever the developer runs locally.
- **UI framework:** Streamlit 1.64.0 (floor pinned `>=1.64.0,<2`).
- **Stats stack:** pandas 2.3.3, numpy 2.5.3, scipy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.1, pingouin 0.6.1 (optional), rapidfuzz.
- **Plots/exports:** Plotly 5.24.1, kaleido 0.2.1 (server-side image export), matplotlib (one site), openpyxl (Excel).
- **Not a package.** There is no `pyproject.toml [project]` table, no `setup.py`, no wheel build. `pyproject.toml` only configures ruff. The app is run from a clone.
- **Launch:** `streamlit run app.py` after `pip install -r requirements.txt` (README "Installation"). `.streamlit/config.toml` sets `server.headless = true`, `browser.gatherUsageStats = false`, and theming. No other server options are set (so `server.maxUploadSize` is Streamlit's default, 200 MB, verified with `streamlit.config.get_option`).
- **Deployment artefacts:** none. No `Dockerfile`, no `Procfile`, no Streamlit Community Cloud config, no `.github/` (no CI), no lockfile.

```
app.py                     thin entry: page config, init_session, sidebar, overlays, lazy module router
core/                      config (MODULES registry, VERSION, p-value convention), data loaders, session state, upload UI/validation
modules/<m>/{workflow,ui}.py   6 modules, Streamlit UI and step routing
stats/ (+ stats/shared/)   pure statistics, @st.cache_data wrapped
utils/                     ui_shell, plotting (4,392 lines), plot_theme, export (2,591 lines), colours, docs
tests/                     31 pytest files, 366 tests
validation/                Python emitters + R reference scripts per module, frozen reference CSVs
example_data/              7 published GPL (>=2) datasets from SensoMineR / cata
docs/open-items.md         the project's live backlog (states "Nothing is open")
README.md, Statistical_Methods_README.md (257 KB), CHANGELOG.md, CLAUDE.md, LICENSE (MIT)
data/                      git-ignored private datasets (never committed; checked, see section 7)
```

Line counts (production Python): about 40,000 lines. Largest files: `utils/plotting.py` 4,392; `modules/liking/workflow.py` 3,675; `modules/cata/ui.py` 3,136; `modules/fusion/workflow.py` 2,965; `utils/export.py` 2,591; `modules/descriptive/workflow.py` 2,544.

## 2. Module inventory

All modules are registered in `core/config.py::MODULES` and routed lazily by `app.py` via `importlib` from the `"render"` string. Steps inside a module dispatch by index (`core/state.dispatch_step`). Every module ends in an Excel export built in `utils/export.py`, and each export writes a `Run_Parameters` sheet (`utils/export.build_run_parameters_sheet`) including `freesense_version`.

| Module | Entry (render) | Steps | Main stats functions | Input expected | Outputs |
|---|---|---|---|---|---|
| CATA (stable) | `modules.cata.workflow:render_cata_module` -> `modules/cata/ui.py` | 8 | `stats/shared/frequency.py` (Cochran's Q, McNemar, Wilson CI, citation matrices), `stats/cata.py` (`compute_ca`, `compute_ca_ellipses`, `run_cata_contrast`, `compute_penalty`) | Wide 0/1/NaN file: consumer, product, optional replicate, attribute columns; optional companion liking file | Frequency tables and heatmap, Cochran's Q, McNemar pairs + CLD, contrast, CA biplot with bootstrap ellipses, penalty analysis, Excel |
| RATA (stable) | `modules.rata.workflow:render_module_content` (re-export of `modules/rata/ui.py`) | 8 | `stats/mixed_models.py` (LMM + LRT), `stats/posthoc.py`, `stats/contrast.py`, `stats/multivariate.py` (PCA, CVA, RV), `stats/descriptive.py`, `stats/shared/lsmeans.py`, `stats/shared/frequency.py` | Wide file: assessor, product, optional replicate, attribute intensity columns (blank = not ticked) | Usage, LMM table, CLD, contrasts, PCA/CVA maps, diagnostics, Excel |
| Descriptive (DA, stable) | `modules.descriptive.workflow:render_module_content` | 8 | `stats/da_anova.py` (two-way OLS, Type III sum-to-zero, conditional F; Type II additive with empty cells), `stats/posthoc.py`, `stats/contrast.py`, `stats/multivariate.py`, `stats/panel_performance.py` (pingouin ICC), `stats/shared/lsmeans.py` | Wide file: assessor, product, optional replicate/session, attribute intensities; NaN preserved | ANOVA table, CLD, attribute overview, contrasts, PCA/CVA, 4-dimension panel performance, diagnostics, Excel |
| Liking (stable) | `modules.liking.workflow:render_liking_module` | 8 | `stats/liking.py` (hedonic LMM, LS means, Kendall's W, demographics), `stats/jar_penalty.py`, `stats/segmentation.py` (AHC, k-means), `stats/mdpref.py`, `stats/prefmap.py`, `stats/contrast.py` | Long file: consumer, product, liking, optional JAR columns; optional demographics file | Hedonic overview, demographics, contrasts, segmentation, JAR penalty, internal preference map, Excel |
| Fusion (beta) | `modules.fusion.workflow:render_fusion_module` | 5 | `stats/data_fusion.py` (matching with rapidfuzz, autoscaling, merging), `stats/pls.py` (PLS, VIP, jackknife, permutation, Hotelling T2), `stats/multivariate.compute_pca_scores` | Precomputed means tables (products x variables), or DA/RATA means from session | PCA overlay, PLS model, VIP, diagnostics, Excel |
| PrefMap (beta) | `modules.prefmap.workflow:render_prefmap_module` | 3 | `stats/prefmap.py` (PREFMAP vector/quadratic, AICc), `stats/multivariate.compute_pca_scores`, `stats/data_fusion.match_samples` | Sensory means table + consumer liking (raw or means); can reuse DA/RATA means | External preference map, surface, Excel |

Shared UI: `utils/ui_shell.py` (sidebar, landing page, `render_chart`, `render_result_table`, export section), `core/upload_ui.render_column_mapping`, `core/upload_validation.validate_scale_range`.

## 3. Data flow

1. **Upload:** each module's Step 1 main panel has an `st.file_uploader` with an `on_change` reset handler. Files are held in memory by Streamlit (`UploadedFile`); `core/data.load_data()` (`@st.cache_data(max_entries=4)`) parses CSV/XLSX into a DataFrame. Nothing is written to disk by the app (Observed: grep for `tempfile`, `open(... 'w')`, `to_csv(` paths in `core/ modules/ stats/ utils/` finds none that write files; exports are built into in-memory buffers).
2. **Column mapping and validation:** `core/upload_ui.render_column_mapping` (persisted widgets), `core/upload_validation` (scale range), module-specific validators (for example CATA rejects non-binary cells).
3. **Structuring:** RATA, DA and CATA go through `core/data.clean_and_structure_data()` to a long frame (`attribute`, `intensity`, `binary`). Liking builds its long frame in `modules/liking/workflow.py`. Fusion/PrefMap use `core/data.load_precomputed_means()`.
4. **Analysis:** a "Run full analysis" button in Step 1 runs the module pipeline (`stats/*`, cached with `max_entries=8`), stores results in module-prefixed `st.session_state` keys, and calls `core.state.set_module_analysis_complete()`.
5. **Visualisation:** later steps read results from session state; Plotly figures pass through `utils.plot_theme.apply_base_layout` and render via `utils.ui_shell.render_chart` (Word/PowerPoint presets via kaleido).
6. **Export:** `utils.ui_shell.render_export_section` builds the workbook lazily in a deferred `st.download_button`. Builders live in `utils/export.py`; each writes `Run_Parameters` and a final p-value format sweep.

State lives only in the browser session's server-side `st.session_state`; there is no database and no persistence between sessions.

## 4. Dependencies

From `requirements.txt` (runtime) with installed version, licence (from package metadata) and whether production code imports it:

| Package | Installed | Licence | Used in production code? |
|---|---|---|---|
| streamlit | 1.64.0 | Apache-2.0 | yes |
| pandas | 2.3.3 | BSD-3-Clause | yes |
| numpy | 2.5.3 | BSD-3-Clause (+ bundled MIT/0BSD/Zlib/CC0) | yes |
| plotly | 5.24.1 | MIT | yes |
| kaleido | 0.2.1 | MIT | yes, indirectly (Plotly `to_image`); not imported by name |
| matplotlib | 3.11.2 | PSF-style (matplotlib licence) | yes, one site: `utils/plotting.py:2894` |
| statsmodels | 0.15.0 | BSD-3-Clause | yes (9 files) |
| scipy | 1.18.1 | BSD-3-Clause | yes (17 files) |
| scikit-learn | 1.9.1 | BSD-3-Clause | yes (6 files) |
| openpyxl | 3.1.5 | MIT | yes (Excel engine) |
| **pingouin** | 0.6.1 | **GPL-3.0** | yes, optional import in `stats/panel_performance.py:22` |
| rapidfuzz | 3.14.6 | MIT | yes, `stats/data_fusion.py:7` |
| pytest, pytest-xdist | 9.1.1, 3.8.0 | MIT | dev only |

Transitive packages of note: pingouin pulls in `seaborn` (BSD), `pandas-flavor` (MIT), `xarray` (Apache-2.0), `tabulate` (MIT). statsmodels pulls `patsy` (BSD-2). No production code imports seaborn.

**Licence flag:** the application is MIT (`LICENSE`), but it imports pingouin, which is GPL-3.0. README's licence section discusses only the GPL example datasets, not pingouin. This is carried into B08 and `02-decisions.md`; it is a legal judgement, not an engineering fact.

## 5. Tests

- Framework: pytest (`pytest.ini`: `testpaths = tests`, `-q`), with Streamlit `AppTest` for UI flows.
- Size: 31 files, 366 tests. Per file: largest are `test_export_rata.py` (18), `test_stats_layer_moves.py` (18), `test_unbalanced_designs.py` (17), `test_liking_acceptance.py` (17), `test_apptest_fusion.py` (16), `test_pvalue_convention.py` (16). Every module has an AppTest file.
- **Result:** `env/bin/python -m pytest tests/ -n auto -q -p no:cacheprovider` -> **366 passed, 0 failed, 0 skipped**, exit 0, 2 min 40 s wall (17 min 37 s CPU across workers).
- Warnings emitted during the run (each is a lead for B01/B06, not yet a finding): pingouin `RuntimeWarning: invalid value encountered in scalar divide` (`pingouin/reliability.py:353-394`, ICC on degenerate data); `ConstantInputWarning` in `stats/panel_performance.py:362` (`pearsonr` on constant input); `SingularMatrixWarning` in `stats/da_anova.py:526` (rank-deficient OLS with empty cells); pandas `FutureWarning` in `stats/panel_performance.py:138` (`DataFrameGroupBy.apply` on grouping columns, will change behaviour in a future pandas); numpy `Degrees of freedom <= 0` in the panel-stability path.
- Reference-value tests: `tests/test_validation_pins.py` (7 tests) re-runs the validation emitters against frozen R reference CSVs.
- Coverage: see section 5a (filled in once the coverage run finishes).

### 5a. Coverage

Command (coverage and pytest-cov installed to the session scratchpad, not the project venv):
`PYTHONPATH=<scratchpad>/covtools env/bin/python -m pytest tests/ -n auto -q -p no:cacheprovider --cov=core --cov=stats --cov=utils --cov=modules --cov-report=term -W ignore`

**Total line coverage: 77% (13,562 statements, 3,142 missed).** Selected files:

| Area | Lowest-covered files |
|---|---|
| stats | `mdpref.py` 12%, `data_fusion.py` 64%, `segmentation.py` 66%, `multivariate.py` 77%, `contrast.py` 80%, `posthoc.py` 81% |
| modules | `prefmap/ui.py` 44%, `fusion/ui.py` 64%, `prefmap/workflow.py` 65%, `liking/ui.py` 66%, `liking/workflow.py` 67% |
| core/utils | `core/data.py` 55%, `utils/plotting.py` 61% |
| well covered | `stats/descriptive.py` 98%, `modules/descriptive/ui.py` 95%, `utils/ui_shell.py` 95%, `core/state.py` 95%, `stats/mixed_models.py` 93% |

Caveat (Inferred, not verified): if `tests/test_validation_pins.py` runs the emitters in a subprocess, the code they exercise is not counted, which would understate coverage for `stats/mdpref.py` and similar. B05 checks this.

## 6. Static checks (substitute for `R CMD check`)

`ruff check . --exclude env --statistics` using the repo's own `pyproject.toml` rule set (ruff installed to the session scratchpad): **226 findings**, of which 141 auto-fixable.

| Rule | Count | Meaning |
|---|---|---|
| I001 | 75 | unsorted imports |
| F401 | 35 | unused imports (spread over 16 files; 9 in `modules/descriptive/ui.py`, 7 in `modules/liking/workflow.py`) |
| E701 / E702 | 34 / 32 | multiple statements on one line |
| W293 | 23 | whitespace on blank line |
| E712 | 18 | `== True` / `== False` comparisons |
| W292, E401, F541, F811, W291 | 4, 2, 1, 1, 1 | minor |

No F821 (undefined name) or E9 (syntax) findings. CLAUDE.md states "No linter is configured", but `pyproject.toml` does configure ruff; ruff is not in `requirements.txt` and is not run anywhere.

## 7. Git state

- Branch `main`, up to date with `origin/main` (`https://github.com/Sesnor-y/FreeSense.git`). 403 commits. Tags (local only, per B08): `v0.2.0` (2026-03-08), `v1.0.0` (2026-05-18, 146 commits behind HEAD).
- Recent commits: `bcaf9f8 beta labels for prefmap and data fusion`, `03efed4 improved unbalanced data handling`, `a564616 Fixed panel performance issues with unbalanced data`, `1b43357 Improved DA performance evaluation`, `b0996ea ui improvements`.
- TODO/FIXME/HACK/XXX in `*.py`, `*.R`, `*.sh` outside `env/`: **none found**.
- Data files in history outside `example_data/` and `validation/*/reference/`: **none** (`git log --all --name-only --diff-filter=A` filtered on csv/xlsx/xls/xlsm/env/pem/key and `data/`).
- Secret-like assignments (`api_key|secret|password|token = '...'`) anywhere in `git log --all -p`: **none**.
- Absolute home paths (`/var/home/Lukas/...`) appear 130 times in history, all in deleted planning/review Markdown files (for example "Working tree: `/var/home/Lukas/Projects/RATA-Flow-App`"). None in the current tree. Low sensitivity (reveals a local username), noted for B07.

## 8. Prior review work found

The prompt's section 0 lists no prior work, but the repository contains a lot:

- **`docs/review/` (deleted in `d9ac9d5`, 2026-06-13; created in `bbd91e2`, 2026-05-16):** a full staged pre-release audit (inventory, stats, UX, docs, code, release findings, fix plan, stage prompts, triage summary). 105 findings: 6 blockers (DA Type II vs Type III SS; `.get()` defaults on statistical parameters across modules; README "five modules"; missing dendrogram docs; stat README defending Type II; no LICENSE), 31 major, 50 minor, 18 nit. Retrieve with `git show d9ac9d5^:docs/review/_summary.md`.
- **Other deleted audit files in history:** `AUDIT_REPORT.md`, `AUDIT_REPORT_R2.md`, `AUDIT_FIX.md`, `AUDIT_PrefMap.md`, `data_fusion_audit_findings.md`, `data_fusion_review.md`, `fable_review.md`, `docs/streamlit_plumbing_audit.md`, `docs/ui-audit-notes.md`, several implementation plans.
- **Live:** `CHANGELOG.md` (claims closure of every stage A to H and the September 2026 Streamlit clean-up), `docs/open-items.md` ("Nothing is open"), `.claude/agent-memory/method-auditor/da_anova_audit.md`, `validation/README.md` (coverage map and known gaps).

**Where the prior work no longer matches the code (Observed):**
- The May review's "no LICENSE" and "no tests/" blockers no longer apply: `LICENSE` (MIT) and `tests/` (366 tests) exist.
- The May review's "DA Type II vs Type III" blocker was resolved towards Type III with sum-to-zero coding (`stats/da_anova.py`), but the September changelog reintroduces Type II for the empty-cell path. Both paths exist today; B01 must check each.
- `CHANGELOG.md` `[1.0.0]` says "the local tag candidate `v1.0.0` ships after sign-off", the tag exists locally (not pushed) and 146 commits have landed since with the version string unchanged.
- `docs/open-items.md` says nothing is open. That is a claim to be tested by this review, not accepted.

Leads noticed during orientation, passed to the relevant reviewers (not yet findings):
- `modules/descriptive/workflow.py:389` status text says "Running mixed-effects ANOVA for each attribute" while CLAUDE.md and `stats/da_anova.py` describe two-way OLS (B09).
- `README.md:154` says the CATA penalty independence caveat is rendered "under every significant row"; CLAUDE.md says the per-row caveat was retired in favour of a single caption (B09).
- README states "no application code reads" `example_data/`: grep confirms no `example_data` reference in `app.py`, `core/`, `modules/`, `utils/` (B03/B08).
- The pandas `FutureWarning` at `stats/panel_performance.py:138` (B04/B06).
