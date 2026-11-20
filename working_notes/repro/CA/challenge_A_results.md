# Challenge A results (independent reproduction)

All scripts are in this folder (`CA/`) and were written from scratch. They run from the repo root with `env/bin/python`. Test inputs were built from `example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx` by `mkfiles.py` into `CA/files/`. No repo files, venv or git state were touched, and nothing under `data/`, `working_notes/` or `B*/` was read.

AppTest harness: `harness.py` + `run_io.py`. It patches `ui_shell.render_data_upload_section` and `core.data.load_data` the same way `tests/test_apptest_{da,rata}.py` do. The difference is that `load_data` here calls the **real** (unwrapped) loader on the file bytes, so parsing is exercised for real.

## Summary

| ID | Verdict | Claimed | Recommended | One-line reason |
|---|---|---|---|---|
| STAT-01 | REPRODUCED | HIGH | MEDIUM | Post-selection ANOVA gives about 3.7 to 4 of 6 products ★ on pure noise. But it is a widespread descriptive convention, and a copy/caveat fix removes the harm. |
| STAT-02 | REPRODUCED | HIGH | MEDIUM (HIGH if panels < ~30 are in scope) | The contrast df (n_c − n_p) and the CLD df (Welch, about 2(n−1)) are both wrong; the correct df is (n_c−1)(n_p−1). The effect is large at 10 consumers (13% disagreement) and small at 60 (1.2%). |
| STAT-03 | REPRODUCED | HIGH | MEDIUM | Exactly 16/420 RATA-Tukey mismatches, in both directions. Both decisions can be defended; the real problem is the broken consistency promise on one screen. |
| STAT-04 | REPRODUCED | HIGH (beta) | HIGH (beta) | An in-fold SD of 6e-17 passes the `> 0` guard. Q² falls silently (for example −3.05 against 0.53). |
| FUNC-01 | REPRODUCED | BLOCKER | BLOCKER | Products whose names contain "Var"/"Cov" silently get the reference LS mean. |
| FUNC-02 | REPRODUCED | HIGH | HIGH | All-text attributes in DA give a `KeyError: 'mean_bias'` traceback. Same root cause as IO-02. |
| FUNC-03 | REPRODUCED | HIGH | HIGH | Duplicated rows flip every interaction test to p ≈ 0, switch the error term and change 4 pairwise verdicts, with no warning. |
| FUNC-04 | REPRODUCED | HIGH | BLOCKER (merge with IO-01) | Blank product cells become product "nan": DA results change silently (Type II path, 5 verdicts) and RATA crashes. |
| FUNC-05 | REPRODUCED (`.CSV` by code reading, not in a browser) | HIGH | HIGH | `;`/tab CSVs load as one column with no message; latin-1, `.xls` and `.CSV` all fail. |
| IO-01 | REPRODUCED (the CLD change needs Tukey; default FDR shows no verdict change) | BLOCKER | BLOCKER (merge with FUNC-04) | Trailing empty rows give a phantom product/assessor "nan" in DA outputs, and RATA crashes. |
| IO-02 | PARTLY REPRODUCED | HIGH | HIGH | RATA 7.5 becomes 0 and DA drops the value, both under a misleading "blank cells" warning. The means-table claim "NaN warning never shown" is wrong: `drop_incomplete_attributes` does warn. |
| IO-06 | REPRODUCED | HIGH | MEDIUM | The metadata really is missing, but it cannot corrupt results. It is an audit/reproducibility gap, and the user can record it by hand. |

Root-cause groupings:
- **FUNC-04 and IO-01 share one root cause.** `core/data.py:193-195` casts meta NaN to the string `'nan'`, and `load_data` never drops rows that are entirely blank. File them as one finding; one fix covers both.
- **FUNC-02, IO-02 and the decimal-comma bullet of FUNC-05 share one root cause.** There is no locale-aware numeric parsing, and there is no "attribute column is not numeric" check in DA Step 1. RATA has only the >50% check at `modules/rata/ui.py:256-262`. FUNC-02 is the crash symptom; IO-02 is the silent-partial symptom.
- The other FUNC-05 sub-items (delimiter sniffing, encoding, `.xls` without xlrd, case-sensitive `.csv`) are separate defects in the same function (`core/data.py:17-21`).
- **STAT-02 and STAT-03 are the same class of defect** (the contrast engine does not share the CLD's error term/df) but sit on different code paths (Liking LMM path against RATA path). They need separate fixes.

---

## STAT-01: cluster ANOVA on the partition it was built from

**Verdict: REPRODUCED.**

Script `s01.py`: 20 datasets of 100 consumers × 6 products, iid N(6, 1.5) clipped to 1 to 9 (rounded in the first run), `k = 2`, alpha 0.05. The count is of products flagged `significant` in the returned cluster-ANOVA frame.

```
compute_ahc_clusters raw     [3,2,3,4,3,3,6,5,5,5,3,4,4,5,4,3,6,3,4,4] mean 3.95 (expected 0.3)
compute_kmeans_clusters raw  [5,5,3,4,3,2,5,4,4,4,4,3,3,5,4,4,4,2,3,2] mean 3.65
compute_ahc_clusters std     [5,4,2,4,3,4,5,2,5,4,4,3,3,3,4,5,4,3,4,5] mean 3.8
```

**Reasoning.** The reasoning is sound. The clustering maximises between-cluster separation on exactly the variables the ANOVA then tests, so the F statistics do not follow an F distribution under H0 (double dipping / selective inference). Standardised clustering does not rescue it: row-standardised partitions still correlate with raw product scores.

The caption (`modules/liking/workflow.py:133-135`) says "★ = product liking differs significantly across segments". `Statistical_Methods_README.md` has no selection caveat for this ANOVA. It does have one elsewhere, for panel performance at l.1123, which shows the authors know the concept.

**Severity.** I recommend MEDIUM rather than HIGH. The partition itself is correct, and reporting per-cluster ANOVAs is common practice in sensory software and papers, so users are not misled about *which* products separate the segments. They are misled only about the p-value's meaning. The fix is cheap: relabel the ★ as descriptive ("largest separation"), or drop the p-value and give effect sizes / F as descriptive.

**Incidental new defect (not in A's list).** `compute_ahc_clusters(..., standardise=True)` raises `ValueError: The condensed distance matrix must contain only finite values` if any consumer gave the same score to every product (a straight-liner). `zscore` returns NaN for that row. The call sites (`modules/liking/workflow.py:1360`, `:1573`) have no try/except and there is no upstream filter (`s01c.py`). Straight-liners are common in consumer data, so this is a crash of the Liking segmentation step when the standardise toggle is on. hedochoc has 0 such consumers, so the example data does not show it.

## STAT-02: Liking contrast df = n_consumers − n_products

**Verdict: REPRODUCED.** The code at `stats/liking.py:290` sets `df_satterthwaite = max(1, n_c − n_p)`. It is consumed at `stats/contrast.py:297, 303, 311`.

**Deriving the correct df.** The model is y_ij = μ + τ_j + u_i + e_ij with random consumer intercept, balanced and complete. A product difference τ_j − τ_k is a pure within-consumer contrast: the u_i cancel. Its variance is 2σ²_e / n_c, and σ²_e is estimated from the consumer × product residual stratum with (n_c − 1)(n_p − 1) df. The Satterthwaite df for the contrast is therefore exactly (n_c−1)(n_p−1). This is what lmerTest/emmeans report on complete data with a positive variance component, and it is the same as the RCBD OLS residual df.

- n_c − n_p is not a meaningful df for this design.
- The CLD's per-pair Welch df, (v1+v2)² / (v1²/(n1−1) + v2²/(n2−1)) = 2(n−1) when balanced, treats the two products as independent samples. It is also wrong.

Both errors are conservative.

Script `s02.py`, 10 consumers × 6 products, random product and consumer effects:

```
contrast df 4.0   RCBD resid df 45.0
SE diff LMM 0.5158157  RCBD 0.5158154      (identical: only the df is wrong)
disagree 352 of 2700   (30 datasets × 3 methods × 6 refs × 5 comparisons; contrast 'significant' against CLD letter overlap)
```

Example (seed 0, reference P1, comparison P3): p = 0.126 at df 4, 0.070 at df 18 (CLD), 0.060 at df 45 (correct).

Floor case (7 consumers, 6 products): `df_satterthwaite = 1.0`, and `hedges_g = 0.0` for every comparison, because J = 1 − 3/(4·1 − 1) = 0.

Scaling with panel size (`s02n.py`, 15 datasets): at n_c = 30 (df 24 against 145) there were 28/1350 disagreements; at n_c = 60 (df 54 against 295) there were 16/1350.

**Severity.** I recommend MEDIUM rather than HIGH. The numbers are genuinely wrong, but conservative, and at typical consumer-test sizes (60 to 120 or more) the effect on decisions is about 1%. HIGH is justified if small hedonic panels (pilot or trained panels under 30) are a supported use case: there the contrast contradicts the CLD letters in about 13% of comparisons and Hedges' g collapses. Fix both paths together by using (n_c−1)(n_p−1), or better a real Satterthwaite/Kenward-Roger df, in the contrast **and** in `compute_liking_cld`.

## STAT-03: RATA Tukey contrast and CLD use different error terms

**Verdict: REPRODUCED exactly.**

Script `s03.py`: sensochoc through `clean_and_structure_data(module='RATA')`, `calculate_descriptives`, `run_mixed_models` and `generate_pairwise_table`. It then runs `compute_contrast(module='RATA')` for all 6 references × 5 comparisons, keeping the (attribute, pair) entries present in the pairwise table.

```
Tukey HSD                 pairs 420 mismatches 16
  ('MilkF','choc1','choc2', contrast 'Yes', CLD reject False, adj p 0.163)
  ('Sticky','choc1','choc3', contrast 'No', CLD reject True,  adj p 0.016)
  ('Sweetness','choc2','choc6', contrast 'No', CLD reject True, adj p 0.046)
FDR (Benjamini-Hochberg)  pairs 420 mismatches 0
Fisher LSD (Uncorrected)  pairs 420 mismatches 0
```

**Should the two error terms agree?** Yes, given the codebase's own contract. The module docstring (`stats/contrast.py:23-24`) says the `significant` flag "is always consistent with the chosen correction, matching the CLD letters produced by `generate_cld()`". The two paths differ as follows:

- **CLD** (`posthoc._rcbd_tukey_decisions`): the textbook Tukey for an RCBD. It uses a pooled residual MS from `intensity ~ product + assessor` on assessor means, with df (J−1)(P−1). This assumes sphericity (compound symmetry) and is the right family-wise procedure.
- **Contrast** (`contrast.py:447-491`): a hybrid of a per-pair paired SE (sd(d)/√n, df n−1) with a studentized-range quantile for k_total. That is not a standard procedure. Each pair gets its own variance estimate on 28 df, and the SR quantile is applied on top.

The pair-specific variance can be much smaller or larger than the pooled one (MilkF choc1/choc2: significant by the paired SE, adjusted p 0.16 by the pooled one). So the disagreement is structural, not rounding. FDR and LSD agree only because the CLD also uses paired t-tests for those.

**Severity.** I recommend MEDIUM. Neither answer is indefensible statistically, it affects only RATA with Tukey (about 4% of pairs), and the CLD / pairwise table remain available. It does contradict itself on one screen, the contrast table shows `cld_ref`/`cld_comp` next to `significant`, and the documented guarantee is false. The fix is to route the RATA Tukey contrast through the same RCBD MS/df.

## STAT-04: PLS in-fold scaling blows up near-constant columns

**Verdict: REPRODUCED.**

Script `s04.py`: n = 8, 4 predictors, with column 4 non-zero in exactly one product (value U(1, 5)). Y is 2 columns driven by X1 and X2 plus noise. Data is autoscaled with `stats.data_fusion.autoscale`, then `fit_pls(Xs, Ys, 2, 'loo', run_permutation_test=False)['q2']` is compared with an independent LOO that uses the same in-fold scaling but guards `sd > 1e-10`.

```
seed  app_q2   independent
0     -3.051   0.526
2     -0.353   0.322
5     -0.371   0.468
7     -2.424   0.247
9     -1.101   0.466
11    -0.154   0.451
(9 of 20 seeds identical; median |diff| 0.08, max 3.6)
in-fold SD of the constant column: 5.9959e-17
```

**Mechanism confirmed.** The 7 remaining autoscaled values are bit-identical, but `np.std` of them is about 6e-17 because of rounding in the mean. `np.where(x_sd > 0, …)` keeps it, so the column is multiplied by about 1e16. The training column becomes O(1) rounding noise, and the held-out value becomes about 1e16. `effective_rank` sees a full-rank matrix, so no warning is raised.

The same `_compute_q2_cv` feeds the permutation test and the bootstrap CI (`stats/pls.py:460, 611`), so those are contaminated too. Any sparse design variable triggers it: an ingredient present in one recipe, or a 0/1 factor with a single level-1 product. The Fusion module has no guard against near-constant columns.

**Severity.** HIGH (beta) is right. Q² is the headline validity metric, and here it is silently wrong in a realistic composition design.

## FUNC-01: LS means wrong when a product name contains "Var" or "Cov"

**Verdict: REPRODUCED.**

Script `f01.py` runs hedochoc through `compute_liking_lmm`, first as-is and then with products renamed:

```
     product   ls_mean       raw
0     Covent  5.765766  5.765766
1       Dark  5.626126  5.626126
2       Milk  5.905405  5.905405
3      Plain  5.765766  5.765766
4  Variety A  5.765766  5.328829   <- equals intercept
5  Variety B  5.765766  5.689189   <- equals intercept
```

With `choc1..6` the LS means equal the raw means. The cause is `stats/liking.py:258-261`, which filters parameter names by substring. `C(_product)[T.Variety A]` contains "Var", so its column is dropped from X, and the covariance rows for those products are built from the intercept alone. The CLD, the contrast and the export all inherit this. The test is case-sensitive, so "variety" is safe but "Variant", "Varietal", "Coventry", "Cover" and "Covid" are not.

The fix is to use `result_reml.fe_params.index`.

**Severity.** BLOCKER is right: the results are silently wrong under ordinary product naming.

## FUNC-02: DA crash when no attribute is numeric

**Verdict: REPRODUCED** (AppTest, `run_io.py da:eu_comma_all.csv`). The input is sensochoc with every attribute written as a quoted decimal comma (`"7,5"`), comma-delimited.

```
step1: [warning] **4872 blank cells detected** across 14 attribute columns ... missing observation
after run: [exception] 'mean_bias'
  stats/panel_performance.py:551 compute_scale_usage -> KeyError: 'mean_bias'
```

Step 1 metrics look normal (29 / 6 / 14 / 2). DA has no non-numeric check; RATA has the >50% one. 4872 = 348 × 14, so *every* cell is reported as "blank", which is a misleading diagnosis.

**Severity.** HIGH is right. It crashes a core workflow with a traceback on a common European export format. Not BLOCKER, because no wrong numbers are produced.

## FUNC-03: duplicated rows silently change DA results

**Verdict: REPRODUCED.**

`files/dup.csv` is sensochoc concatenated twice. AppTest shows Step 1 metrics unchanged (29 assessors, 6 products, **2** replicates) and no message before or after the run. Direct comparison (`da_cmp.py`, FDR):

```
                clean        dup
MilkF      p_interaction 0.0528   0.0
Bitterness p_interaction 0.126    0.0     tested_against Residual -> Interaction, F 59.9 -> 49.9
Sweetness  p_interaction 0.518    0.0     tested_against Residual -> Interaction
pairwise verdict changes among real products: 4 of 210
```

**Mechanism.** Exact duplicates make the within-cell residual pseudo-replicated (half the within-cell deviations are zero), which deflates MS_residual and inflates every interaction F. In RATA the replicate cells are averaged, so the results are unchanged.

**Severity.** HIGH is right. Arguably BLOCKER, since the app changes scientific output silently, but the defect is in the user's data, and a duplicate check (assessor × product × replicate key count > 1) is the fix.

## FUNC-04: blank product cells become level "nan"

**Verdict: REPRODUCED.** Input `files/nanprod.csv` is sensochoc with `Product` blanked in 3 rows.

- **DA (AppTest):** there is no message. Metrics show "Products 6", while `da_df_long` products are `['choc1'..'choc6', 'nan']`. Direct comparison (`da_cmp.py`): every attribute switches to `ss_type = 'II (empty cells)'`, MilkF F goes from 83.09 to 82.52, and **5 of 210** pairwise verdicts among the real products change (for example Bitterness choc2/choc6 adjusted p goes from 0.035 to 0.064).
- **RATA (AppTest):** Step 1 shows Products 7 and "Unbalanced design (Min: 3, Max: 29)". Run then gives `[exception] factor contains missing values  intensity ~ C(Prod_Safe)` (PatsyError).

**Severity.** I recommend **BLOCKER** rather than HIGH: DA gives silently different scientific results. This is the same root cause as IO-01 and should be merged with it.

## FUNC-05: brittle file reading

**Verdict: REPRODUCED.** The `.CSV` case is confirmed by reading Streamlit's code, not in a browser.

`load_check.py` calls the unwrapped `core.data.load_data` on an uploaded-file-like BytesIO:

```
semicolon.csv -> (348, 1) ['Panelist;Session;Product;...']
tab.csv       -> (348, 1) ['Panelist\tSession\t...']
latin1.csv    -> ERR Error loading file: 'utf-8' codec can't decode byte 0xfc in position 156
UPPER.CSV     -> ERR Error loading file: Excel file format cannot be determined, you must specify an engine manually.
xlrd not installed  (and not in requirements.txt); uploaders at modules/rata/ui.py:108, descriptive/workflow.py:109, cata/ui.py:369,616 advertise 'xls'
```

In DA through AppTest, the semicolon file renders no error or warning. The mapping selectboxes offer only `['Select…', 'Panelist;Session;Product;…']`, so the user is stuck with no explanation.

For `.CSV`, Streamlit 1.64's `enforce_filename_restriction` (`streamlit/elements/lib/file_uploader_utils.py:144-157`) lower-cases both the allowed types and the filename, and browsers match `accept` case-insensitively. An upper-case `.CSV` is therefore accepted, but `load_data` then routes it to `read_excel`.

**Severity.** HIGH is right. Semicolon CSV is Excel's default in much of continental Europe, and the user gets no diagnosis. Nothing here gives wrong numbers; the silent-wrong part is IO-02.

## IO-01: trailing empty rows create phantom "nan"

**Verdict: REPRODUCED.** The claim of 3 CLD verdict changes holds only with Tukey.

Input `files/trailing.csv` is sensochoc plus two lines of 16 commas. `load_data` returns (350, 17) with all-NaN last rows.

- **DA (AppTest):** the only message is "28 blank cells detected"; metrics show Products 6, Assessors 29. `da_df_long` has products `[choc1..6, 'nan']` and **30** assessors. `da_cld_df` contains rows such as `MilkF nan abcde` (letters for a product with no data). `da_rv_df` has 30 rows against 29, and `da_agree_df`/`da_scale_df` differ from the clean run.
- **Verdicts (`da_trail.py`):**
  - Default FDR and LSD: 0 CLD verdict changes. The ANOVA is identical, because the all-NaN rows drop out of the OLS.
  - Tukey-Kramer: **3 changes**: Bitterness choc4/choc6, MilkF choc2/choc6, Sweetness choc2/choc6. The phantom product raises k from 6 to 7.
- **RATA (AppTest):** after zero-fill the phantom rows pass validation. Step 1 shows Products 7, Assessors 30, Replicates 3 and "Unbalanced (Min: 1, Max: 29)". Run gives `factor contains missing values` (PatsyError).

**Severity.** BLOCKER is right when merged with FUNC-04. Deleted-row artefacts are very common in Excel exports. On the default FDR path the damage is visible junk rows plus altered panel-performance frames, not changed product verdicts, so the BLOCKER rests mainly on the Tukey and blank-product-cell cases.

## IO-02: decimal-comma numbers zero-filled, dropped, or silently omitted

**Verdict: PARTLY REPRODUCED.** Input `files/eu_comma_35.csv` has 35 CocoaA cells written as `"x,5"`.

- **RATA (AppTest):** Step 1 warning: "35 blank cells detected … filled with 0". After the run, CocoaA has **36 zeros** against 1 in the clean file. Reproduced. The warning is present but misdiagnoses the cause: they are not blank cells.
- **DA (AppTest):** "35 blank cells detected … missing observation"; CocoaA has 35 NaN. Reproduced.
- **Means table (`means.py`, cocktail sensory means):**
  - An all-decimal-comma column (`color.intensity`) stays object dtype and is silently removed by the numeric-column filters at `fusion/workflow.py:536` and `prefmap/workflow.py:339`. **Reproduced.**
  - A mixed column (6 of 16 comma cells) gets 6 NaN, and `nan_affected` is returned but unused (grep confirms only the tuple unpacking at `prefmap/workflow.py:313` and `fusion/workflow.py:363`). **However**, both modules then call `drop_incomplete_attributes` (`fusion/workflow.py:522-530`, `prefmap/workflow.py:324-332`). That shows `st.warning("Missing values in the sensory means — left out of the analysis …: odor.intensity")`. So the claim that the NaN warning is never shown is **wrong** in effect. The user is warned, although the warning says "missing values" where the true cause is unparseable text, and the whole attribute is dropped rather than just the cells.

**Severity.** HIGH is right: RATA silently turns real ratings into zeros under a misleading message. It has the same root cause as FUNC-02.

## IO-06: Run_Parameters cannot reproduce a run

**Verdict: REPRODUCED** (by inspection).

- `core/__version__.py` is `"1.0.0"`.
- `git rev-list --count v1.0.0..HEAD` returns 146.
- `git diff --shortstat v1.0.0..HEAD -- stats/` returns "16 files changed, 2667 insertions(+), 844 deletions(-)".

`build_run_parameters_sheet` (`utils/export.py:334-566`) writes the version, module, status, palette, file name, col_map, scale/alpha/post-hoc and module-specific options. It writes **no** timestamp; the only `datetime` is in the Fusion `Analysis_Info` sheet at l.1739/1753. It also writes no Python or package versions, no commit, no sheet name, no file hash or row count, and no RATA/DA CVA/RV bootstrap `N_BOOTSTRAP=500` / `BOOTSTRAP_SEED=42` (`stats/multivariate.py:11-12`). CATA's CA seed is recorded (l.2127, 2345).

`requirements.txt` gives ranges only (`statsmodels>=0.14.2,<1.0.0`, `scipy>=1.13.0,<2.0.0`), and there is no lockfile.

**Severity.** I recommend MEDIUM rather than HIGH. This cannot corrupt a result or lose data. It weakens auditability, and the user can record the missing facts themselves. The version stamp is a release-process issue: bump the version at release. The bootstrap seed and the dependency versions are the most valuable additions, and they are cheap.
