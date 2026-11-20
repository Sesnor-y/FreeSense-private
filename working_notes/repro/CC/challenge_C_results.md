# Challenge C results (independent reproduction)

All scripts in this folder; run from the repo root with `env/bin/python <script>`. No repo, venv or git state touched.

| ID | Verdict | Recommended severity | One-line reason |
|---|---|---|---|
| PERF-01 | REPRODUCED | BLOCKER (narrow trigger) | Corrected re-upload in the same session silently shows the old Cochran's Q (p 0.80 instead of 0.012); needs >= 50,000 long rows and a same-shape correction that misses the 10,000-row sample |
| PERF-02 | REPRODUCED | BLOCKER (one-line fix) | DA "Run full analysis" raises an uncaught pingouin AssertionError for 2 products x 2 sessions, or 3 x 2 with one missed product; pingouin is in requirements.txt so the default install is affected |

## PERF-01: stale cache for large long frames

### Mechanism (Streamlit 1.64 `env/lib64/python3.14/site-packages/streamlit/runtime/caching/hashing.py`)
- Lines 52-54: `_PANDAS_ROWS_LARGE = 50_000`, `_PANDAS_SAMPLE_SIZE = 10_000`.
- Lines 519-533 (DataFrame branch): hashes `df.shape`; if `len(df) >= 50_000` it replaces the frame with `df.sample(n=10_000, random_state=_sample_seed())`; then hashes `hash_pandas_object(df.dtypes)` (dtypes plus column names, since the Series index is hashed) and `hash_pandas_object(sample)` (values plus index labels of the sampled rows only).
- `_sample_seed()` (lines 88-127) reads `runner.cacheHashSeed`, default 0; the project sets no seed and uses no `hash_funcs` anywhere.
- So: same shape, same dtypes, same column names, and all changed rows outside the fixed 10,000 sampled positions gives an identical key. The threshold is `>=` 50,000, not `>`.
- `UploadedFile` (lines 646-653) is hashed by name, `tell()` and the full `getvalue()` bytes, so `load_data` recomputes on a corrected file. `clean_and_structure_data` receives the wide frame (rows = assessors x products x reps, well under 50,000), so it also recomputes and yields a genuinely new `df_long`. The stale hit happens at every downstream `@st.cache_data` function that takes `df_long`.
- Nested caches compound it: `build_citation_matrix` calls the cached `build_citation_counts`, so clearing only the outer function still returns the stale matrix (observed in my first attempt).

### Stats-level reproduction (`perf01_stats.py`, uses the real `clean_and_structure_data`)
`env/bin/python perf01_stats.py 150 8 50` (CATA, 60,000 long rows; 20 P02/Attr003 ticks flipped 0 -> 1 at unsampled positions):
```
long rows 60000 / flipped cells 20 raw differ True / long differ True
P02/Attr003 before 0.267 cached after 0.267 true after 0.4
Q Attr003 cached [3.80, p=0.802] true [12.37, p=0.0889]
```
`perf01_stats.py 100 8 63` (50,400 rows): citation 0.3 cached vs 0.5 true; Q 3.67 (p 0.817) cached vs 21.62 (p 0.0030) true, i.e. a significance flip.
Control `150 8 40` (48,000 rows, below threshold): no collision possible (whole frame hashed).

### End-to-end in the real app (`perf01_apptest.py`)
One AppTest session, CATA, 150 consumers x 8 products x 50 attributes. Upload is faked the same way `tests/test_apptest_cata.py` does (patched `render_data_upload_section` + `load_data`); the re-upload fires the real `_reset_cata_upload` on_change.
```
long rows 60000 flipped 25
first upload                                (0.2667, [Q 3.80, p 0.802])
analysis_complete after re-upload reset:    False
corrected upload (same session, app shows)  (0.2667, [Q 3.80, p 0.802])
corrected upload after cache clear (truth)  (0.4333, [Q 18.00, p 0.0120])
```
No warning is shown. The re-upload reset pops only session-state keys; nothing in `core/`, `modules/`, `utils/` or `stats/` clears `st.cache_data`, so the reset path does not help. The cache is process-wide, so another session with a frame differing only outside the sample would also be served the entry.

### Trigger size and likelihood
- Condition: long rows = assessors x products x replicates x attributes >= 50,000, same shape after the correction.
- CATA: 150 x 8 x 50 = 60,000; 300 x 6 x 30 = 54,000; 200 x 6 x 42 = 50,400. The bundled bread set (161 x 6 x 31 = 29,946) is below it. This is the realistic module for the trigger (consumer panels).
- RATA: e.g. 120 consumers x 8 x 53. Possible with large consumer RATA panels.
- DA: trained panels (12 x 8 x 3 x 20 = 5,760) are an order of magnitude below; practically not affected.
- Liking: one row per consumer x product; not affected in practice.
- Probability that a correction of k independent cells is missed: roughly (1 - 10,000/n)^k. One cell at 60,000 rows: 83%; 5 cells: 40%; 25 cells: 1%. My 25-cell case collided only because I placed the edits outside the sample on purpose. Realistic hits are therefore single-typo or few-cell corrections, which is exactly the "I spotted a mistake and fixed it" workflow. A correction that changes the row count, a column name or a dtype always recomputes.

### Severity
The rubric's BLOCKER test is "could produce incorrect scientific results without warning"; this does, including a p-value that flips across alpha in the real app. The trigger is narrow (large CATA/RATA studies, small same-shape correction, same server process), so a reasonable reviewer could argue HIGH; I keep BLOCKER because the failure is silent and the fix is cheap (e.g. `hash_funcs={pd.DataFrame: <full hash_pandas_object digest>}` on the df_long-taking caches, or pass a full content digest argument).

## PERF-02: DA crash on small replicated designs

### Reproduction via the pipeline function (`perf02.py`)
Uses `core.data.clean_and_structure_data(..., module='Descriptive')` then `modules.descriptive.workflow.run_full_da_analysis`. 5 attributes, scores 0-10.
```
10x2prod x2rep:                 AssertionError: Data must have at least 5 non-missing values.  @ stats/panel_performance.py:253 (raised in pingouin/parametric.py:1063)
10x2prod x3rep:                 OK
30x2prod x2rep:                 AssertionError (same)
12x3prod x2rep, A0 missed P1:   AssertionError (same)
12x3prod x2rep balanced:        OK
12x4prod x2rep, A0 missed P1:   OK
```
With `PINGOUIN_AVAILABLE = False` (`perf02.py nopg`) all six cases complete. pingouin 0.6.1 is installed and `requirements.txt:11` lists `pingouin>=0.5.4,<1.0.0`, so the default install crashes.

### Exact cause
`stats/panel_performance.py` `compute_repeatability`, the call `pg.intraclass_corr(...)` at lines 253-258. pingouin asserts at least 5 non-missing values per (assessor x attribute) subset (products x reps: 2 x 2 = 4, or 3 x 2 minus one missed product = 4). The inner `except` (line 262) catches `LinAlgError, ValueError, RuntimeError, KeyError, IndexError` and the outer one (line 266) catches `LinAlgError, ValueError, RuntimeError`; neither catches `AssertionError`. `modules/descriptive/workflow.py:393` calls `run_full_da_analysis` with no try/except, so the user gets a Streamlit exception box and the analysis is not marked complete.

### Real app (`perf02_apptest.py`)
```
10x2x2: exception: ['Data must have at least 5 non-missing values.'] | da_analysis_complete: None
10x2x3: exception: [] | da_analysis_complete: True
```

### Severity
Crashes a core workflow (the only DA "Run" button) for designs the module otherwise supports, including the unbalanced case the recent commits targeted (3 products x 2 sessions with one missed product). Not a silent-wrong-result bug, and the designs are small, but the rubric puts "crashes a core workflow" at BLOCKER. The fix is one token (add `AssertionError`, or skip the CI when fewer than 5 values). No user-side workaround except adding a session/product or editing the data.
