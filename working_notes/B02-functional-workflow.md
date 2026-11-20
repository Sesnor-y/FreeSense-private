# B02 Functional behaviour and user workflow

Reviewer: B02 (functional workflow). Commit `bcaf9f8`. Review only; no application files changed.

## Scope and method

- Drove the real app headlessly with `streamlit.testing.v1.AppTest` (Streamlit 1.64.0). Unlike the repo's own AppTests, which monkeypatch `render_data_upload_section` and `load_data`, uploads went through the **real `st.file_uploader`** (`at.file_uploader(key=...).set_value((name, bytes, mime))`), so `core.data.load_data`, the uploaders' `on_change` resets and the widget lifecycle were all exercised.
- To render every lazily gated panel on each step, the harness patched `ExpanderContainer.open` / `TabContainer.open` to `True` in the test process (a "maximal render"), and wrapped `utils.ui_shell.render_export_section` so every Excel workbook was actually built and its sheets listed.
- Each step: counts of `at.exception`, `st.error`, `st.warning`, `st.info`, charts and dataframes were recorded.
- Scripts and outputs: `/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B02/` (`harness.py`, `raw_driver.py`, `run_*.py`, `out_*.txt`, `data/` holds every constructed bad file, built by `make_bad.py`).
- Datasets: all eight files in `example_data/`, plus 17 constructed variants of a 12-panelist x 4-product x 2-session x 5-attribute subset of sensochoc (`data/small.csv`): European CSV (`;` + decimal comma), comma CSV with decimal commas, text cells in an intensity column, extra text columns, the whole file duplicated, blank product cells, special/non-ASCII/emoji/formula-character factor levels, 220-character and formula-character attribute names, headers colliding after whitespace stripping, numeric product codes, no product column, `.CSV` upper-case extension, title row above the header, Latin-1 encoding, tab-separated `.csv`.

End-to-end walks completed without an exception element (all steps, export built):

| Module | Data | Result |
|---|---|---|
| DA | sensochoc (full), small subset, special levels, weird attribute names, colliding names, extra text columns | all 8 steps render, 17-sheet export |
| RATA | small subset | all 8 steps, 12-sheet export |
| CATA | bread (with in-file liking), bread with special product names | all 8 steps, 11-sheet export |
| Liking | hedochoc | all 8 steps, export |
| Fusion | cocktail sensory + composition | 5 steps, PCA and PLS, export (7 sheets before fit, 14 after) |
| PrefMap | cocktail sensory + a **pivoted** liking file | 3 steps, fit, export |

Special characters in factor levels (Käse, Crème brûlée, emoji, `A+B ~ x:y (new)`) and in attribute names (`Sweet+Sour`, `a ~ b`, `Bitter:after`, `1st taste (x)`, 220 x "L") caused no crash in DA, RATA or CATA. Verified reason: every statsmodels formula uses fixed internal column names (`Prod_Safe`, `Assessor_Safe`, `_product`, `_consumer`, `_demo`), and user labels only appear as data values (`stats/da_anova.py:175-176,224`, `stats/mixed_models.py:56-64`, `stats/liking.py:166-167,235-248,1155`). However, one place parses statsmodels *parameter names* back into labels, and that is the BLOCKER below.

## Findings

### FUNC-01: Liking LS means silently wrong when a product name contains "Var" or "Cov"
- Severity: BLOCKER
- Confidence: VERIFIED
- Location: `stats/liking.py:258-261` (`compute_liking_lmm`)
- Evidence: fixed-effect parameters are selected with `if 'Var' not in p and 'Cov' not in p`. The parameter names include the product label (`C(_product)[T.Variety A]`), so a product whose name contains "Var" or "Cov" is dropped from the fixed-effect design matrix and gets the intercept (the reference product's mean) as its LS mean. Reproduction: `scratchpad/agents/B02/liking_var.py` renames hedochoc `choc1..6` to `Variety A, Variety B, Covent, Plain, Dark, Milk`:
  ```
  product   ls_mean   (raw mean)
  Covent    5.765766  5.765766
  Variety A 5.765766  5.328829   <- wrong, equals the reference
  Variety B 5.765766  5.689189   <- wrong
  ```
  The same data with names `choc1..6` gives the correct 5.3288 / 5.6892. `cov_lsmeans` is built from the same matrix, so standard errors, CLD letters and contrasts that consume it are also wrong. The UI path (Liking Step 1 "Run full analysis") calls this function (`run_liking.py`, `variety.csv`, ran with no warning). No error or warning is shown.
- Impact: any consumer study with a product called "Variety ...", "Varietal", "Covent ...", "Cover", "Vareniki" and so on gets wrong hedonic means, wrong letters and wrong contrasts, with no signal. Plausible product names in food and beverage work.
- Recommendation: select fixed effects by position or with `result.fe_params.index` (statsmodels exposes it) instead of substring matching; add a regression test with product names containing "Var" and "Cov".
- Effort: S
- Dependencies: none

### FUNC-02: DA crashes with a raw traceback when no attribute column is numeric (for example decimal-comma CSV)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `stats/panel_performance.py:551` (`compute_scale_usage`), reached from `modules/descriptive/workflow.py:76,393`; Step 1 has no numeric check (`modules/descriptive/workflow.py:255-340`, `modules/descriptive/ui.py:69-142`)
- Evidence: `data/eu_comma_quoted.csv` (comma-separated, values such as `"7,5"`). DA, map Panelist/Product/Session, scale 0 to 10. Step 1 shows only "**480 blank cells detected** across 5 attribute columns ... treats a blank as a missing observation". Clicking Run gives an exception element `KeyError: 'mean_bias'` with a stack trace (`client.showErrorDetails` is `full`, so the user sees the full traceback). The same happens for any file whose attribute columns are all text.
- Impact: a European Excel user (decimal comma is the default in DE/FR/IT/ES/NL/Nordics locales) sees a Python traceback after being told the cells are merely "blank". Core workflow crash.
- Recommendation: in DA Step 1, detect attribute columns that are mostly non-numeric (as RATA does) and block with a message naming the likely cause ("these columns contain text such as '7,5'; if your file uses decimal commas, re-save it with a decimal point or ..."). Better still, accept decimal commas in `load_data` (see FUNC-05). Also make `compute_scale_usage` return an empty frame rather than raising when nothing is numeric.
- Effort: S
- Dependencies: FUNC-05

### FUNC-03: Duplicated rows silently change DA results
- Severity: HIGH
- Confidence: VERIFIED
- Location: `modules/descriptive/ui.py:69-142` (`validate_da_design` has no duplicate check); `stats/da_anova.py`
- Evidence: `data/dup_rows.csv` is `small.csv` concatenated twice (a typical copy/paste or double-export error). DA Step 1 shows no warning at all (metrics still say 12 assessors, 4 products, 2 replicates). The ANOVA changes materially (`checks1.py`):
  ```
  small: MilkF F_product 64.98, df_error 48, tested_against Residual, p_interaction 0.113
  dup:   MilkF F_product 44.43, df_error 33, tested_against Interaction, p_interaction 3.1e-10
  ```
  Every attribute's interaction becomes "significant" and the error term switches. RATA is unaffected in substance (cells are averaged, `modules/rata/ui.py` warns only when no replicate is mapped).
- Impact: wrong inference (interaction, error-term choice, repeatability, panel performance) from a common data-entry error, with no warning.
- Recommendation: in DA (and for consistency RATA/Liking/CATA) Step 1, count rows duplicated on assessor x product x replicate and block or warn with the count and example rows.
- Effort: S
- Dependencies: none

### FUNC-04: Blank product (or assessor) cells become a real level called "nan"; RATA crashes
- Severity: HIGH
- Confidence: VERIFIED
- Location: `core/data.py:190-197` (`clean_and_structure_data` casts meta columns with `astype(str)`), `stats/mixed_models.py:60`
- Evidence: `data/nan_product.csv` (three rows with an empty Product cell).
  - DA: runs with no warning; Step 1 metric says "Products 4" (computed on the raw frame) but `da_df_long` contains products `['choc1','choc2','choc3','choc4','nan']`, so a fifth product "nan" with three observations enters the ANOVA, means, maps and export.
  - RATA: Step 1 shows "Products 5" and an unbalanced-design warning, then Run raises `PatsyError: factor contains missing values` as an exception element (`modules/rata/ui.py:427` to `stats/mixed_models.py:60`).
- Impact: silently analysing a phantom product (DA) or crashing (RATA) on a very common data defect (empty trailing rows in Excel, missing codes).
- Recommendation: before casting to string, drop rows with a missing assessor/product (and replicate, if mapped), and report "N rows had no product/assessor code and were excluded". Compute Step 1 metrics on the cleaned frame.
- Effort: S
- Dependencies: none

### FUNC-05: File reading is brittle and failures are silent or unintelligible (delimiter, decimal comma, encoding, .xls, .CSV)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `core/data.py:7-37` (`load_data`); uploaders in `modules/descriptive/workflow.py:109`, `modules/rata/ui.py:108`, `modules/cata/ui.py:369,616` accept `xls`
- Evidence (`load_check.py` and AppTest `run_bad.py`):
  - `;`-separated file (`data/eu_semicolon.csv`, Excel's CSV default in most of continental Europe): loads as **one** column `Panelist;Session;Product;...`. Step 1 shows no error; the mapping selectbox simply offers that one string. Same for a tab-separated `.csv` and a file with a title row above the header (`title_row.csv`: single column "Study XYZ export 2026").
  - Decimal commas: see FUNC-02 (DA crash) and FUNC-06 (RATA message).
  - Latin-1 file with umlauts (`latin1.csv`): `Error loading file: 'utf-8' codec can't decode byte 0xfc in position 61: invalid start byte`.
  - `.xls`: uploaders advertise it but `xlrd` is not in `requirements.txt` or the venv; any real `.xls` gives `Error loading file: Missing optional dependency 'xlrd'. Install xlrd >= 2.0.1 for xls Excel support Use pip or conda to install xlrd.`
  - `SMALL.CSV`: `load_data` tests `name.endswith('.csv')` case-sensitively, so it goes to `read_excel`: `Error loading file: Excel file format cannot be determined, you must specify an engine manually.` (Inferred: Streamlit's uploader accepts `.CSV` for `type=["csv"]`; not tested in a browser.)
- Impact: the first contact for many European users is either a silent one-column mapping screen or a developer-facing error. None of the messages tells a sensory scientist what to do.
- Recommendation: sniff the delimiter (`sep=None, engine="python"` or `csv.Sniffer`), accept `decimal=","` when the sniffed delimiter is `;`, fall back from UTF-8 to cp1252/latin-1, compare extensions case-insensitively, and either add `xlrd` or drop `xls` from every uploader's `type`. When the parsed frame has one column, show "Only one column was found; your file may use ';' or tabs as separator, or have a title row above the headers".
- Effort: S to M
- Dependencies: decision on supported file formats

### FUNC-06: Non-numeric cells are reported as "blank", and wrong advice is given for decimal-comma columns
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `modules/rata/ui.py:255-263` and the blank-cell warnings in DA (`modules/descriptive/workflow.py:~310-330`), RATA (`modules/rata/ui.py:~370`), CATA (`modules/cata/ui.py:~797-812`); `core/data.py:200-214`
- Evidence:
  - RATA, `data/text_cells.csv` (cells `n/a`, `high`, `5,5` in CocoaA): warning "**3 blank cells detected** ... Blank cells are filled with **0**". The cells were not blank; `5,5` (a real 5.5 rating) becomes 0 and the analysis runs.
  - RATA, `data/eu_comma_quoted.csv`: "Text metadata detected in attributes: **CocoaA, MilkA, CocoaF**. Please add these to 'Exclude Metadata Columns'." These are the rating columns; excluding them is the wrong fix, and only three of five are named.
  - CATA, bread with `yes` / `x` typed into a 0/1 column: "**2 blank cells detected** ... Missing values will be excluded from pairwise tests", then "Cochran's Q: 2 of 161 assessor(s) with missing data excluded". "yes"/"x" almost certainly meant a tick.
  - DA, `data/extra_cols.csv` (un-excluded `Comment` and `Date` text columns): Step 1 counts "Attributes 7" and warns about 192 "blank cells"; Step 3 then says `Comment, Date` "were excluded ... because their mean is constant across products", and the ANOVA table carries them with status `insufficient_products`. RATA and CATA detect such columns; DA does not.
- Impact: users are misled about what is wrong with their file; in RATA a non-blank rating can be silently turned into 0.
- Recommendation: report non-numeric (text) cells separately from true blanks, with column, row and example values; block when a supposedly numeric cell holds text (other than an agreed missing code). Give DA the same text-column detection as RATA/CATA. When the text looks like a decimal comma (`^\d+,\d+$`), say so.
- Effort: S
- Dependencies: FUNC-05

### FUNC-07: The shipped PrefMap consumer file cannot be used by PrefMap, and the error does not explain why
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `modules/prefmap/workflow.py:546-600`; `example_data/05_Fusion_PrefMap/Cocktail_consumer_liking.xlsx`; `example_data/README.md` ("Use: the consumer block for PrefMap")
- Evidence: PrefMap, sensory = `Cocktail_sensory_means.xlsx`, consumer = "Upload raw consumer liking scores", file = `Cocktail_consumer_liking.xlsx` (long: consumer, product, liking). Result: `Only 1 numeric consumer columns found. Expected at least 5 consumers. Check that columns represent individual consumers and the product column is correctly selected.` The product-column selectbox defaults to the first column (`consumer`). The path expects wide format (products x consumers). The repo's own test pivots the file before feeding it (`tests/test_apptest_prefmap.py:34-37`), so the test suite never exercises the shipped file as a user would. After pivoting (`run_prefmap.py`) the whole PrefMap workflow and export work. Uploading the same long file as Fusion's external block gives "Different number of products: sensory (16) vs external (1600)".
- Impact: the documented example fails; the message does not mention long versus wide layout. The Liking module takes long format, so users will reasonably try the same layout here.
- Recommendation: accept long format (consumer/product/liking mapping, pivot internally), or at minimum detect it (few numeric columns, many repeated product values) and say "this looks like long format; PrefMap needs one row per product and one column per consumer". Ship a wide copy or fix the README.
- Effort: S to M
- Dependencies: none

### FUNC-08: After switching modules, the uploaded file is gone from Step 1 although results remain, and changing any setting forces a full re-upload
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: DA/RATA/CATA/Liking Step 1 (`render_data_upload_section` returns `None`; e.g. `modules/descriptive/workflow.py:113-116` returns immediately)
- Evidence (`run_state.py`): run DA, switch to PrefMap, switch back. `da_analysis_complete` is still `True` and Step 3 renders the old results, but Step 1 shows only an empty uploader (`uploader value None`): no mapping, no parameters, and no message saying which file the current results came from. Re-uploading the same file fires `on_change=reset_analysis_state` and discards the completed analysis (`da complete None`). PrefMap already handles this case with "Using previously uploaded liking scores, re-upload to change" (`modules/prefmap/workflow.py:563-566`); DA/RATA/CATA/Liking do not.
- Impact: a user who goes back to Step 1 to check or tweak a parameter sees an apparently empty study and has to redo the analysis; nothing shows which file produced the results on screen.
- Recommendation: keep the last raw frame and file name in module state and render Step 1 from it when the uploader is empty ("Current data: sensochoc.xlsx, uploaded 14:02. Upload a new file to replace it"). Alternatively, show at least the file name and parameters used on every step.
- Effort: M
- Dependencies: none

### FUNC-09: Browser refresh or a dropped connection loses all work with no warning
- Severity: MEDIUM
- Confidence: VERIFIED (code inspection); refresh itself not simulated in a browser
- Location: `app.py`, `core/state.py` (all state in `st.session_state`); `.streamlit/config.toml`
- Evidence: no persistence, save/restore, or `query_params` mechanism exists (`grep -rn "query_params|pickle|save_session|beforeunload"` over `app.py core modules utils`: no hits). No text in the app or README tells users that refreshing, closing the tab or a network drop longer than `server.disconnectedSessionTTL` (120 s, default) discards uploads and results (`grep -i "refresh|not saved|session only"`: no user-facing hits). `persist_state="session"` keeps widget values across module switches only, not across a browser session.
- Impact: a sensory scientist who spends time on segmentation, PLS pruning or penalty settings and presses F5 loses everything silently. The Excel export is the only way to keep results.
- Recommendation: one caption on the landing page and on each Step 1 ("Nothing is stored on the server. Refreshing or closing this tab clears your data and results; download the Excel report to keep them."). Consider an "export/import settings" JSON later.
- Effort: S
- Dependencies: decision on deployment (hosted versus local)

### FUNC-10: DA/RATA default scale 0 to 100 is accepted silently for 0 to 10 data
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/descriptive/workflow.py:175-195`, `modules/rata/ui.py:195-203`
- Evidence: with sensochoc (0 to 10) and the default scale 0 to 100, DA Step 1 raises nothing and the Run button is enabled (`run_da.py`, "mapped (scale default 0-100)": 0 errors, 0 warnings). The scale feeds bar-chart axes (`workflow.py:523,580`), profile plots (`:1799,1848`) and scale-usage panel metrics. Liking already suggests a scale from the observed range (U2); DA/RATA only check values above the maximum.
- Impact: charts compressed into the bottom tenth of the axis; scale-usage metrics relative to the wrong range.
- Recommendation: show the observed min/max next to the scale inputs and warn when the data use less than about half of the declared range.
- Effort: S
- Dependencies: none

### FUNC-11: Gating messages reference step names and actions that do not exist
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/fusion/workflow.py:1053,1416,2393,2744`, `modules/prefmap/workflow.py:1494`
- Evidence: Fusion Steps 2 and 3 say "run the full analysis in the **1. Analysis Setup** step". Fusion has no "Run full analysis" button (the action is "Confirm matches"), and the sidebar label is sentence case. Other hard-coded labels: "**3. PLS Model Building**", "**2. Exploratory Overlay (PCA)**", "**2. External Preference Map**", which do not match the sidebar labels (`2. Exploratory overlay (PCA)` and so on) that `core.state.check_analysis_ready` derives from `MODULES`.
- Impact: small confusion; drift from the naming convention the project pins elsewhere.
- Recommendation: derive these messages from `MODULES` (`ui_shell.step_title`) and name the actual button.
- Effort: S
- Dependencies: none

### FUNC-12: The bundled CATA example opens with a red error
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/cata/ui.py:766-795`
- Evidence: bread file, after mapping consumer and product: "**Attribute columns contain values greater than 1.** ... use the **RATA module** instead", because the in-file `liking` column is not auto-designated; the user must pick it in "Consumer overall liking". The follow-up info box does explain the fix.
- Impact: the first run of the flagship example looks like a failure.
- Recommendation: when exactly one non-binary numeric column exists and it is named like `liking|hedonic|overall`, pre-select it as the liking column (the upload-derived default convention already exists for other widgets).
- Effort: S
- Dependencies: none

## Checked, nothing material found

- Full end-to-end walks of all six modules on the bundled data (table above): no exception elements on any step with every tab and expander forced open; every Excel export built and opened with pandas.
- Special characters, non-ASCII, emoji and patsy-significant characters in product/assessor levels and attribute names (DA, RATA, CATA): no crash, exports built. Formulas never embed user labels.
- 200+ character attribute names: no crash (layout not visually inspected).
- Header names that collide after stripping (`Sweet`, `Sweet `): de-duplicated to `Sweet.1` by `load_data` (`core/data.py:24-35`), with no message. Acceptable, though the user is not told.
- Numeric product codes (101, 102, ...): run cleanly (cast to string).
- Changing Step 1 inputs after a run: DA re-upload through the real uploader cleared `da_anova_df` and completion; later steps then show "Please configure your parameters and run the full analysis..." (no stale output). The repo tests cover the alpha/interaction-alpha resets.
- Re-uploading a file with different column names: mapping falls back to "Select…" (no stale column used).
- Cross-module handoff DA to PrefMap: PrefMap picks up DA means; after DA is re-run with 5 attributes excluded, PrefMap updates its sensory block, drops the old fit ("Settings changed since the last run. Press **Fit PREFMAP models** to update.") and blocks Step 3. When DA is invalidated, PrefMap Step 1 says "No Descriptive Analysis results found in this session". Correct behaviour.
- RATA with duplicated rows: averaged per cell, no change in inference.
- Missing product column, where the user maps the wrong column: runs as the user instructed (Session as product); not an app defect.

## Decisions raised

- Supported input formats: is `.xls` supported (add `xlrd`) or not (remove it from uploaders)? Are European CSV conventions (`;` and decimal comma) in scope? For an EU sensory audience they arguably must be.
- Deployment: if hosted, the 120 s disconnected-session TTL and the absence of any save/restore become more significant (FUNC-09); if local, a refresh warning is probably enough.
- Should Fusion and PrefMap accept long-format consumer data (FUNC-07), given that Liking only accepts long format?

## Leads for other areas

- B01 (stats): FUNC-01 is a statistical correctness defect found through the workflow; the rest of `stats/` should be checked for any other parsing of statsmodels parameter names (grep found only this site).
- B04/B06: `stats/panel_performance.compute_scale_usage` raises `KeyError` on an empty frame instead of degrading (FUNC-02 root cause).
- B06 performance (observed under shared CPU load, not a finding): full sensochoc DA run took 12 s in one run and 115 s in another with nine reviewers running; DA Step 7 took 17 to 27 s with all panels forced open.
- B09 (docs): `example_data/README.md` says `Cocktail_consumer_liking.xlsx` is the PrefMap consumer block, which contradicts FUNC-07. README should state that session data is lost on refresh.
- B03: the AppTest suite monkeypatches both the uploader and `load_data`, so no test covers real file parsing, which is how FUNC-05 and FUNC-07 slipped through.
