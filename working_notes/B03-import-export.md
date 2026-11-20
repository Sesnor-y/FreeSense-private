# B03 Data import, export and reporting

Reviewer: B03 (data pipeline). Commit `bcaf9f8`. Review only; no code changed.
Scratch scripts and outputs: `/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B03/`.

## Scope and method

- Read `core/data.py` (`load_data`, `load_precomputed_means`, `clean_and_structure_data`), `utils/ui_shell.render_data_upload_section` / `render_export_section` / `render_chart`, `utils/plot_theme.export_figure`, `utils/export.build_run_parameters_sheet` and module Step 1 blocks (RATA, DA, CATA, Liking, Fusion, PrefMap).
- `fmt.py`, `fmt2.py`: fed `load_data` / `load_precomputed_means` real `UploadedFile` objects (as `tests/test_load_data.py` builds them) in UTF-8, UTF-8 BOM, Latin-1, cp1252, UTF-16, semicolon + decimal comma, comma + quoted decimal comma, TSV, uppercase `.CSV`, trailing empty rows/columns, header offset, duplicate headers, multi-sheet xlsx, xlsm, real OLE2 `.xls`.
- `at_rata_trailing.py`: AppTest runs of RATA and DA Step 1 through "Run full analysis" on the sensochoc dataset (a) as a CSV with two trailing all-comma rows (what Excel writes after deleted rows), (b) with 10 % of `CocoaA` cells written with a decimal comma. `da_cmp.py`, `da_cld.py`: direct comparison of DA results with and without the trailing rows.
- `export_drive.py`: AppTest drives RATA, DA, CATA and Liking on the bundled example datasets through every step, captures the deferred workbook builder and every `render_chart` figure; `inspect_xlsx.py` checks number formats, stored precision and `Run_Parameters`. Fusion/PrefMap `Run_Parameters` checked by calling `build_run_parameters_sheet` directly.
- `render.py`: rendered the 10 RATA figures through `export_figure` (Word and PowerPoint presets, PNG and SVG) with kaleido 0.2.1 on Python 3.14.7; inspected two PNGs visually.
- `cvd.py`: simulated deuteranopia, protanopia, tritanopia (Machado et al. 2009 matrices, severity 1.0) and luminance-only greyscale for every palette in `utils/colours.py`, reporting minimum pairwise CIEDE2000.
- Per the coordinator: Excel formula injection and the upload size cap are covered by B07 and not repeated here.

## Findings

### IO-01: Trailing empty rows create a phantom product "nan"; DA silently changes results, RATA crashes
- Severity: BLOCKER
- Confidence: VERIFIED
- Location: `core/data.py:17-37` (`load_data`, no empty-row drop), `core/data.py:193-195` (`astype(str)` turns NaN into the string `'nan'`), `core/data.py:214` (RATA zero-fill); RATA `modules/rata/ui.py:427` -> `stats/mixed_models.py:60`
- Evidence: sensochoc exported to CSV plus two lines of only commas (the usual artefact of deleted rows in Excel). `load_data` returns 350 rows, the last two all-NaN. After `clean_and_structure_data` both DA and RATA carry a product `'nan'`, assessor `'nan'` and replicate `'nan'`.
  - DA (AppTest): no error. The only message is "28 blank cells detected". Step 1 metrics say Products 6 / Assessors 29, but `da_df_long` has products `[choc1..choc6, 'nan']` and 30 assessors. `'nan'` shows up in `da_summary_df`, `da_cld_df` (for example `MilkF nan abcde`), `da_rv_df` (30 assessors) and the Raw_Data export. Direct comparison (`da_cld.py`) against the clean file shows **3 CLD pairwise verdicts among the real products change**: Bitterness choc4 vs choc6 and Sweetness choc2 vs choc6 go from different to not different. Panel-performance frames (`da_agree_df`, `da_scale_df`, `da_rv_df`) also differ.
  - RATA (AppTest): the zero-filled `'nan'` product passes validation. It shows only an "Unbalanced design (Min: 1, Max: 29)" warning and Products 7. "Run full analysis" then raises an uncaught `patsy.PatsyError: factor contains missing values` from `run_mixed_models`. The user sees a traceback.
  - An xlsx whose stray cell holds a space, or a formatted row further down, gives the same NaN rows (`fmt2.py`, `trail.xlsx`: 7 rows for 2 data rows, plus `Unnamed: 3/4` columns).
- Impact: a very common file artefact silently changes DA post-hoc groupings and panel-performance figures, and crashes RATA. Unnamed empty columns also become attributes: all-zero in RATA, all-NaN in DA.
- Recommendation: in `load_data`, `dropna(how='all')` on rows and columns and drop `Unnamed: n` columns that are entirely empty, and report the count. In `clean_and_structure_data`, reject (raise) rows where any mapped meta column is NaN before the `str` cast, and never let the literal string `'nan'` become a level. Add a regression test using sensochoc plus trailing blank rows.
- Effort: S
- Dependencies: none

### IO-02: Decimal-comma numbers are silently zero-filled (RATA), dropped (DA) or dropped as whole columns (means tables)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `core/data.py:199-214`, `core/data.py:103-109` (`load_precomputed_means`, 50 % coercion rule), RATA blank-cell warning `modules/rata/ui.py` Step 1
- Evidence: sensochoc with 35 of 348 `CocoaA` cells written as `"7,5"` (a comma-delimited CSV with quoted decimal-comma cells, or a column Excel stored as text).
  - RATA: no error. The warning reads "35 blank cells detected … filled with 0". After the run, `CocoaA` has 36 zeros instead of 1: every 7.5 became 0.
  - DA: "35 blank cells detected … treated as missing observation". The values are dropped from the ANOVA.
  - The text-column check only fires above 50 % non-numeric, and the scale-range check (`core/upload_validation.py:63`) coerces first, so neither catches it.
  - Means table (`load_precomputed_means`, `fmt2.py`): a column that is all decimal-comma (`Sour`) stays object dtype and is silently left out, because the Fusion/PrefMap validators keep only numeric columns (`modules/fusion/workflow.py:536`, `modules/prefmap/workflow.py:338`). Mixed columns get NaN cells. `nan_affected` is returned, but no caller reads it (grep: only the tuple unpacking at `fusion/workflow.py:363` and `prefmap/workflow.py:313`), so the NaN warning the docstring promises is never shown.
- Impact: European-locale users lose or zero real ratings. The only message calls them "blank". For RATA this changes means, LMM and CLD without a correct warning.
- Recommendation: before coercion, count cells that are non-empty strings but fail `to_numeric`. Report them separately from true blanks, naming the column and example values. Block the run when they match `^\d+,\d+$`, and offer "interpret comma as decimal separator". Never zero-fill a non-empty unparseable cell. Surface `nan_affected` and any dropped non-numeric columns in Fusion/PrefMap.
- Effort: M
- Dependencies: IO-03

### IO-03: European CSVs (semicolon delimiter, Windows-1252/Latin-1 encoding) are rejected with raw parser messages
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `core/data.py:18-23`, `core/data.py:82-92`
- Evidence (`fmt.py`):
  - A Latin-1 or cp1252 CSV with umlauts gives `Error loading file: 'utf-8' codec can't decode byte 0xfc in position 17`. UTF-16 fails the same way. Good: no mojibake.
  - A semicolon CSV with decimal commas loads "successfully" as one column named `Panelist;Sample;Sweet;Bitter`. The user then sees a single-column mapping and no hint about the delimiter.
  - A TSV named `.tsv` is sent to `read_excel` and fails with "Excel file format cannot be determined". Its uploader would reject it anyway.
  - UTF-8 with BOM works in both loaders.
- Impact: Excel's default "CSV" on German, French or Nordic Windows is semicolon plus cp1252, so a large part of the stated audience cannot load their files directly and gets no actionable message.
- Recommendation: use `sep=None, engine='python'` (or `csv.Sniffer`) for delimiter detection. Try UTF-8-sig, then cp1252 with a caption saying which encoding was used. When only one column results, raise a message that names the delimiter.
- Effort: S
- Dependencies: none

### IO-04: `.xls` is offered by the uploader but cannot be read (xlrd not a dependency); uppercase `.CSV` fails
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `modules/rata/ui.py:108`, `modules/descriptive/workflow.py:109`, `modules/cata/ui.py:369,616` (`type=[…,'xls']`); `requirements.txt`; `core/data.py:18`
- Evidence:
  - A real OLE2 `.xls` gives `Missing optional dependency 'xlrd'. Install xlrd >= 2.0.1 …`. `xlrd` is not installed and not in `requirements.txt`.
  - `DATA.CSV` passes `endswith('.csv')` as false, goes to `read_excel`, and fails with "Excel file format cannot be determined". `load_precomputed_means` lowercases the name, so the two loaders disagree. Inferred: Streamlit accepts the upper-case extension (not verified in a browser).
  - Liking, Fusion and PrefMap accept only `csv, xlsx`, while RATA, DA and CATA also list `xls`. `.xlsm` is not accepted anywhere, although pandas reads it (`fmt2.py`).
- Impact: users following the uploader's own prompt get a developer error message.
- Recommendation: add `xlrd>=2.0.1` or drop `xls` from every `type=` list. Lowercase the extension in `load_data`. Use one shared accepted-types constant.
- Effort: S
- Dependencies: none

### IO-05: Multi-sheet workbooks: the first sheet is read silently and the user cannot choose
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `core/data.py:21`, `core/data.py:87`
- Evidence: a workbook whose sheets are `Instructions` and `Data` loads as the single column `['Info']` from `Instructions` (`fmt2.py`). No sheet picker exists and no message says which sheet was used. Title rows above the header are also not supported: the header becomes `Study X results`, `Unnamed: 1`, … with no hint.
- Impact: panel-software exports and lab templates often start with a cover sheet. The user sees nonsense columns with no explanation.
- Recommendation: when `ExcelFile.sheet_names` has more than one entry, show a sheet selectbox (default: first sheet with ≥ 2 columns) and record the sheet in `Run_Parameters`. Optionally add a "header row" number input.
- Effort: S
- Dependencies: IO-06 (record sheet)

### IO-06: `Run_Parameters` cannot reproduce a run: no date, dependency versions, commit, bootstrap settings or file fingerprint; the version stamp "1.0.0" is ambiguous
- Severity: HIGH
- Confidence: VERIFIED
- Location: `utils/export.py:334-566` (`build_run_parameters_sheet`), `core/__version__.py`
- Evidence: the exports generated for RATA, DA, CATA and Liking (see `inspect_xlsx.py` output) record `freesense_version = 1.0.0`, module, palette, file name, col_map, scale, alpha, post-hoc and module-specific options. None of them records:
  - export date and time (only the Fusion `Analysis_Info` sheet has one, `utils/export.py:1753`)
  - Python, statsmodels, scipy, pandas, numpy, scikit-learn or pingouin versions
  - git commit
  - sheet name
  - input file hash or row count
  - for RATA/DA, the CVA/RV bootstrap settings (`stats/multivariate.py:11-12`, `N_BOOTSTRAP=500`, `BOOTSTRAP_SEED=42`). CATA does record its CA seed and iterations in `Methods_Notes`.

  `git log v1.0.0..HEAD` lists 146 commits, including 2,667 inserted lines in `stats/` (for example the Type II empty-cell path), all still stamped `1.0.0`. The `requirements.txt` ranges are wide (`statsmodels>=0.14.2,<1`, `scipy>=1.13,<2`) and there is no lockfile, so two installs of "1.0.0" can differ numerically.
- Impact: a reviewer or auditor cannot tell which code or library versions produced a workbook. Today the version stamp does not identify the statistical engine: an export from the May tag and one from `HEAD` look identical but can differ (DA Type III vs Type II on empty cells).
- Recommendation: bump the version at release and on every stats change. Add rows for `exported_at` (ISO 8601, with timezone), `python_version`, versions of the key packages via `importlib.metadata`, `git_commit` when available, input file SHA-256, rows × columns read, sheet name, and bootstrap n/seed. Ship a lockfile or pinned constraints for releases.
- Effort: S
- Dependencies: decision D-1 (versioning)

### IO-07: Exported `data_source_file` can name a different module's file (Fusion, PrefMap; suspected for DA/RATA/CATA)
- Severity: MEDIUM
- Confidence: VERIFIED for Fusion/PrefMap; SUSPECTED for DA/RATA/CATA
- Location: `utils/export.py:366-373`. The global `uploaded_file` key is written by `modules/rata/ui.py:113`, `modules/descriptive/workflow.py:114` and `modules/cata/ui.py:379`.
- Evidence:
  - `build_run_parameters_sheet(w, 'Fusion', {'uploaded_file': <RATA_panel_study_X.csv>}, …)` writes `data_source_file = RATA_panel_study_X.csv`. The same happens for PrefMap. No `fusion_df_raw_name` / `prefmap_df_raw_name` key exists anywhere, so a Fusion or PrefMap export always shows whichever RATA, DA or CATA file was last uploaded, or "—". It never shows its own files, and neither the external block nor the liking file is recorded.
  - Suspected for DA/RATA/CATA, because the three modules share one global key: run DA on file A, then upload file B in RATA, return to DA, go straight to Step 8 and export. The DA workbook would record B. Confirm with an AppTest doing exactly that.
- Impact: the provenance row can be wrong, which is worse than missing.
- Recommendation: each module stores `<prefix>_df_raw_name` (plus hash) at run time, as Liking already does. Remove the global `uploaded_file` fallback.
- Effort: S
- Dependencies: IO-06

### IO-08: Export precision and typing are inconsistent: many values rounded to 3 dp, rates stored as text
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `utils/export.py:574, 615-621, 679-706, 764, 861-867, 881, 924, 937, 1813-1885`
- Evidence:
  - p-values are good: stored at full precision with `P_VALUE_EXCEL_FORMAT` on every p column found (RATA 26 + 14 + 418 + 12 + 138 cells, DA, CATA and Liking the same).
  - Means, SD, SE, CIs, F, Cochran's Q, correlations and panel-performance scores are rounded at export to 3 dp, and PLS outputs to 4 dp, with `number_format='General'`.
  - Ticking rates are stored as text (`'100.0%'`, `'91.4%'`) in `TickingRate_Wide`, `TickingRatePerRep_Wide` and `Descriptives_CLD`, so Excel cannot compute on them.
  - Other sheets (the Contrast sheets, the Liking `Acceptance` sheet) store full-precision floats with no display format.
  - Header labelling is mixed: humanised in some sheets (`Mean Intensity`, `p (Product)`), raw snake_case in others (`raw_diff`, `lsd_or_hsd`, `neg_log_p`, `tested_against`, `p_value_fdr`).
  - The Liking workbook has no `Methods_Notes` sheet, while RATA and CATA do.
- Impact: re-analysis from the workbook loses precision (3 dp of a 0-10 mean is fine for reporting but not for recomputation) and rates need parsing. The mixed column naming makes the workbook look unfinished.
- Recommendation: store full precision everywhere and use Excel `number_format` for display, the same approach the p-values already use. Write rates as numbers with a `0.0%` format. Apply one label map across builders. Add `Methods_Notes` to Liking (and to DA if intended).
- Effort: M
- Dependencies: none

### IO-09: Word/PowerPoint image exports: text becomes very small at page size
- Severity: MEDIUM
- Confidence: VERIFIED (sizes measured); legibility judgement is inferred
- Location: `utils/plot_theme.py:55-58, 152-181`
- Evidence (`render.py`, RATA figures):
  - Word preset: 1200 CSS px × scale 3 gives 3600 px PNG (554 dpi at 6.5 in). Wide preset: 2000 px × 3 gives 6000 px (667 dpi at 9 in). The resolution is ample.
  - Fonts are not scaled. At the page width the preset targets, base 17 px text is 6.6 pt (5.5 pt for wide figures), CLD footnotes and CVA/PCA loading labels at 10-11 px are 3.2-4.3 pt, and the legend in the CVA export is about 3.6 pt (visible in `img/RATA_rata_cva_biplot_word.png`).
  - kaleido writes no DPI metadata, so Word places the image at 96 dpi and the user must shrink it to the page, which gives the above sizes.
  - PowerPoint preset: 8.5 pt base at 13.33 in, minimum 5 pt.
  - SVG export embeds text elements with `font-family: Arial`, which is good.
- Impact: journal and report figures need about 7-8 pt minimum. Loading labels and legends are hard to read in print.
- Recommendation: author the Word preset at the physical page width (6.5 in × 96 = 624 px, scale 6), or scale fonts proportionally to the width ratio, with a minimum font size (for example 8 pt equivalent) for annotations. Write a pHYs/DPI chunk so the image inserts at its intended size.
- Effort: M
- Dependencies: none

### IO-10: Default palettes and fixed semantic colours are not colour-blind safe or greyscale-distinguishable
- Severity: MEDIUM
- Confidence: VERIFIED (simulation)
- Location: `utils/colours.py:20-73`, `utils/plotting.py:111-119`, `modules/liking/ui.py:990`, `modules/fusion/ui.py:733`
- Evidence (`cvd.py`, minimum pairwise ΔE2000; below about 10 is hard to tell apart):
  - Default product palette (Plotly Bold), first 6 colours: deutan 4.5, greyscale 5.9. With 11 colours: deutan 2.7, protan 2.6, and 24/55 greyscale pairs below 10.
  - `muted`: protan 0.3.
  - Default cluster palette (Set2), 4 colours: protan 1.6, greyscale 0.8.
  - `DRIVER_COLOUR_MAP`, fixed and not user-selectable: protan 1.3 (green vs orange), deutan 4.6 (green vs red), so "Robust driver" and "No discrimination" merge for deuteranopes.
  - The opt-in `colourblind` palette holds up for 6 colours (≥ 11.6 under all three CVD types) but collapses in greyscale (orange vs sky blue, 0.6).
  - `greyscale` has adjacent steps at ΔE 4.
  - Liking heatmaps default to `RdYlGn` and switch only when the user picks `colourblind`. The Fusion Q² heatmap and the Liking JAR colours are hard-coded red/green.
  - CVA/PCA products also get distinct marker symbols (good). Bars and spider lines rely on colour alone.
- Impact: about 8 % of male users cannot separate product and cluster colours in the default configuration, and printed greyscale reports lose product identity.
- Recommendation: make an Okabe-Ito or Tol palette the default, keep "bright" as opt-in, recolour `DRIVER_COLOUR_MAP` with a blue/orange/grey scheme, use a viridis or `RdBu` ramp by default for liking, and add pattern or marker redundancy for bars in the greyscale mode.
- Effort: S
- Dependencies: decision D-4

### IO-11: kaleido 0.2.1 pin is a deployment and upgrade risk
- Severity: MEDIUM
- Confidence: VERIFIED (works here); SUSPECTED (other platforms)
- Location: `requirements.txt:5`, `utils/plot_theme.py:181`
- Evidence:
  - Observed: on this host (Fedora x86_64, Python 3.14.7) `fig.to_image` works; cold start 2.8 s, then 0.2-1.8 s per image. The package bundles its own Chromium binary (`kaleido/executable/bin/kaleido`, ELF x86-64), and its `py2.py3-none` wheels do not depend on the Python version, so 3.14 is not an issue in itself.
  - Inferred: kaleido 0.2.x is no longer developed. Plotly ≥ 6.1 requires kaleido ≥ 1 (which drives a system Chrome), so the `plotly<6` and `kaleido==0.2.1` pins lock the app to Plotly 5.x.
  - SUSPECTED: kaleido 0.2.1 is widely reported to hang indefinitely on some Windows installs (the common workaround is `kaleido==0.1.0.post1`). The download callable runs on a worker thread with no timeout, so a hang would leave the button spinning. Not tested here (no Windows host).
- Impact: Windows desktop users may be unable to export images. Any Plotly upgrade breaks image export.
- Recommendation: add a timeout and a friendly error around `export_figure`. Test on Windows and macOS arm64 before release. Plan the migration to Plotly 6 with kaleido 1 (Chrome requirement documented) or keep the SVG/modebar path as the fallback.
- Effort: M
- Dependencies: decision D-2 (platforms)

### IO-12: Browser modebar download: fixed 1200×800 at scale 2 and a generic file name
- Severity: LOW
- Confidence: VERIFIED
- Location: `core/config.py:106-115`; `utils/ui_shell.py:996`
- Evidence:
  - The modebar exports every chart as `FreeSense_Plot_Export.<fmt>` at 1200×800 whatever the chart's aspect (for example 1000 px tall CVA or 1410 px tall butterfly plots are squashed or re-laid out), at 2400×1600 px for PNG. That is adequate for slides, not for print.
  - 77 of 81 `render_chart(` call sites pass `config=`. The other four fall back to Plotly's default modebar (PNG at screen size).
  - `render_chart` image names are `FreeSense_<key>_<preset>.<fmt>`, so per-attribute charts (for example the bar CLD for Acidity and for Sweetness) download under the same name.
  - Excel downloads are `FreeSense_<module>_Report_<YYYY-MM-DD>.xlsx`, so several exports on one day, or from different datasets, collide.
- Impact: overwritten or confusingly named files; distorted aspect ratios.
- Recommendation: use the figure's own height/width in `toImageButtonOptions`, and include attribute or dataset stem and time in the file names.
- Effort: S
- Dependencies: none

## Checked, nothing material found

- UTF-8 with and without BOM, including umlauts and accents in headers and values: loads correctly in both loaders. Encoding errors raise and are not cached as `None` (`tests/test_load_data.py` pins this).
- No silent mojibake for Latin-1, cp1252 or UTF-16: they error.
- Whitespace in headers is stripped. Duplicate headers become `col.1` (pandas does this itself before the explicit de-dup).
- `load_data`, `load_precomputed_means`, `clean_and_structure_data` and `build_cata_liking_long` carry `max_entries=4` and contain no `st.*` calls (the CLAUDE.md note that `load_data` calls `st.error` and returns `None` is outdated: it raises).
- Meta columns are cast to `str`. The `replicate` key being absent or `None` is handled (`core/data.py:188`).
- p-value export convention: numeric, full precision, `[<0.0001]"< 0.0001";0.0000` on every p column found in the RATA, DA, CATA and Liking workbooks. No p-value is stored as text.
- Deferred export builders run without script context. All four driven workbooks built without exception from a full AppTest run.
- Run_Parameters does record module-specific run options (exclusions, blank fill, replicate rule, CATA filter, Liking clusters), read from run records rather than live widgets.
- SVG exports keep text as text with an Arial font family. Dark-theme neutrals are swapped back for print (`_to_print_colours`).
- `example_data/` is not read by application code (grep).

## Decisions raised

- D-1 Versioning: what version string ships, and is it bumped on every change to `stats/`? Without that, the export's `freesense_version` does not identify results (IO-06).
- D-2 Supported platforms (Windows desktop? macOS arm64? hosted Linux only?) decide how urgent the kaleido risk is (IO-11).
- D-3 Locale support: is European CSV (semicolon, decimal comma, cp1252) in scope for this release, or documented as "save as UTF-8 CSV / xlsx"? At minimum the loader must refuse rather than mis-read (IO-02 is required either way).
- D-4 Default palette: switch to a colour-blind-safe default, or keep the current look with the opt-in (IO-10)?
- D-5 Export precision policy: full precision plus display formats, or rounded "report" values? The two serve different users (IO-08).

## Leads for other areas

- DA Step 1 metrics (Products 6 / Assessors 29) disagree with `da_df_long` (7 / 30) when NaN rows are present: the metric code appears to count differently from the stored frame (B05/UX).
- RATA "Run full analysis" has no try/except around `run_mixed_models`, so any PatsyError reaches the user as a traceback (B06 robustness).
- Excel formula injection in exported cells and the upload size cap: see B07.
- CLAUDE.md "Caching rules" and the data-engineer notes say `load_data` calls `st.error` and returns `None`, which no longer matches the code (B09 docs).
- `load_precomputed_means`'s `nan_affected` return value is unused by both callers; the dead contract should be wired up or removed (B06).
