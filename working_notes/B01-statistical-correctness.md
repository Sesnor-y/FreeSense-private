# B01 Statistical correctness

Reviewer: B01 (statistical correctness). Commit `bcaf9f8`. Read-only; scratch scripts in `/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B01/` (`h.py` harness, `t_da.py`, `t_da2.py`, `t_cons.py`, `t_lik.py`, `t_seg.py`, `t_pls.py`, `t_pls2.py`, `t_edge.py`).

## Scope and method

- Read `stats/da_anova.py`, `stats/posthoc.py`, `stats/contrast.py`, `stats/mixed_models.py`, `stats/shared/lsmeans.py`, `stats/shared/frequency.py`, `stats/cata.py` (contrast, CA ellipses, penalty), `stats/liking.py` (LMM, CLD), `stats/jar_penalty.py`, `stats/segmentation.py`, `stats/mdpref.py`, `stats/pls.py` (CV, permutation, rank caps), parts of `stats/panel_performance.py`, and the module call sites that feed them.
- Ran production stats functions headless (Streamlit stubbed with `validation/_common._stub_streamlit`) with the project venv. No app code was modified.
- Independent references used (R is not installed):
  - DA ANOVA: my own numpy least-squares (RSS differences, sum-to-zero design) for all three paths: complete Type III, complete-but-unequal-replicate Type III, empty-cell Type II additive, and no-replicate additive with empty cells. Dataset: `example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx`, plus variants with sessions or whole cells deleted.
  - Liking pairwise df: statsmodels OLS RCBD (`intensity ~ C(product) + C(consumer)`) on synthetic 10 consumer x 6 product panels.
  - PLS Q²: independent LOO loop (raw data autoscaled within each fold, constant-in-fold columns dropped, sklearn `PLSRegression`).
  - Segmentation: 20 pure-noise datasets with no true segments.
- Frozen R references: `tests/test_validation_pins.py` asserts DA F and p within 1e-3 absolute, CLD share-a-letter partition identical, ICC within 1e-3; RATA chi² within 1e-2, p within 1e-4, decisions identical; Liking LS means within 1e-8, LRT within 1e-3, CLD partition identical; JAR within 1e-8 or better; Fusion coefficients within 1e-6, VIP within 1e-3; PrefMap AICc within 1e-8. These tolerances are meaningful for what they cover, but each covers **one complete, balanced dataset**, so the empty-cell DA path, unbalanced Liking designs, small-panel df behaviour, RATA/Liking contrasts and segmentation are not reference-covered. I did not re-run the pins (the suite passed in orientation).

## Findings

### STAT-01: Cluster ANOVA tests the partition it was built from, so "significant" stars appear on pure noise
- Severity: HIGH
- Confidence: VERIFIED
- Location: `stats/segmentation.py:57-93` (`_cluster_anova`), called from `compute_ahc_clusters` (l.211) and `compute_kmeans_clusters`; rendered as ★ markers by `modules/liking/workflow.py:114-139` (`_cluster_profile_caption`), l.1505-1540 (AHC tab) and the k-means tab.
- Evidence: the one-way ANOVA per product compares the clusters on the same liking scores the clusters were formed from. Script `t_seg.py`: 20 datasets of 100 consumers x 6 products, iid N(6, 1.5) rounded to 1 to 9, no segment structure. AHC (Ward, k = 2, raw scores) flagged `[5, 4, 3, 5, 3, 5, 3, 3, 3, 4, 4, 5, 4, 6, 5, 5, 4, 3, 4, 2]` of 6 products significant at alpha = 0.05. A valid test would flag about 0.3 per dataset. The caption says "★ = product liking differs significantly across segments (one-way ANOVA on raw scores, p < α)" with no caveat; `Statistical_Methods_README.md` (around l.1610) presents the ANOVA as the test of absolute level without mentioning selection.
- Impact: users will read ★ as evidence that segments genuinely differ in liking of a product. The p-values are invalid by construction (post-selection inference); they will be significant for almost any partition, including noise. This can drive product or segmentation decisions.
- Recommendation: stop presenting these as inferential tests. Either drop the p-values/stars and show effect sizes (between-cluster range, eta²) labelled descriptive, or state plainly next to the chart that the tests are descriptive because the clusters were formed to differ. If an inferential check is wanted, use a split-sample or permutation-of-the-whole-clustering procedure.
- Effort: S (caveat and relabel) / M (valid alternative)
- Dependencies: none

### STAT-02: Liking contrast uses df = n_consumers - n_products, disagreeing with the CLD and with the correct RCBD df
- Severity: HIGH
- Confidence: VERIFIED
- Location: `stats/liking.py:289-290` (`df_satterthwaite = max(1, n_c - n_p)`); consumed by `stats/contrast.py:292-312` (Liking contrast p-value, CI, HSD critical value, Hedges' J) and `stats/contrast.py:628-640` (FDR family); `compute_liking_cld` (`stats/liking.py:786-814`) instead uses a per-pair Welch formula.
- Evidence (`t_lik.py`): balanced synthetic panels, 10 consumers x 6 products. The contrast uses df = 4; the CLD uses per-pair df of about 2(n-1) = 18; the correct residual df of the balanced RCBD (equal to lme4/emmeans Satterthwaite on complete data) is (10-1)(6-1) = 45. The SEs agree exactly (LMM 0.5193 vs RCBD 0.5193), so only the df differs. P2 vs P5: p = 0.0255 at df 45 against 0.0820 in the contrast. Across 30 datasets x 3 post-hoc methods x all reference/comparison pairs, the contrast's significance disagreed with the CLD letters in **442 of 2700** comparisons (16%). When n_consumers <= n_products + 1 the df floors at 1, and the Hedges' g correction `J = 1 - 3/(4·df - 1)` becomes 0, so g is reported as 0 for every pair. The hedochoc validation cannot catch this because at 222 consumers every df choice gives the same decisions.
- Impact: in small or moderate consumer panels (pilot tests, trained-panel hedonics, central-location tests with many products) the contrast step is heavily conservative, and it contradicts the CLD shown in the previous step. This is the old F-16 finding. It is only partly fixed: the CLD moved to per-pair df, but the contrast did not, and neither uses the RCBD df. The UI caption "Fallback degrees of freedom" (`modules/liking/workflow.py:1001-1007`) hides that the contrast uses the fallback df as its **primary** df.
- Recommendation: derive one df for both CLD and contrast. For complete data use (n_c - 1)(n_p - 1). For incomplete data compute Satterthwaite or Kenward-Roger per contrast, or use the containment df from an OLS RCBD fit. Remove the per-pair Welch formula, which treats LS means as independent groups. Fix Hedges' J to use a df consistent with the SD used.
- Effort: M
- Dependencies: none (lead (a) from another reviewer confirmed)

### STAT-03: RATA Tukey contrast uses a different error term from the RATA Tukey CLD
- Severity: HIGH
- Confidence: VERIFIED
- Location: `stats/contrast.py:447-491` (RATA path: paired SE, df = n-1, studentized range with k_total) against `stats/posthoc.py:177-258` (`_rcbd_tukey_decisions`: pooled RCBD residual MS, df (J-1)(P-1)); docstring `stats/contrast.py:23-24` claims flags always match `generate_cld()`.
- Evidence (`t_cons.py`, sensochoc run as RATA, all 6 references x 5 comparisons x significant attributes, 420 pairs): Tukey had **16 mismatches** between contrast `significant` and the pairwise/CLD `Reject H0`, in both directions. Examples: MilkF choc1 vs choc2, CLD adj p = 0.163 (not significant), contrast significant; Sticky choc1 vs choc3, CLD adj p = 0.016 (significant), contrast not significant. FDR and LSD had 0 mismatches for RATA. DA had 0 mismatches for all three methods.
- Impact: in RATA with Tukey selected, the contrast chart and the CLD letters can contradict each other for the same pair. The RCBD Tukey path is the one validated against emmeans, so the contrast is the wrong one.
- Recommendation: in the RATA Tukey branch of `compute_contrast`, reuse `_rcbd_tukey_decisions`' error MS and df (or call it) for both the ribbon half-width and the decision. Add a test asserting contrast-vs-CLD agreement for every module x method, like `t_cons.py`.
- Effort: S
- Dependencies: none

### STAT-04: PLS CV Q² collapses when a predictor is constant inside a training fold (in-fold scaling divides by ~1e-17)
- Severity: HIGH (beta module)
- Confidence: VERIFIED
- Location: `stats/pls.py:325-331` (`x_sd = np.where(np.isfinite(x_sd) & (x_sd > 0), x_sd, 1.0)`, same for `y_sd`), used by Q², permutation test and bootstrap CI.
- Evidence (`t_pls.py`, `t_pls2.py`): n = 8 products, 4 predictors, one predictor non-zero in a single product (for example an ingredient in only one recipe). After global autoscaling, the LOO fold that omits that product has a column whose in-fold SD is 6.0e-17, not 0, so the guard passes and the column is multiplied by ~1e16. Over 20 seeds, `fit_pls(...)['q2']` against an independent LOO: seed 4 gives -14.519 vs 0.889, seed 9 gives -11.046 vs 0.560, seed 2 gives -2.547 vs 0.733 (median absolute difference 0.46). Changing only the guard to `> 1e-10` reproduces the independent values exactly for every seed. No warning is raised: the per-fold effective-rank cap sees a full-rank scaled matrix.
- Impact: Q², the Q²-per-component curve used for component selection, and the permutation p-value can be grossly wrong, with no warning, on composition or formulation blocks where an ingredient appears in one product. That is a common Fusion input.
- Recommendation: use a relative tolerance (for example `x_sd > 1e-8 * max(1, global_sd)`). Better, drop constant-in-fold columns from that fold's fit and prediction. Add a regression test with a one-product indicator column.
- Effort: S
- Dependencies: none

### STAT-05: Consumer segmentation with "standardise" on crashes when any consumer rates every product the same
- Severity: MEDIUM
- Confidence: VERIFIED (stats layer); SUSPECTED for the exact UI rendering
- Location: `stats/segmentation.py:27-35` (`_standardise_rows` z-scores rows, and a flat rater gives NaN); `compute_ahc_clusters` l.193 and `compute_kmeans_clusters` l.294; call sites `modules/liking/workflow.py:1357-1364` and around l.1574 have no try/except.
- Evidence: 60 x 6 random matrix with one row set to 7. `compute_ahc_clusters(..., standardise=True)` raises `ValueError: The condensed distance matrix must contain only finite values`. `compute_kmeans_clusters(..., standardise=True)` raises `ValueError: Input X contains NaN`. Both succeed with `standardise=False`. A random-noise run on integer 1 to 9 scores also hit this by chance (`t_seg.py`).
- Impact: flat raters are common in consumer panels. Turning the toggle on raises an uncaught exception in Step 4 (Inferred: Streamlit shows a traceback).
- Recommendation: exclude zero-variance consumers before standardising, report how many were excluded (they carry no pattern information), and guard the call site.
- Effort: S
- Dependencies: none

### STAT-06: DA with a replicate column that has a single session: every attribute ends in an error row
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `stats/da_anova.py:285-298` (the interaction model always runs when `replicate` is mapped); validator `modules/descriptive/ui.py:109-117` only warns that ICC is unavailable.
- Evidence (`t_da2.py`): sensochoc restricted to Session 1 with `replicate='Session'` mapped. Every attribute returns `significant='Error'` with status `error: r_matrix performs f_test for using dime...`. No CLD, contrast or letters follow. The same data with replicate unmapped analyses correctly.
- Impact: a user who maps a session column that happens to be constant (a single-session study, or a filtered file) gets an empty analysis and a cryptic status hidden in an expander. The driver scatter shows only "no valid p-values".
- Recommendation: when every assessor x product cell has one observation, treat the design as non-replicated (set `replicate=None` for the ANOVA) and say so. Also handle partially replicated designs where residual df is tiny.
- Effort: S
- Dependencies: none

### STAT-07: Liking LMM never checks `.converged`; the convergence warning can only fire when every optimiser raises
- Severity: MEDIUM
- Confidence: VERIFIED (code path); SUSPECTED (frequency of silent non-convergence on real data)
- Location: `stats/liking.py:227-252` (loop breaks on the first fit that does not raise; `convergence_warning = False` is never updated), `_failure_return` l.219; UI `modules/liking/workflow.py:1021-1024`.
- Evidence: statsmodels `MixedLM.fit` warns but does not raise on non-convergence, and all warnings are suppressed (`warnings.simplefilter('ignore')`). Neither `result_reml.converged` nor `result_ml.converged` is read anywhere in `stats/liking.py`. RATA (`stats/mixed_models.py:73-84`) does check it. On my synthetic data the fits converged, so I did not observe a silent failure.
- Impact: a non-converged REML/ML fit would feed LS-means SEs, the CLD and the LRT with no warning shown.
- Recommendation: check `.converged` on both fits, fall through to the next optimiser when it is False, and set `convergence_warning` when the accepted fit did not converge.
- Effort: S
- Dependencies: none (lead (c) confirmed)

### STAT-08: MDPREF silently mean-imputes missing consumer x product cells
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `modules/liking/workflow.py:3052-3056` and `3220-3221` (`liking_wide.fillna(liking_wide.mean(axis=0))`); `stats/mdpref.py` requires imputation by the caller.
- Evidence: code read. No UI text or `Statistical_Methods_README.md` passage mentions imputation (grep for "imput" finds only the code comment). The Liking module accepts incomplete designs (balance report, `pct_missing_cells`).
- Impact: in incomplete-block consumer tests each consumer's unseen products are placed at their personal mean. That shrinks product separation on the map and biases consumer vectors, with nothing telling the user. It also contradicts the project's stated principle of never filling missing cells before a PCA.
- Recommendation: disclose the imputation and its extent (the share of cells imputed). Prefer excluding consumers below a completeness threshold, or use an EM/iterative PCA (missMDA-style).
- Effort: S (disclose) / M (method)
- Dependencies: none

### STAT-09: Tukey "fallback" to uncorrected paired t-tests is described as conservative
- Severity: LOW
- Confidence: VERIFIED (code); trigger is rare
- Location: `stats/posthoc.py:398-403`, `416-421`, `762-765`, `786-791`, `826-829`.
- Evidence: when the DA error MS is unavailable, or RATA RCBD df < 1, Tukey silently becomes uncorrected paired t (Fisher LSD). The comments call this "conservative"; it is the least conservative option. The error MS is taken from `full_df['MS']`, which is rounded to 4 decimals (`stats/da_anova.py:421`). An attribute whose true MS is below 5e-5 (proportions or very small scales) therefore resolves to 0, falls back, and loses multiplicity control. `t_edge.py` showed the fallback label "Paired t-test (Tukey-Kramer fallback)" in the pairwise table, while the CLD gives no indication.
- Impact: rare, but it gives anti-conservative letters under a Tukey label.
- Recommendation: do not round MS/SS in `full_df` (round for display only). Make the fallback apply a Bonferroni or Holm correction and surface the switch.
- Effort: S
- Dependencies: none

### STAT-10: DA docstring says the interaction pre-test alpha has no effect on product p-values
- Severity: LOW
- Confidence: VERIFIED
- Location: `stats/da_anova.py:135-141`.
- Evidence: sensochoc, `alpha_interaction` 0.10 against 0.01 changes `p_product` on 6 of 14 attributes (MilkF 3.7e-40 vs 2.4e-51; Granular 9.1e-05 vs 1.1e-06). Decisions did not flip on this dataset. The behaviour is correct by design (the pre-test selects the error term); the claim is wrong.
- Impact: misleads maintainers and anyone reading the API docs.
- Recommendation: rewrite it as "selects the error term, and therefore the product F, p and df".
- Effort: S
- Dependencies: none (lead (e) confirmed)

### STAT-11: Kendall's W UI caption says ties are not corrected, while the code applies the tie correction
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/liking/workflow.py:1015-1020` against `stats/liking.py:381-404` (tie-corrected denominator, B.17).
- Evidence: the caption reads "Kendall's W is not adjusted for ties; … W may be slightly overestimated" whenever tied ranks exist. The code applies the Kendall/Wallis tie correction, and `ref_kendall.csv` matches to 1e-8.
- Impact: tells users the opposite of what was computed.
- Recommendation: replace the caption with "tie-corrected (n ties)".
- Effort: S
- Dependencies: none

### STAT-12: Liking Tukey ribbon labelled "±LSD zone"
- Severity: LOW
- Confidence: VERIFIED
- Location: `utils/plotting.py:1219-1220`, `1266-1269` (checks `('Tukey HSD', 'Tukey-Kramer HSD')`; the Liking label is `'Tukey HSD (Studentized Range)'`).
- Evidence: code read. `stats/contrast.py:205-207` does treat the Liking label as HSD, so the drawn width is an HSD width under an LSD legend.
- Impact: mislabelled chart.
- Recommendation: test `use_hsd` the way `contrast.py` does, or pass the label through.
- Effort: S
- Dependencies: none (lead (f) confirmed)

## Checked, nothing material found

- **DA ANOVA, all paths** (`t_da.py`, `t_da2.py`): complete Type III sum-to-zero; complete with unequal replicate counts; empty cells with replicates (Type II additive product SS, interaction = additive minus full SS, pure-error residual); no replicates with empty cells. F, p, interaction p and error df match the independent least-squares computation to display precision on all 14 attributes in every path. The conditional F-test pools correctly (interaction MS and df when p_int < alpha_int, otherwise residual). Assessor is tested against the same denominator. The prior F-01 (Type II vs III), F-13 and F-14 (moment Satterthwaite removed, exact OLS df) are fixed.
- **DA post-hoc and contrast consistency**: Tukey, FDR and LSD CLD, pairwise table and contrast gave 0 disagreements over 420 pairs (`t_cons.py`). The SE uses per-observation n = J·R, consistent with emmeans. The empty-cell LS means and contrast variance `L(X'X)⁻¹L'` are correctly derived.
- **RATA LMM**: ML fits for the LRT, random intercept per assessor, replicates averaged before fitting (no double counting), cg then Nelder-Mead fallback with the convergence status recorded. RATA FDR and LSD contrasts agree with the CLD. Edge data (`t_edge.py`): an all-zero attribute gives `not_converged` with p = 1; an attribute with no residual variance gives an `Error` row; one assessor using an attribute is analysed normally.
- **CATA**: Cochran's Q listwise-deletion diagnostics are reported. McNemar exact below 25 discordant pairs and uncorrected χ² at or above (documented, validated). Within-attribute BH for the post-hoc; within-comparison-product across attributes for the contrast (as documented). Paired-proportion Wald SE formula (Agresti) is correct. CA ellipses project onto the original basis with no re-decomposition, resampling consumers (a documented design choice rather than FactoMineR's multinomial default), with a fixed seed. Penalty: Welch t, independence caveat present.
- **JAR**: two separate correction families (too low, too high); independence caveat present for the pooled "All products" view (`modules/liking/workflow.py:2912-2917`), so lead (b) is **not confirmed**.
- **p-values**: no p-value rounding in the stats layer in the files read (F, SS and MS are rounded, see STAT-09). All t-based tests are two-sided.
- **pandas FutureWarning** at `stats/panel_performance.py:138`: `_rank_column` reads only `neg_log_p` and `range_score`, never the grouping column, so the pandas 3 change (grouping columns excluded from apply) does not change results.
- **`pearsonr` ConstantInputWarning** (`panel_performance.py:362`): gives r = NaN, which is shown as missing rather than flagged. Acceptable.
- **Fusion Q-residual / leverage 95th-percentile line** (lead (d)): the behaviour is as described, but it is disclosed in `Statistical_Methods_README.md:2217` ("flags roughly 1 product in 20 by construction"). This is a design and UX choice, not a computation error. Passed to B09/UX to check the in-app wording.
- **PLS** permutation p uses (count + 1)/(n + 1) on finite draws; the dropout count is surfaced; Hotelling T² uses pinv. Prior F-22 and F-23 are addressed.

## Decisions raised

1. Whether Fusion and PrefMap (beta) ship in this release. STAT-04 affects Fusion only.
2. Whether segmentation keeps p-values at all (STAT-01), or becomes descriptive.
3. The Liking df policy (STAT-02): complete-design RCBD df and Kenward-Roger/Satterthwaite for incomplete designs would need either a new dependency or an in-house implementation.
4. CATA/JAR penalty independence: shipping Welch with a caveat is a documented D-6 decision. Whether that is acceptable for release is a scientific call.

## Leads for other areas

- `modules/descriptive/workflow.py:758-760` caption says the conditional F-test is "on the assessor term"; it is on the interaction term (B09).
- DA step text calls the model "Mixed-effects ANOVA" and "Two-way mixed ANOVA"; it is fixed-effects OLS with a conditional error term (B09).
- `tests/test_validation_pins.py` covers only complete, balanced datasets; there is no pin for the DA empty-cell path, unbalanced Liking, or contrast-vs-CLD agreement (B06).
