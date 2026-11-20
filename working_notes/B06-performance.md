# B06 Performance and robustness

Reviewer: B06 (Claude), read-only session, commit `bcaf9f8`, 2026-09-26.

## Scope and method

What was checked: wall time of each module's "Run full analysis" pipeline and of the heavy later-step computations, at realistic and stress sizes; rerun cost of result steps; memory of a session and of the process; behaviour of the `@st.cache_data` caches across sessions; GIL contention; progress feedback and cancellation; large uploads; pathological designs; kaleido export latency.

All scratch scripts and outputs are in `/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B06/` (`gen.py` generates the data; `bench_<module>.py`, `apptest_*.py`, `patho*.py`, `hash_collision*.py`, `gil.py`, `kaleido_t.py`, `bigupload.py`; results in the `*.txt` files next to them). Every script runs with `env/bin/python` from the repo root, with `OMP_NUM_THREADS=1`.

**How the timings were taken.** Direct benchmarks call the same production functions the Run handlers call (`modules/descriptive/workflow.run_full_da_analysis` and its stages; the RATA handler body at `modules/rata/ui.py:405-446`; `modules/cata/ui._run_full_cata_pipeline`; the Liking handler body at `modules/liking/workflow.py:745-800`; `stats.pls.fit_pls` and `compute_cv_coefficient_stability` as in `modules/fusion/workflow._run_pls_fit`; `stats.prefmap.compute_prefmap`). Real Streamlit caching was left on, and `st.cache_data.clear()` was called before each repeat, so the times include cache hashing and pickling. End-to-end times come from driving `app.py` with `AppTest`, using the fake-upload pattern from `tests/test_apptest_*.py`.

**CPU caveat.** Nine other reviewers were using the same 8-core machine. The first DA run happened at load average 21. Later runs happened at load average 2.5 to 4.3. I report both where I have both, so treat all times as ranges on a loaded developer machine, not as benchmarks. At stable load, repeats agreed within about 3% (DA 34.9 s and 35.1 s; RATA 25.5 s and 25.7 s).

**Synthetic dataset sizes** (from `gen.py`; the realistic data has product effects, assessor effects, interaction and noise):

| Module | Realistic | Stress |
|---|---|---|
| DA | 20 assessors x 12 products x 30 attributes x 3 reps (720 wide rows, 21,600 long rows) | 40 x 20 x 50 x 3 (120,000 long rows) |
| RATA | 100 assessors x 8 products x 30 attributes, no reps, about 40% ticked (24,000 long rows) | 200 x 12 x 40 (96,000 long rows) |
| CATA | 150 consumers x 8 products x 40 attributes + liking (48,000 long rows) | 500 x 12 x 60 (360,000 long rows) |
| Liking | 300 consumers x 10 products, 5 JAR columns, demographics file (4 variables) | 1,000 consumers x 12 products, 8 JAR columns |
| Fusion / PrefMap | 12 products x 30 sensory variables; Y = 8 external variables or 300 consumers | UI maximum of 10,000 permutations (extrapolated) |

### Timing table

"Quiet" means load average about 3; "loaded" means about 20. Stages marked [Sn] run later, when step n is first rendered, not during Run.

| Module / size | Stage | Quiet | Loaded |
|---|---|---|---|
| **DA realistic** | End-to-end Run click (AppTest, default post-hoc = FDR) | 12.6 to 15.3 s (7 runs) | |
| | End-to-end Run click, Tukey-Kramer HSD | 36.1 s | |
| | `run_full_da_analysis`, Tukey (2 repeats) | 34.9 / 35.1 s | 97.4 s |
| | of which `compute_repeatability` (pingouin ICC) | 11.6 / 11.7 s | 34.4 s |
| | of which `generate_cld` Tukey | 20.9 / 21.2 s | 57.7 s |
| | of which `run_da_anova` | 1.1 s | 2.4 s |
| | of which discrimination + agreement + rest | about 1.2 s | about 2.8 s |
| | [S4] first visit contrast / [S6] panel perf. / [S7] diagnostics | 1.1 / 2.6 / 1.1 s | |
| | Rerun of any result step with no change | 0.02 to 0.17 s | |
| | [S5] widget interaction (PCA standardisation) | 0.17 to 0.25 s | |
| **DA stress** | `run_full_da_analysis`, Tukey | 189.6 s (ANOVA 39.5, repeatability 47.5, CLD 97.7) | |
| | [S7] `compute_da_diagnostics` / [S6] assessor summary | 27.6 / 8.4 s | |
| **DA 5 x 3 x 2 x 1,000 attributes** | `run_full_da_analysis`, FDR | 102 s (10,000 attributes extrapolates to about 17 min) | |
| **RATA realistic** | Run handler, Tukey (3 runs) | 25.5 / 25.7 / 54.2 s | |
| | of which `run_mixed_models` (30 LMM pairs) | 14.7 to 14.9 s (39.4 s in the slow run) | |
| | `generate_cld`: Tukey / FDR (default) / Fisher | 10.3 to 14.4 / 0.9 / 0.9 s | |
| | [S6] PCA, CVA / [S7] stability | 0.02 / 0.6 s | |
| **RATA stress** | Run handler, Tukey | 105.3 s (LMM 74.1, CLD 30.9) | |
| **CATA realistic** | Run (`_run_full_cata_pipeline`) | 2.7 s | |
| | [S5] contrast / [S6] CA / ellipses (500 boot) / [S7] penalty | 2.5 / 0.00 / 0.05 / 0.13 s | |
| **CATA stress** | Run / contrast / ellipses / penalty | 11.0 / 9.8 / 0.28 / 0.93 s | |
| **Liking realistic** | Run (LMM 2.1 s + Tukey CLD 0.4 s) | 2.4 s | |
| | [S3] demographic LMMs (3 variables) / [S5] AHC / k-means (n_init 50) | 2.4 / 0.03 / 0.17 s | |
| | [S6] JAR block (uncached; runs on every Step 6 rerun) / [S7] MDPREF | 0.13 / 0.01 s | |
| **Liking stress** | Run / demographic LMMs / k-means / JAR block | 4.0 / 4.8 / 0.35 / 0.23 s | |
| **Fusion** | `fit_pls`, LOO, 1,000 permutations, Y = 8 or Y = 300 | 6.9 to 12.2 s (permutation test is about 100% of it) | |
| | coefficient stability | 0.01 s | |
| | 10,000 permutations (UI maximum), extrapolated linearly | about 70 to 120 s | |
| **PrefMap** | `compute_prefmap` on 300 consumers / surface on a 50x50 grid | 0.08 / 0.01 s | |
| **Export** | kaleido: first PNG / later PNG / SVG | 0.54 / 0.11 / 0.03 s | |
| **Upload** | 194 MB CSV (468,750 rows x 103 columns): `load_data` | 1.7 s, RSS +480 MB, frame 429 MB | |
| | cache-hit rehash of the 194 MB upload on every rerun | 0.37 s | |
| | `clean_and_structure_data` on 10% of it | 0.7 s, long frame 1,064 MB (so about 10.6 GB for the full file) | |

Profiling (`prof_da.py`, cProfile, output in `prof_da.txt`):
- The Tukey time in DA is 2,310 calls to `scipy.stats.studentized_range.cdf`, each 8 to 17 ms because each one is a numerical integration (`scipy.integrate.nquad`), plus 30 calls to `.ppf` at 100 to 230 ms each.
- `compute_repeatability` spends 23.1 of its 32.1 s in 600 calls to `pingouin.intraclass_corr`, one per assessor x attribute.
- `fit_pls` (`prof_pls.py`) spends 12.19 of 12.2 s in `_permutation_test`, which runs 1,001 leave-one-out CVs.

## Findings

### PERF-01: Cached statistics return stale results after a corrected re-upload of any study with 50,000 or more long-format rows
- Severity: BLOCKER
- Confidence: VERIFIED
- Location: every `@st.cache_data` function that takes `df_long` (for example `stats/shared/frequency.py` `build_citation_matrix`, `run_cochrans_q`, `run_mcnemar_posthoc`; `stats/descriptive.py`; `stats/da_anova.run_da_anova`; `stats/mixed_models.run_mixed_models`; `stats/posthoc.generate_cld`; `stats/panel_performance.*`; `stats/multivariate.run_cva` / `calculate_panel_stability`; `stats/cata.compute_ca_ellipses`; `stats/liking.compute_liking_lmm`). The mechanism is Streamlit's hasher, `env/lib/python3.14/site-packages/streamlit/runtime/caching/hashing.py:52-54,519-533`.
- Evidence: Streamlit hashes a DataFrame of 50,000 rows or more by taking a random sample of 10,000 rows with a fixed seed (`runner.cacheHashSeed`, default 0) and hashing that sample plus the frame's shape. A change outside the sampled rows gives the same cache key, so the cached result is returned. `load_data` hashes the full upload bytes and `clean_and_structure_data` gets the small wide frame, so these two recompute. Every downstream function receives the long frame, which is over 50,000 rows for realistic studies: 150 consumers x 8 products x 50 attributes is 60,000 rows, and the RATA and DA stress sizes above are 96,000 and 120,000.
  - Stats level (`hash_collision.py`, `hash_collision_cata.py`): in a 50,000-row CATA frame I flipped 20 ticks of P02/Attr003 outside the sample. `build_citation_matrix` still returned 0.06 against a true 0.26. `run_cochrans_q` returned Q = 128.66, p = 2.2e-23, against a true Q = 98.11, p = 3.8e-17. The DA descriptives showed the same behaviour: a cached mean of 5.207 against a true 5.116.
  - End to end in the real app (`apptest_stale.py`): one AppTest session ran CATA on a 150 x 8 x 50 file. A second session in the same server process, representing the user reloading the page and uploading a corrected file with 25 cells fixed, ran again. Output: `P02/Attr003 citation rate shown after corrected upload: 0.427; correct: 0.593` and `Cochran's Q Attr003 shown: 124.41; correct: 151.89`. There was no warning, and the new file really was different (`raw data differ: True`).
  - For a single changed cell, the chance of falling outside the sample is 1 - 10,000/n: 83% at 60,000 rows and 90% at 100,000. The cache is process-wide, so the stale entry is also served to any other session whose data differs only outside the sample.
- Impact: the typical correct-and-rerun workflow can silently show the old numbers: frequency tables, Cochran's Q, ANOVA, LMM, CLD letters and panel performance. They then go into the Excel export. This affects CATA consumer studies of ordinary size (100 or more consumers with 50 or more attributes, or several products) and any large DA or RATA panel.
- Recommendation: stop letting Streamlit sample. Two options:
  - Pass `hash_funcs={pd.DataFrame: _full_frame_digest}` to every `st.cache_data` in `stats/` and `core/data.py`, where `_full_frame_digest` returns `pd.util.hash_pandas_object(df, index=True).values.tobytes()` plus the column names and dtypes. That is about 50 ms per million rows. A shared decorator (`core/cache.py::cache_stats = functools.partial(st.cache_data, max_entries=8, hash_funcs=...)`) keeps it in one place.
  - Or compute a content digest once in the Run handler and pass it as an explicit argument, with `_df_long` underscore-prefixed so Streamlit does not hash it.
  - Add a regression test that runs a cached function on a 60,000-row frame, changes one row outside the sample, and asserts that the result changes.
- Effort: S
- Dependencies: none

### PERF-02: DA "Run full analysis" crashes when any assessor x attribute has fewer than 5 ratings (2 products x 2 sessions, or 3 x 2 with one missed product)
- Severity: BLOCKER
- Confidence: VERIFIED
- Location: `stats/panel_performance.py:251-264` (`compute_repeatability`, the optional pingouin CI block), called from `modules/descriptive/workflow.py:74`.
- Evidence: `pg.intraclass_corr` asserts "Data must have at least 5 non-missing values". The surrounding `except` catches `(LinAlgError, ValueError, RuntimeError, KeyError, IndexError)` but not `AssertionError`, and the outer `except` at line 266 does not catch it either, so it propagates out of `run_full_da_analysis`.
  - Through the real app (`apptest_patho.py`): 10 assessors x 2 products x 5 attributes x 2 sessions gave `exception: ['Data must have at least 5 non-missing values.'] | complete: False`. The same design with 3 sessions completed.
  - Stats level (`patho_tb.py`, `patho2.py`): 30 assessors x 2 products x 2 reps also fails. So does 12 assessors x 3 products x 2 reps where one assessor missed one product, which is the unbalanced case the last three commits set out to support. 4 products x 2 reps with one missing session passes.
- Impact: a crash of the core DA workflow for legitimate designs: two-product tests with duplicate sessions, and ordinary 3-product studies with a single missed evaluation. The user sees a Python exception and cannot get any result. The failing code only computes an "approximate" CI that the primary ICC does not need.
- Recommendation:
  - Catch `AssertionError`, or better, guard on `len(sub) >= 5 and sub[replicate_col].nunique() >= 2`, and set the approximate CI to NaN.
  - Add an AppTest for 2 products x 2 sessions and for 3 x 2 with one missing assessor x product cell.
  - See PERF-03: removing this block from the Run path also removes three quarters of DA run time.
- Effort: S
- Dependencies: none

### PERF-03: DA and RATA run times are dominated by two avoidable costs (pingouin CI loop; per-pair numerical-integration Tukey p-values)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location:
  - `stats/panel_performance.py:251-264` (600 `pg.intraclass_corr` calls at realistic size).
  - `stats/posthoc.py:362-391` and `:624` (`1.0 - stats.studentized_range.cdf(q_obs, k, df)` once per pair per attribute, plus `.ppf` once per attribute). The same pattern is at `stats/posthoc.py:230,251` (RATA crossed Tukey) and `stats/contrast.py:211-228`.
- Evidence: see the timing table and `prof_da.txt`.
  - DA realistic, default FDR: 12.6 to 15.3 s end to end. `compute_repeatability` is 11.6 s of it, and 23 of its 32 s under profiling is pingouin.
  - Tukey adds 21 s (57.7 s under load).
  - DA stress with Tukey: 190 s. RATA realistic with Tukey: 25 to 54 s, of which the LMM loop is 15 to 39 s and the Tukey CLD 10 to 14 s. FDR CLD is 0.9 s.
  - `sr.py`: one `studentized_range.cdf` call costs 7 to 12 ms and one `.ppf` call 100 to 130 ms, independent of the q value.
  - By contrast, Liking's Tukey (`stats/liking.py:836`, `.sf` per pair on 45 pairs) takes 0.4 s, because there is only one "attribute".
- Impact: a 15 to 55 s wait at realistic size and about 3 min at stress size, with no working progress indicator (PERF-05). The wait is annoying but tolerable locally. On a shared server it is multiplied by the number of concurrent users (PERF-04).
- Recommendation:
  - (a) Move the approximate pingouin CI out of Run: compute it lazily in the Step 6 detail tab, or drop it. The primary ICC is already computed by the OLS formula above it.
  - (b) Compute Tukey p-values in one vectorised pass per attribute. Options: interpolate `studentized_range.sf` on a small q grid per (k, df) and cache it; or use `statsmodels.stats.libqsturng.psturng`, which is table-based and vectorised, with a documented accuracy check against the scipy value in `tests/`. Keep the one `.ppf` per (k, df), since it is shared by all attributes with the same k and df.
  - (c) Optionally, fit the RATA and DA per-attribute models in a `concurrent.futures.ProcessPoolExecutor`. Threads will not help (PERF-04).
- Effort: M
- Dependencies: PERF-02 (same code block)

### PERF-04: No resource limits for a hosted deployment: default 200 MB upload, no size caps, GIL-bound compute in one process, small shared caches
- Severity: MEDIUM (HIGH if the app is hosted for more than a handful of concurrent users; LOW for local single-user installs)
- Confidence: VERIFIED for the measurements; the extrapolation to N users is Inferred
- Location: `.streamlit/config.toml` (no `server.maxUploadSize`, so Streamlit's default of 200 MB applies, per the orientation note); `core/data.py:8-37` (`load_data`, `max_entries=4`); `max_entries=8` on each stats cache; no row, attribute or product caps anywhere in Step 1 validation.
- Evidence:
  - GIL (`gil.py`): `sys._is_gil_enabled()` is True on this Python 3.14 build. Four `run_da_anova` calls took 4.18 s one after another and 4.39 s in four threads (0.95x). The statsmodels, pingouin and scipy `nquad` work is Python-level and does not run in parallel. Streamlit runs every session as a thread in one process, so N users pressing Run together each wait about N times as long, and every other user's 0.05 to 0.25 s reruns slow down too.
  - Memory at realistic sizes is not the problem (`apptest_mem.py`). RSS was 262 MB after imports and 362 MB after one full DA session (Run plus every step). Six sessions in the same process reached 373 MB, about 2 MB per extra session. `st.session_state` after a DA run is 1.1 MB pickled, of which `da_df_long` is 0.76 MB.
  - Large uploads are the problem (`bigupload.py`). A 194 MB CSV (468,750 rows x 103 columns) parses in 1.7 s into a 429 MB frame, and RSS rises by 480 MB. `load_data` keeps up to 4 such frames in its cache (about 1.7 GB), and Streamlit also keeps the upload bytes per session. The upload is re-hashed on every rerun (0.37 s per interaction). Melting 10% of it gave a 1.06 GB long frame, so pressing Run on the full file needs about 10.6 GB for `df_long` alone, before the cached copy that `clean_and_structure_data` stores. I did not run the full melt, to protect the shared machine.
  - A 1,000-attribute DA file ran for 102 s; 10,000 attributes extrapolates to about 17 minutes.
  - B07 already measured a 0.3 MB xlsx that decompresses to 86 MB, taking 46 s and 475 MB in `load_data`. Referenced, not repeated.
  - Cache eviction: the stats caches hold 8 entries each for the whole process. With more than 8 active datasets, step-level results that are only cached and not stored in session state are evicted and recomputed on a later rerun. At realistic and stress sizes that means `compute_da_diagnostics` (0.8 to 27.6 s), `summarise_assessor_performance` (2.5 to 8.4 s), CVA, stability and contrast. Inferred from `max_entries=8` and the call sites at `modules/descriptive/workflow.py:2324, 1874`; not measured under real concurrency.
- Impact: one user with a large or decompression-bomb file can exhaust memory or CPU for everyone on a hosted instance, and a handful of simultaneous Tukey runs makes the whole app unresponsive. For a local single-user install this is mostly irrelevant.
- Recommendation:
  - Set `server.maxUploadSize` to something like 20 MB, since realistic sensory files are well under 1 MB.
  - Validate rows, attributes and products in Step 1 against documented limits (for example 100,000 long rows or 500 attributes), with a clear message.
  - For hosting: run several Streamlit replicas behind a sticky load balancer, or move Run pipelines into a process pool; size memory at roughly 400 MB per process plus the upload limit times 4 for the `load_data` cache.
  - Consider `max_entries` of 16 or more, or TTLs, once PERF-01 makes entries cheaper to verify.
- Effort: S (config and caps); L (process isolation)
- Dependencies: deployment decision (see below)

### PERF-05: Long runs cannot be cancelled, DA's progress display is fake, and touching a widget mid-run discards the run
- Severity: MEDIUM
- Confidence: VERIFIED (code reading for the status text); Inferred from Streamlit source (interrupt semantics, not reproduced in a live browser)
- Location: `modules/descriptive/workflow.py:377-393`; `modules/cata/ui.py:987-996`; `modules/fusion/workflow.py:1560-1597`; Streamlit `runtime/scriptrunner/script_runner.py:493-557`.
- Evidence:
  - DA writes all five progress lines ("Running mixed-effects ANOVA…", "Running post-hoc comparisons…", "Computing panel performance…", "Running multivariate analysis (PCA)…") before the single blocking `run_full_da_analysis` call. The user therefore sees every stage as "done" at once for the whole 13 to 190 s. The line about PCA is also wrong, since PCA is not computed in Run.
  - CATA sets "Step 2/3: frequency tests + CLD…" only after those tests have finished.
  - RATA's labels are sequential and accurate.
  - Fusion runs up to 10,000 permutations (about 70 to 120 s) under a bare `st.spinner("Fitting PLS model…")`.
  - There is no cancel control. Streamlit can only interrupt a script at a "yield point", which is any `st.*` call that enqueues a message (`_maybe_handle_execution_control_request`, `runner.fastReruns` default True). Inside a stats function such as the 30-attribute LMM loop there is none, so the Stop menu item and widget clicks wait for the current cached function to return.
  - The next yield point (the next cached function's spinner, or the next `st.write`) raises `RerunException`. Everything after it, including `st.session_state.update(results)` and `set_module_analysis_complete`, is skipped. The run is lost and the user must press Run again. Stages that finished are cached, so the second attempt is shorter.
- Impact: on 30 s to 3 min runs, users will click around, lose the run without explanation, and have no idea how long is left.
- Recommendation:
  - Replace the up-front `st.write` lines in DA with `status.update(label=...)` between the stages. That means inlining the stage calls from `run_full_da_analysis`, or giving it a progress callback.
  - For per-attribute loops (LMM, CLD, ICC), accept an optional `progress` callable, called outside the cached function or via `st.progress` in the handler.
  - Show the permutation count and an estimated duration next to the Fusion permutation input.
  - Say in the status label that interacting with the page cancels the run.
- Effort: M
- Dependencies: PERF-03 (shorter runs reduce the need)

### PERF-06: DA "Run" crashes for a single-attribute dataset
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `stats/panel_performance.py:130-139` (`compute_discrimination`, `groupby('attribute').apply(_rank_column)`).
- Evidence: through the real app, 10 assessors x 5 products x 1 attribute x 2 sessions gave `exception: ['Cannot set a DataFrame with multiple columns to the single column score'] | complete: False` (`apptest_patho.py`). With one group, `groupby.apply` returns a wide frame rather than a Series. This is the same line that raises the pandas `FutureWarning` noted in orientation. RATA with one attribute works (`patho.py`).
- Impact: a single-attribute DA (for example a sweetness-only study, or a user who excludes all but one attribute) cannot be analysed at all.
- Recommendation: use `disc_df.groupby('attribute')['neg_log_p'].rank(pct=True)`, filled from `range_score` where `neg_log_p` is all NaN, instead of `apply`, and add an AppTest for one attribute. The 1-product case is correctly blocked in Step 1 ("At least 2 products are required") and 1 assessor completes with a clear status.
- Effort: S
- Dependencies: none

### PERF-07: `render_chart` docstring misdescribes kaleido behaviour
- Severity: LOW
- Confidence: VERIFIED
- Location: `utils/ui_shell.py:965-966`.
- Evidence: the docstring says kaleido 0.2.1 "starts a subprocess per export". Measured (`kaleido_t.py`): one persistent child process was reused for all 8 exports (`child_procs=1` throughout). The first PNG took 0.54 s and later PNGs 0.11 s. Four concurrent exports were serialised (0.12, 0.23, 0.34, 0.44 s; 0.46 s wall).
- Impact: none functionally. Export latency is not a concern, but the comment will mislead anyone sizing a hosted deployment.
- Recommendation: correct the docstring: one shared kaleido process, exports serialised behind its lock, about 0.1 s each after a cold start of about 0.5 s.
- Effort: S
- Dependencies: none

## Checked, nothing material found

- Rerun cost on result steps (DA via AppTest): 0.02 to 0.25 s for unchanged reruns and widget interactions. Step first visits take 0.1 to 2.6 s. Tabs and expanders are `.open`-gated as CLAUDE.md claims, so steps do not rebuild every figure.
- Per-session memory at realistic sizes is small (about 2 MB per extra session; 1.1 MB of session state).
- CATA (Run 2.7 s; 11 s at 500 consumers x 60 attributes), Liking (2.4 s; 4.0 s at 1,000 consumers), PrefMap (0.1 s) and CA bootstrap ellipses (0.05 to 0.28 s) are fast.
- The CA bootstrap is cached separately from the ellipse fit (0.01 s to switch axes). Liking's uncached JAR block (0.13 to 0.23 s per Step 6 rerun) is acceptable.
- kaleido first-call latency (0.54 s) is acceptable; see PERF-07.
- LMM convergence on the synthetic RATA data: 100% converged at both sizes.
- The 1-product DA case is blocked in Step 1; the 1-assessor DA case completes with a clear status per attribute; the RATA 1-product and 1-attribute cases complete.

## Decisions raised

1. **Deployment model** (local install vs hosted multi-user). PERF-04 is LOW locally and HIGH when hosted. Hosting needs, at minimum: an upload limit, size caps, a replica or process-pool strategy, and a memory budget. The measured budget is about 400 MB base per process, plus up to 4x the upload limit for the `load_data` cache, plus the melted long frame at about 50x the CSV size.
2. **Supported study size.** State the tested envelope, for example "up to 50 assessors x 20 products x 60 attributes", and enforce or warn above it. The current behaviour for 1,000+ attributes is a silent multi-minute run.
3. **Whether the approximate pingouin ICC CI is worth keeping.** It is about 75% of the default DA run time and the cause of PERF-02; it also bears on the GPL question already raised in orientation.

## Leads for other areas

- B01/B04: `stats/posthoc.py` uses `1.0 - studentized_range.cdf(...)` while `stats/liking.py` uses `.sf(...)`. They were numerically identical in my spot checks (`q` from 3 to 40, k = 12, df = 418), so this is not a finding, but one helper would remove the duplicated Tukey code paths (PERF-03).
- B09: DA status text says "mixed-effects ANOVA" and "multivariate analysis (PCA)" during Run; the first is the wrong method name and the second is not computed there (`modules/descriptive/workflow.py:389-391`).
- B05/UX: `@st.cache_data` functions without `show_spinner=False` show Streamlit's default spinner text "Running `generate_cld(...)`." with internal function names during Run and step renders. SUSPECTED: seen in the Streamlit source (`cache_utils.py:686-760`), not observed in a browser.
- B04: my harness call of `cached_compute_contrast(..., module='Liking')` returned in 0.00 s on a cold cache; I did not check whether it returned an empty frame for my arguments. Not investigated further.
- B07: the 0.37 s re-hash of a 194 MB upload on every rerun compounds the decompression-bomb case they measured.
