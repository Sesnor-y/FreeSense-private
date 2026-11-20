# Reference-product contrast: audit and fix plan

Audit 2026-10-06, on `main` at `d58c1ab` (plus the uncommitted FDR caption fix in DA and RATA from 2026-10-05). Covers the reference contrast in all four modules that have one: DA (Step 4), RATA (Step 5), Liking (Step 4), CATA (Step 5). Fusion and PrefMap have no contrast step.

The numbers in this document come from `working_notes/repro/contrast/contrast_audit.py`. Run it from the repository root with `env/bin/python`. It runs every product as the reference against all the others, on every bundled dataset, for every method each module offers. Each pair therefore appears twice in its counts, once per direction.

**Order of work (owner, 2026-10-06):** first make the statistics and the visualisation correct, then streamline and restyle the step.

**Status (2026-10-06): complete.** Phases A to E are done (reports in §7). Phase A corrected CON-05 and added CON-20 and CON-21. Phase B built the many-to-one engine. Phase C finished the display and the export (D-C15 to D-C20). Phase D made one renderer for the four modules and streamlined the step (D-C21 to D-C24). Phase E updated the user documentation. Deferred by decision: small multiples (D-C24), the QMC speed-up (D.6), the HTML report.

---

## 1. What the contrast is for

The user picks **one sample** and compares it with a chosen set of others. The sample might be:

- a control or benchmark, compared with test products;
- a new prototype, compared with the current line samples;
- a sample of particular interest, to see quickly on which attributes it differs and by how much.

Every one of these is a **many-to-one** question: "how does each of these products compare with the reference?" None of them asks "which products differ from which?", which is what the Step 3 letters answer.

**The one visual rule.** For every row of the contrast, three things must agree:

> **a star (\*) ⇔ the bar is in full colour ⇔ the drawn interval excludes zero**

The number of stars grades the same adjusted p-value that drives the decision. Today this rule is broken in every module (§4).

---

## 2. Decisions

| ID | Decision | Source |
|---|---|---|
| D-C1 | The contrast step shows **no CLD letters**. Its question is the reference comparison only. Significance is shown by stars, colour and the CI error bars. | Owner, 2026-10-06 |
| D-C2 | Selecting comparison products **only changes what is displayed**, never the statistics. The multiplicity family is fixed by the design, not by what is ticked. This prevents changing the family until a borderline result flips. | Owner, 2026-10-05 |
| D-C3 | **The family is many-to-one, now.** Within each attribute, the family is every other product compared with the reference (m = k − 1 tests, where k is the number of products with data on that attribute). The method chosen in Step 1 maps to its many-to-one form: **Tukey → Dunnett**, **FDR → BH over the k − 1 comparisons**, **LSD / uncorrected → no adjustment**. The contrast and the Step 3 letters may then legitimately differ, and the page says so in one sentence. | Owner, 2026-10-06 |
| D-C4 | **CATA uses the same family as the other modules**: within each attribute, across the k − 1 comparisons with the reference. Today CATA corrects within each comparison product across attributes. | Owner, 2026-10-06 |
| D-C5 | **The z-score view divides by the panel-noise (error) SD** of the attribute, not by the SD of the product means. | Owner, 2026-10-06 |
| D-C6 | **The profile (spider) tab drops the ribbon.** On each comparison product's line, a point is drawn filled (with its stars) when that product differs significantly from the reference on that attribute, and hollow otherwise. The decision is the same one the bars use. | Owner, 2026-10-06 |

| D-C7 (MA-1) | **CATA uses a hybrid test and interval.** Where fewer than 25 consumers are discordant, the exact McNemar test decides and **no interval is drawn**; the row carries an `interval_note` ("too few discordant consumers for an interval; decided by the exact test"). From 25 discordant consumers up, the asymptotic McNemar test (no continuity correction) decides and Tango's score interval is drawn at the adjusted level. That interval inverts the same test, so the two agree by construction. Rejected: the asymptotic test everywhere, which made 50 squashes pairs significant from counts as small as 4 vs 0. | Owner, 2026-10-06 |
| D-C8 (MA-2) | **Holm is applied as Bonferroni in the contrast step.** This covers the profiling "no pooled error term" fallback and CATA's Holm option; Step 3 keeps real Holm. A caption says so ("Holm is applied as Bonferroni here so every difference has an interval"). Every row keeps a matching interval. | Owner, 2026-10-06 |
| D-C9 (MA-5) | **RATA keeps the paired t-tests for FDR and LSD.** They use the assessors who rated both products, with their own SE and df n − 1, and are robust to pairs differing in variability. Dunnett (the Tukey slot) uses the blocked model, as Tukey does today. Consequences: (1) the table shows the **paired means** (reference and comparison over the same assessors) and the number of assessors, so the difference always subtracts; (2) on attributes with empty cells, the estimate changes when the user switches between Dunnett and FDR/LSD, and the caption says so; (3) the spider keeps the module's means, with a caption on attributes with empty cells; (4) the methods reference's claim (line ≈811) that the contrast uses the module's LS means is corrected for RATA FDR/LSD. Measured cost of the rejected alternative: 6–7 of 210 sensochoc LSD decisions would have changed. | Owner, 2026-10-06 |
| D-C10 (MA-4) | **One standardised difference, on the test's own error SD,** with the small-sample correction J on the error df. DA: √(MS of the term the test uses: interaction when significant, residual otherwise). RATA Dunnett: √(blocked error MS). RATA FDR/LSD: the SD of the paired differences (d_z). Liking: the LMM residual SD. CATA keeps Cohen's h under its own name. The z-score view shows the same number, so the standardised error bars scale exactly. Because RATA's error SD depends on the method (D-C9), its standardised values change with the method too; the column header names the SD used. | Owner, 2026-10-06 |
| D-C11 (MA-3, MA-6) | Accepted as recommended, pending objection. Dunnett uses the exact one-dimensional integral for complete designs and the multivariate-t cdf (fixed seed, p tolerance ≈ 1e-4) otherwise; it reduces to t with one comparison. The FDR interval is described as "adjusted for the false discovery rate; it excludes zero exactly when the difference is significant". | Recommendation, 2026-10-06 |

| D-C12 | **Untested rows** (no SE could be formed, or pairwise inference suppressed) carry no star and no interval. They are drawn as a hollow outline bar in the product colour, and the reason appears in the hover and the table. §1's rule applies to tested rows. | Owner, 2026-10-06 (accepting the Phase A proposal) |
| D-C13 | **Liking effect size under suppression:** the standardised difference on the LMM residual SD **without** Hedges' J (the df behind J is the one that cannot be trusted); `effect_size_name` says so. | Owner, 2026-10-06 |
| D-C14 | The Phase A adjustments to Phases B and C are accepted: the chart and table wiring move into Phase B, CON-20 is in Phase B, the blanking moves into `compute_contrast`, and the FDR captions are rewritten in Phase B. | Owner, 2026-10-06 |

| D-C15 | **Attribute order:** sorted by difference by default, with a remembered toggle for alphabetical. Three bands (higher / no evidence / lower). An attribute is banded when at least one shown product differs significantly, the sign coming from the mean standardised difference across the shown products. Within a band, attributes are ranked by that mean. | Owner, 2026-10-06 (Phase C Q1a) |
| D-C16 | **Many products:** grouped bars stay for now. Small multiples are deferred to a later visual pass. | Owner, 2026-10-06 (Q2) |
| D-C17 | **Hover** is one sentence from a fixed template, in "points" (DA, RATA, Liking), "percentage points" (CATA) or "SD units" (standardised view, naming the SD). | Owner, 2026-10-06 (Q3) |
| D-C18 | **Spider:** points are filled when significant and hollow when not; a thin × in the product colour marks a not-tested row; no ribbon. Attribute labels keep only the omnibus ★. | Owner, 2026-10-06 (Q4a, Q5a) |
| D-C19 | **Export:** the Contrast sheet gets plain-language headers (list in Phase C); Significant reads Yes / No / Not tested; the sheet holds the reference viewed last and the products selected, with a title row giving reference, products, method and family size; Methods_Notes and the export step carry the "how to report" sentence. | Owner, 2026-10-06 (Q6a–Q9) |
| D-C20 | **Validation:** freeze RATA-with-empty-cells and incomplete-Liking sets; add a per-method AppTest for every module; DA empty cells stay documented, not frozen. | Owner, 2026-10-06 (Q10a) |

| D-C21 | **Summary cards:** a row of bordered cards above the tabs, one per selected comparison product, counting attributes where it is higher / lower / no evidence (and not tested). The counts follow the attribute filter. Liking (one attribute) shows the difference and the verdict instead. | Owner, 2026-10-06 (Phase D) |
| D-C22 | **Display options** (attribute filter and picker, order switch, standardise toggle) go in a "Display options" popover; the reference and comparison selectors stay on the page. | Owner, 2026-10-06 |
| D-C23 | **Attribute filter:** a three-way switch, All / ★ product effect / Differs from the reference (at least one shown product differs significantly), with the manual picker kept. | Owner, 2026-10-06 |
| D-C24 | **Many products:** small multiples stay deferred (D-C16 stands). | Owner, 2026-10-06 |

D-C3 supersedes the "contrast and letters are one decision" rule (STAT-02/03/09, CLAUDE.md "Key design principles") **for the contrast step only**. The Step 3 letters keep the all-pairs family. CLAUDE.md, `Statistical_Methods_README.md` §23 and `tests/test_cld_contrast_agreement.py` change accordingly (Phase B).

---

## 3. How it works today

| | DA | RATA | Liking | CATA |
|---|---|---|---|---|
| Function | `stats.contrast.compute_contrast` | same | same | `stats.cata.run_cata_contrast` |
| Estimate | product means (LS means on attributes with empty cells) | FDR / LSD: mean of paired assessor differences. Tukey: block-model means | LMM LS means | paired citation proportions |
| Error term | conditional ANOVA MS (`resolve_da_error_term`) | FDR / LSD: per-pair paired SE, df n − 1. Tukey: pooled blocked MS (`rcbd_error_term`) | LS-means covariance, `df_pairwise` | Agresti paired-proportion variance |
| Test | t | t | t | McNemar: exact when b + c < 25, asymptotic χ² otherwise |
| Family | all C(k,2) pairs in the attribute | same | same | all attributes, within each comparison product |
| Interval | t (LSD, FDR) or studentized range (Tukey), **never FDR-adjusted** | same | same | Wald, **never adjusted** |
| Stars from | `p_value_fdr` if present, otherwise **raw** `p_value` | same | same | `p_value_fdr` (the adjusted p, whatever the method) |
| Renderer | `render_contrast_step` in `modules/descriptive/workflow.py` | `modules/rata/ui.py` | `modules/liking/ui.py` | `render_step_5` in `modules/cata/ui.py` |

The four renderers are near-copies (CODE-07). All of them draw with `utils.plotting.plot_butterfly_chart` and `plot_spider_with_ribbon`.

---

## 4. Findings

Severity: **HIGH** means the page shows a contradictory or wrong statistical statement. **MEDIUM** means misleading but internally consistent. **LOW** means presentation or code quality.

### 4a. Statistics

| ID | Sev. | Finding | Evidence | Where |
|---|---|---|---|---|
| CON-01 | HIGH | **Under Tukey, the stars and the table's p-value use the raw t-test p, while the bar's colour uses the HSD decision.** Faded "not significant" bars carry a star. The table shows `p < 0.05` next to "Significant: No". | Rows: RATA sensochoc 40/420, DA sensochoc 44/420, DA with empty cells 42/420, Liking hedochoc 4/30, synthetic 10×6 up to 8/30. That is about 10 % of profiling rows. | `plot_butterfly_chart` (`_sig_stars(row.get('p_value_fdr', row.get('p_value')))`); the tables' `p_col` choice in every module; `contrast.py` keeps only the raw p for Tukey |
| CON-02 | HIGH | **Under FDR, the interval is the unadjusted t interval, but the decision uses the BH-adjusted p.** Bars are faded although their interval clears zero. This only happens in that direction. | RATA 6/420, DA 16/420, DA with empty cells 14/420, RATA with empty cells 12/420, Liking hedochoc 6/30, synthetic 2–6/30 | `contrast.py` Step 5 (CI) vs Step 9 (FDR overwrite) |
| CON-03 | HIGH | **CATA's interval is an unadjusted Wald interval, while its decision is a corrected McNemar test.** They disagree even with no correction, because Wald and exact McNemar are different procedures. | bread: FDR 50, Bonferroni 168, Holm 148, uncorrected 6 (of 930). squashes: FDR 444, Bonferroni 930, Holm 884, uncorrected 118 (of 3,740). The docstring calls the interval "plot-decoration only". | `run_cata_contrast` |
| CON-04 | HIGH | **`_sig_stars(NaN)` returns `*`**: `NaN >= alpha` is False. A CATA pair with no discordant consumers (nobody ticked the attribute for either product) gets a star on a faded bar. | squashes, "Angry" vs PP7 / PP11: 2 rows | `utils/plotting.py::_sig_stars` |
| CON-05 | HIGH | **The Liking contrast ignores `lmm_pairwise_suppressed`.** Above 5 % missing cells, Step 2 suppresses pairwise inference (letters hidden). *Corrected in Phase A:* Step 4 did **not** draw significance from the unreliable df. The LMM blanks `cov_lsmeans` to NaN; `max(0.0, NaN)` is `0.0` in Python, so `se_diff` became NaN and `compute_contrast` fell back to **p = 1**. Every comparison then showed p = 1.0000, "Significant: No", faded bars and no interval, and the export carried the same. A test that never ran was reported as a confident negative result, beside a Hedges' g of up to 2.4. **Fixed in Phase A** (UI side; the stats-layer cause is CON-20). | Probe: hedochoc-like synthetic 20 × 5, 10 % cells dropped, all three methods give p = 1 on every row. AppTest: hedochoc with 80 of 222 consumers missing one product (6.0 %). | `modules/liking/ui.py`; `stats/contrast.py` Liking branch |
| CON-06 | MEDIUM | **On RATA attributes with empty cells, the plotted difference is not "comparison mean − reference mean" as the table shows it.** FDR/LSD estimate the mean of paired differences over the assessors who rated both products. The summary shows LS means. The methods reference (§ "unbalanced designs") claims the contrast uses the same means as everything else. | sensochoc with 6 empty cells, FDR and LSD: 388/420 rows differ, by up to 0.147 scale points. Tukey: 0 (block-model means). | `contrast.py` RATA paired branch; `Statistical_Methods_README.md` line ≈811 |
| CON-07 | MEDIUM | **The z-score view divides by the SD of the product means.** That changes when products are added or removed, and it isn't a recognised effect size. | Code reading | `contrast.py` Step 3, `run_cata_contrast` |
| CON-08 | MEDIUM | **The effect size means something different in each module.** DA's Hedges' g uses the pooled SD of assessor means (not the error term the test uses). RATA uses d_z of paired differences. Liking uses the LMM residual SD. CATA puts Cohen's h in the same column. The table calls all three "Hedges' g" with the same benchmarks. | Code reading | `contrast.py` Step 7 |
| CON-09 | MEDIUM | **The Holm fallback blanks the interval, and the spider ribbon then gets zero width** (`lsd_values[attr] = 0.0` when every half-width is NaN). That reads as "every product differs". | Code reading: every module's `lsd_values` loop | renderers |
| CON-10 | LOW | DA's Tukey k counts all products, not those present in the attribute (STAT-14, already open). Superseded by D-C3: Dunnett's family size must be the attribute's own k − 1. | `docs/open-items.md` STAT-14 | `contrast.py` |
| CON-20 | MEDIUM | *Found in Phase A.* **When no SE can be formed, `compute_contrast` reports p = 1 instead of "not tested".** Nine branches set `p_value = 1.0`: Liking with a NaN covariance (the cause of CON-05), the DA and RATA-blocked `se_diff == 0`, RATA paired with `n < 2` or zero SD of differences, and four in `_all_pairs_raw_pvals`. Then p = 1 enters the BH family as a real p-value, and the row reads "not significant". In RATA's paired branch, a **constant non-zero** difference (every assessor scores the comparison exactly 1 point higher) has an SD of 0, so it reads p = 1 and LSD = 0. That is the wrong direction: the evidence is as strong as it gets, yet the t-test is undefined. | Code reading: `stats/contrast.py` lines ≈336, 481, 516, 551, 558, 785, 832, 853, 855 | `stats/contrast.py` |
| CON-21 | LOW | *Found in Phase A.* **The butterfly docstring said it draws CLD letters (`cld_comp`). It does not, and never did in the current code.** Fixed in Phase A. | Code reading | `utils/plotting.py` |

### 4b. Visualisation and copy

| ID | Sev. | Finding | Where |
|---|---|---|---|
| CON-11 | HIGH | **Legend swatches take the first attribute's opacity.** A product that wasn't significant on the top attribute appears pale in the legend (owner's RATA screenshot, 2026-10-06: GST-R, HSK-G, PR-CHD and PT-R solid, the rest pale). | `plot_butterfly_chart`: per-bar RGBA in `marker.color` |
| CON-12 | HIGH | **Liking's chart caption still says FDR applies "across the selected comparison(s) only".** It's a third copy of the stale wording fixed in DA and RATA on 2026-10-05. My earlier search missed it because the string is built dynamically. It now contradicts the caption above it. | `modules/liking/ui.py` butterfly caption |
| CON-13 | MEDIUM | **The DA and RATA chart captions describe CLD letters that the chart doesn't draw.** The caption added on 2026-10-05 ("match the CLD letters") becomes false under D-C3. | DA and RATA `render_contrast_step` |
| CON-14 | MEDIUM | **The spider chart's axis stars use the smallest p over all comparison products**, from the same wrong column as CON-01, and say nothing about which product differs. The caption calls them ★, which this project reserves for the omnibus test. | `plot_spider_with_ribbon::_axis_label`; spider captions |
| CON-15 | MEDIUM | **The summary tables break the project's table conventions.** They `.round(3)` and turn the CI and percentages into strings, which stops numeric sorting. The p column is the wrong p under Tukey (CON-01). DA, RATA and Liking join the `cld_ref` / `cld_comp` columns into the frame and export them. | all four renderers |
| CON-16 | MEDIUM | **The export's Contrast sheet holds only the last viewed reference, CLD columns included, and the raw p under Tukey.** `utils/reporting.py` has no "how to report" sentence for the contrast. | `utils/export.py`; `utils/reporting.py` |
| CON-17 | LOW | Attributes are sorted alphabetically, so the answer isn't at the top. Grouped bars stop being readable beyond about 3 products (owner's screenshot has 11). Hover shows only the difference: no CI, p or decision. | `plot_butterfly_chart` |
| CON-18 | LOW | In Liking, "Show significant attributes only" does nothing, because there is one attribute. DA and RATA still have dead `scipy` version probes (CODE-08). | renderers |
| CON-19 | LOW | Four near-identical renderers (CODE-07). Every fix above would have to be made four times. | renderers |

---

## 5. Target specification (the contract)

### 5a. One result row

`compute_contrast` and `run_cata_contrast` return the same core columns for every row (attribute × comparison):

| Column | Meaning |
|---|---|
| `reference`, `comparison`, `attribute` | identity. `reference` moves into the stats layer, so the frame describes itself. |
| `estimate` | comparison − reference. DA, Liking and RATA Dunnett use the module's means; RATA FDR/LSD use the paired means over the assessors who rated both (D-C9), returned beside it with `n_paired`. `estimate_basis` names which. |
| `se`, `df` | the error term the test used. `df` is NaN for z-based CATA. |
| `p_raw` | unadjusted p-value |
| `p_adj` | **the decision p-value**: Dunnett-adjusted, BH-adjusted, Holm/Bonferroni-adjusted, or equal to `p_raw` for LSD |
| `significant` | `p_adj < alpha`. Exactly one boolean, replacing today's `out_of_spec` plus the 'Yes'/'No' column. |
| `ci_lower`, `ci_upper` | an interval that excludes 0 **exactly when** `significant` (§5c). NaN only on CATA's exact branch (D-C7), with the reason in `interval_note`. |
| `interval_type` | e.g. `"Dunnett simultaneous 95 %"`, `"FCR-adjusted (BY 2005), level 97.2 %"`, `"t 95 %"` |
| `std_estimate`, `std_ci_lower`, `std_ci_upper` | estimate and interval divided by the error SD (D-C5) |
| `effect_size`, `effect_size_name` | the standardised difference on the test's own error SD (D-C10); Cohen's h for CATA |
| `family_size` | m = k − 1 for this attribute |
| `method` | the many-to-one method actually used, e.g. `"Dunnett"` |

The `attrs['ui_warnings']` convention stays. The CLD columns are removed from the contrast frame (D-C1).

### 5b. Family and test per module

| Step 1 method | DA | RATA | Liking | CATA |
|---|---|---|---|---|
| Tukey (all three spellings, `is_tukey`) | Dunnett, conditional ANOVA error term | Dunnett, blocked error term (`rcbd_error_term`) | Dunnett, LS-means covariance, `df_pairwise` | — (CATA has no Tukey option) |
| FDR (BH) | BH over the k − 1 comparisons | BH over the k − 1 **paired t-tests** (D-C9) | BH over the k − 1 comparisons | BH over the k − 1 comparisons (D-C4) |
| Bonferroni / Holm | — | — | — | Bonferroni over the k − 1 comparisons; Holm applied as Bonferroni (D-C8) |
| LSD / uncorrected | unadjusted t | unadjusted **paired** t (D-C9) | unadjusted t | unadjusted McNemar |
| No pooled error term (today's Holm fallback) | Bonferroni over the k − 1 paired t-tests (D-C8) | same | — | — |

CATA's test within each method is the D-C7 hybrid: exact McNemar below 25 discordant consumers, asymptotic McNemar from 25 up.

**Dunnett computation.** The critical value and adjusted p-values come from the multivariate t distribution, with the correlation matrix of the k − 1 contrasts and the error df:

- **Complete designs (DA, RATA blocked):** the correlations have the product form ρ_ij = λ_i λ_j. Dunnett's one-dimensional integral is then exact and deterministic.
- **Empty-cell LS means and the Liking covariance:** the correlations are general, and the computation uses `scipy.stats.multivariate_t.cdf`. It's available in SciPy 1.18.1, but the project's floor is SciPy ≥ 1.13; check that `lower_limit` exists at the floor or raise it. This cdf uses quasi-Monte Carlo, so it needs a fixed seed and a stated tolerance, for reproducible exports and stable cache keys (MA-3).
- `scipy.stats.dunnett` **can't be used**: it takes raw independent samples, with no blocked design, custom SE or df.

### 5c. Interval that matches the decision

| Method | Interval | Why it matches |
|---|---|---|
| LSD / uncorrected (t) | estimate ± t(1 − α/2, df)·se | same t and se as the test |
| Dunnett | estimate ± c·se, with c the two-sided Dunnett critical value for the attribute | simultaneous interval inverting the same test |
| BH (FDR) | level 1 − max(R, 1)·α/m per attribute, where R is the number of rejections among the m comparisons (Benjamini & Yekutieli 2005) | BH is step-up: a raw p ≤ R·α/m is always among the R rejections, and a larger one never is. The audit script confirms 0 disagreements on all pairs in the bundled data (all-pairs family; the same argument holds for m = k − 1). |
| Bonferroni (and Holm, applied as Bonferroni per D-C8) | level 1 − α/m | the same threshold as the test |
| RATA paired t (FDR, LSD) | each pair's own t(df = n − 1) at the level above | each row's interval inverts its own paired test; the BH and Bonferroni level rules work row by row |
| CATA, asymptotic branch (≥ 25 discordant) | Tango score interval at the level above | inverts the asymptotic McNemar test (D-C7) |
| CATA, exact branch (< 25 discordant) | none; `interval_note` set | no matching interval on the difference scale (D-C7) |

`p_adj < alpha` vs ≤: BH formally rejects at ≤. Pick one convention (strict `<`, as now) and test the boundary.

### 5d. What every view reads

- **Bar colour, stars, table "Significant" column, export:** `significant` and `p_adj`. Stars use `_sig_stars(p_adj)`, which returns `''` for NaN.
- **Error bars:** `ci_lower` / `ci_upper`, or the `std_*` columns in the z-score view.
- **Spider:** filled or hollow points from `significant`, per product and attribute (D-C6). No ribbon.
- **Captions:** generated from `method`, `interval_type` and `family_size`, never hard-coded per module.

---

## 6. Statistical questions: decided 2026-10-06

All six questions are decided (D-C7 to D-C11 in §2). `method-auditor` still reviews the implementation against them in Phase B. The evidence behind each decision, measured on the bundled data:

- **MA-1, CATA test and interval → D-C7 (hybrid).** Over all product pairs, uncorrected: bread has 38 of 465 pairs on the exact branch, and replacing the exact test with the asymptotic one changes 1 decision. Squashes has 963 of 1,870 pairs on the exact branch, and the switch makes **50 pairs newly significant and none lose significance**, from discordant counts as small as 4 (b + c = 4, 5, 8, 11…). That is the asymptotic test's known liberality at small counts, so the exact test stays where it applies. Reference for Tango's interval: `PropCIs::scoreci.mp` in R (check that it implements Tango 1998 before pinning against it).
- **MA-2, Holm → D-C8 (applied as Bonferroni in the contrast step).** The profiling fallback needs RATA's blocked df < 1 or an unusable DA error MS. No bundled dataset reaches it naturally; the existing fallback tests construct it.
- **MA-3, Dunnett numerics → D-C11.** At the SciPy floor (≥ 1.13), check that `multivariate_t.cdf` with `lower_limit` exists, or raise the floor. The Dunnett critical value for k − 1 = 5 at df = 40 came out as 2.619 on SciPy 1.18.1, in line with published tables.
- **MA-4, effect size → D-C10 (the test's own error SD).**
- **MA-5, RATA estimand → D-C9 (keep paired tests).** The rejected blocked-model alternative would have changed 6 of 210 LSD decisions on sensochoc (all losing significance) and 7 of 210 with 6 empty cells (6 lose, 1 gains). The median SE rose by 2–3 %, and the df went from about 28 to 140.
- **MA-6, FDR interval wording → D-C11.**

The measurement script for MA-1 and MA-5 is not saved separately: both numbers follow from `run_mcnemar_posthoc` / `compute_contrast` calls like those in `working_notes/repro/contrast/contrast_audit.py`. Phase B's tests re-establish them.

---

## 7. Implementation plan

Conventions are as in `03-implementation-plan.md`: read `CLAUDE.md` first; invoke `developing-with-streamlit` before touching `modules/*/{ui,workflow}.py` or `utils/ui_shell.py`; every defect fix lands with a test that fails first; every `stats/` change bumps the version (next: `1.0.0rc2`) and records a CHANGELOG entry plus a sensochoc before/after.

### Phase A. Safety net and fixes that don't depend on the family

Small. Can merge before the method audit.

1. **Invariant test, marked `xfail(strict=True)`:** `tests/test_contrast_consistency.py`. For every module × method × bundled dataset (plus the empty-cell and synthetic sets used in the audit script), assert star ⇔ significant ⇔ interval excludes 0, and table p < α ⇔ significant. It starts xfail for the cases CON-01/02/03 cover. Phase B removes the mark.
2. **CON-04:** `_sig_stars` returns `''` for a NaN or missing p. Unit test.
3. **CON-11:** legend swatches at full product colour, for example one legend-only trace per product with the bars' `showlegend=False`. Test that the legend colour equals `color_mapping[product]`.
4. **CON-12, CON-13:** remove Liking's stale FDR sentence, and remove the CLD sentence from the DA/RATA chart captions. Leave the 2026-10-05 FDR caption until Phase B rewrites all captions.
5. **CON-05:** gate the Liking contrast on `lmm_pairwise_suppressed`. Differences are still shown; stars, colour and intervals are withheld, with the same explanation Step 2 gives. AppTest with a > 5 % missing synthetic panel.

Exit: suite green with the xfails in place; CHANGELOG entry. No version bump, as there is no `stats/` change.

#### Phase A report (2026-10-06)

**Done. Uncommitted on `main` at `08c3db3`.** Full suite green as CI runs it (`FREESENSE_REQUIRE_DATA=1`, `-n auto`): **925 passed, 22 xfailed, 0 failed, 0 skipped**. Not run: the coverage floors (`--cov` + `scripts/check_coverage.py`) and `ruff check .`, because ruff is not installed in `env/` or on PATH. Install the dev lock (`requirements/dev-lock-py3.14.txt`) and run it before committing. CHANGELOG: "Reference contrast, Phase A" under *Unreleased → Fixed*. No version bump.

| Item | Result | Where | Test (fails on the old code: checked) |
|---|---|---|---|
| 1. Invariant test | `tests/test_contrast_consistency.py`, 35 cases: DA and RATA × {sensochoc, 6 empty cells} × 3 methods; Liking × {hedochoc, jar, synthetic 10×6 seeds 0–2} × 3; CATA × {bread, squashes} × 4. Every product is the reference. The test reads the **drawn figure** (stars = bar text, colour = bar alpha, interval = whiskers), not the frame, so a chart-side regression also fails it. It also asserts table p < α ⇔ significant, and that a row with no interval carries `interval_note`. **13 pass, 22 are `xfail(strict=True)`**: CON-01 for every Tukey case, CON-02 for every FDR case, CON-03 for every CATA case, except Liking `jar` and `synthetic seed 1`, where neither defect happens to fire. With `--runxfail`, the violation counts equal the audit script's (RATA sensochoc Tukey 80 = 40 star + 40 table; DA FDR 16; Liking hedochoc Tukey 8; CATA bread uncorrected 6; squashes uncorrected 118, down from 120 because CON-04 removed 2). | new file | the 22 xfails |
| 2. CON-04 | `_sig_stars` returns `''` for NaN, None, `pd.NA` and ±inf. **Side effect:** the DA `Results_Table` star column (`utils/export.py` ≈866) now reads `ns` for an attribute whose product p is NaN, where it used to read `*`. That's correct, but "ns" is arguably wrong too: the attribute was never tested, so `—` would be better. Left for Phase C (export). | `utils/plotting.py` | `tests/test_butterfly_chart.py::test_missing_p_value_earns_no_star` |
| 3. CON-11 | One legend-only `Scatter` (square marker, full product colour, `legendgroup`) per product; bars have `showlegend=False` and the same `legendgroup`, so a legend click still toggles them. A data-less Scatter takes no slot in `barmode='group'`, so the bar layout is unchanged. | `utils/plotting.py` | `test_legend_swatches_carry_the_full_product_colour` |
| 4. CON-12, CON-13 | Liking's "across the selected comparison(s) only" sentence removed. DA and RATA lose the "Letter groups (a, b, ab) …" sentence. As planned, the 2026-10-05 "…match the CLD letters" FDR caption stays in DA and RATA, and so does Liking's own copy ("FDR is applied across all product pairs … match the CLD letters"); see the Phase B adjustment. Also fixed the butterfly docstring (CON-21). | DA `workflow.py`, RATA `ui.py`, Liking `ui.py` | none (copy). `test_step_references` and `test_markdown_injection` stay green |
| 5. CON-05 | The mechanism differs from the audit's description (see CON-05 above). Step 4 now reads `lmm['lmm_pairwise_suppressed']`. When it is set, the step shows Step 2's explanation (now one shared constant, `modules.liking.ui.PAIRWISE_SUPPRESSED_MESSAGE`) plus one sentence. It blanks `se_diff`, `ci_*`, `lsd_or_hsd` and `p_value*` to NaN, and `significant` and `out_of_spec` to None, on a copy *before* storing `liking_contrast_df`, so the table and the export show "not tested" too. The chart gets a new `inference_withheld=` argument: full-colour bars, no stars, no whiskers, and a footnote reading "Differences only: significance not tested (…)". Hedges' g is still shown, as a descriptive standardised difference; see the Phase B adjustment. | Liking `ui.py`, `workflow.py`; `utils/plotting.py` | `test_apptest_liking.py::test_contrast_withholds_inference_when_pairwise_is_suppressed[Tukey, FDR]`; `test_withheld_inference_draws_differences_only` |

**Decisions made in Phase A that the owner should confirm:**

- **Untested rows are drawn in full colour.** The visual rule in §1 has only two states, and both are wrong for a row with no test: faded means "no evidence of a difference", and full colour means "significant". I chose full colour, with no star and no whisker, plus a footnote and a warning. Untested rows were not in §1 at all. They now exist in Liking (suppression), and Phase B adds CATA's b = c = 0 rows and CON-20's degenerate SEs. **Proposal for §1:** the rule applies to *tested* rows; an untested row has no star and no interval, is drawn as a hollow outline bar in the product colour, and gives its reason in the hover and the table. That would replace Phase A's full-colour bars in Phase C.
- **The inferential columns are blanked in the module, not the stats layer.** That keeps Phase A free of `stats/` changes, as the plan required. It is a layer-rule compromise, and Phase B removes it (see below).

### Phase B adjustments (after Phase A)

*Adjusted after Phase A.* Additions to the list below:

- **B-exit is unreachable as planned.** The invariant test reads the drawn chart and the renderers' table p column, which today read `out_of_spec` and `p_value_fdr`/`p_value`. Phase B's new `p_adj` and `significant` columns turn the test green only if, in the same phase, (a) `plot_butterfly_chart` takes stars from `p_adj`, opacity from `significant` and whiskers from `ci_*`, and (b) the four tables show `p_adj`. **Move those wiring changes from Phase C item 1 and item 4 into Phase B.** Phase C keeps sorting, small multiples, hover, the spider and the table restyle. Update `_violations` in `tests/test_contrast_consistency.py` to read the §5a columns at the same time.
- **CON-20: replace the p = 1 sentinel.** Where no SE can be formed, return `p_raw = p_adj = NaN`, `significant = <NA>` (a nullable boolean, so §5a's `significant` has three states: True, False, not tested), NaN interval and a reason in `interval_note`. Exclude these rows from the BH and Bonferroni family (m counts tested comparisons only), and state that in the caption. For RATA paired rows whose differences are constant and non-zero, the note should say the t-test is undefined because all assessors agree exactly. Add a known-answer test for each branch.
- **Move CON-05's blanking into `compute_contrast`.** Pass `pairwise_suppressed` (or detect an all-NaN `lmm_cov_params`) and emit the CON-20 "not tested" rows, with the reason in `attrs['ui_warnings']`. Then delete `_CONTRAST_INFERENCE_COLS` and the blanking block from `modules/liking/ui.py`; the AppTest stays as written.
- **Effect size under suppression.** D-C10 gives Liking the LMM residual SD with J on the error df, but under suppression that df is exactly what can't be trusted. Recommendation: under suppression, report g without J (or not at all), and name it in `effect_size_name`. Owner's call.
- **Captions change with the family, not after it.** The three "…match the CLD letters" FDR captions (DA, RATA, Liking) become false the moment D-C3 lands. Rewrite them in Phase B, in the same commit as the family change, using the D-C3 sentence from Phase C item 3. Otherwise the page states something false between B and C.
- **CATA b = c = 0** (Phase B item 5): the star half is already fixed by CON-04. What's left is the stats-layer p and note, under the CON-20 rule above.
- **Xfail removal is per case.** Each of the 22 marks names its finding (CON-01, CON-02, CON-03). Strict xfails make a partially fixed engine fail the run, so remove each mark as its finding is fixed.

### Phase B. Many-to-one statistics engine

The core. Goes through `method-auditor` before and after.

1. `method-auditor` reviews §5 and D-C7 to D-C11 before coding starts and records any objection here.
2. **`stats/contrast.py`:** restructure around §5:
   - one per-attribute function that builds the k − 1 comparisons (estimate, se, df, covariance of the estimates);
   - one function that applies the method: Dunnett / BH / Bonferroni / Holm / none → `p_adj`, `significant`, the matching interval and `interval_type`.
   Remove `_all_pairs_raw_pvals` (the all-pairs family is gone from the contrast). Dunnett lives in `stats/posthoc.py` or a new `stats/shared/dunnett.py`, never in `modules/`.
3. **RATA** per D-C9: keep the paired branch for FDR/LSD, with BH or no adjustment over the k − 1 comparisons, and return the paired means (`ref_mean_paired`, `comp_mean_paired`) and `n_paired` so the table subtracts. Dunnett goes on the blocked branch. Add a `estimate_basis` column (`"paired assessors"` / `"blocked model"`) that the caption reads.
4. **`std_*` and effect size** per D-C5 / D-C10. Remove the three Hedges' g formulas; `effect_size_name` names the SD used.
5. **`stats/cata.py::run_cata_contrast`:** family per D-C4; hybrid test and Tango interval per D-C7; Holm as Bonferroni per D-C8. Rows with b = c = 0 get `p_raw = 1` or NaN plus an `interval_note`, never a star.
6. **Tests:**
   - remove the xfail from the Phase A invariant test;
   - `tests/test_cld_contrast_agreement.py`: keep the CLD checks; keep contrast agreement only for LSD, where the two views still coincide row by row; delete the rest, with the reason in the module docstring;
   - known-answer tests (`tests/test_known_answers_contrast.py`): Dunnett adjusted p and intervals against `multcomp` / `emmeans` on sensochoc (DA conditional term, RATA blocked) and hedochoc (Liking); the BH interval level against a hand computation (base R `p.adjust` + `qt`); CATA intervals against the MA-1 reference;
   - `validation/`: add a `Contrast/` emitter and R script, freeze the reference CSVs, extend `tests/test_validation_pins.py`;
   - a family test: deselecting comparison products changes no `p_adj` (D-C2).
7. Version `1.0.0rc2`; CHANGELOG entry listing CON-01…CON-10 and the RATA number change; close STAT-14 in `docs/open-items.md`.

Exit: invariant test green on every module, method and dataset; known answers within tolerance; `method-auditor` sign-off.

#### Phase B report (2026-10-06)

**Done. Uncommitted on `main`, on top of Phase A.** Version `1.0.0rc2`. Every CI gate passes locally:
- `ruff check .`: run with the dev lock's `ruff==0.16.9` from a scratch venv, because `env/` has no ruff.
- the suite as CI runs it: **961 passed, 0 failed, 0 xfailed** (after the audit fixes);
- coverage: 88.2 % overall, lowest `stats/` file 84.1 %; `stats/shared/dunnett.py` 85.7 %, `stats/contrast.py` 96.7 %. Run with the dev lock's `pytest-cov`, which `env/` also lacks.

`validation/Contrast/contrast_reference.R` passes all 44 checks.

| Plan item | Result |
|---|---|
| B.1 audit before coding | `method-auditor`: **pass with conditions C1–C7**. All seven are implemented and tested: C1 strict R over the full family; C2 Dunnett tail computed directly, Šidák-clamped, decision \|t\| > c, QMC reconciled; C3 zero blocked MS → paired fallback; C4 SD 0 → no standardised value; C5 no J below 2 df; C6 `mvtnorm` at high precision, not `dunnettx`/default `mvt`; C7 Dunnett on the tested sub-vector. |
| B.2 `stats/contrast.py` | Rewritten around §5a. Three family builders (pooled error term, paired t, Liking LMM), one `_finish_t_family` (Dunnett / BH / Bonferroni / none plus the matching interval), `adjust_family` (shared with CATA). `_all_pairs_raw_pvals` is gone. Dunnett lives in `stats/shared/dunnett.py`. |
| B.3 RATA (D-C9) | FDR/LSD use paired t-tests, with `ref_mean`/`comp_mean` over the paired assessors and `n_paired`; Dunnett uses the blocked model; `estimate_basis` names which. |
| B.4 `std_*` and effect size (D-C5, D-C10, D-C13) | One number on the test's own error SD, with J on the error df; `std_name`/`effect_size_name` name it. The z-score toggle is now "Standardise by panel noise (error SD)". |
| B.5 CATA (D-C4, D-C7, D-C8) | Family per attribute across the k − 1; exact below 25 discordant (no interval, note); asymptotic plus Tango from 25; Holm → Bonferroni; b = c = 0 → exact p = 1. `freq_table` is dropped from the signature. |
| B.6 tests | Invariant test: 35/35, no xfails. `test_cld_contrast_agreement.py`: LSD-only row agreement plus the error-term checks, reason in the docstring. `test_known_answers_contrast.py`: 26 tests (Dunnett vs table and `scipy.stats.dunnett`, exact vs QMC, Šidák bounds, boundary decisions, SciPy keyword pin, BH level including the C1 boundary, D-C2 family test on all four modules, CON-20 branches, C3, C5, D-C13, Tango inversion over a grid, Tango MLE vs brute force, Tango vs PropCIs). `validation/Contrast/` plus `test_contrast_pins`. |
| B.7 version, CHANGELOG, STAT-14 | `1.0.0rc2` everywhere `test_version_identity` checks. CHANGELOG has a "Reference contrast, Phase B" entry with the before/after table. STAT-14 removed from `docs/open-items.md`; CODE-07, CODE-08 and IO-08 rows updated. |
| Phase A adjustments (D-C14) | All done: chart and tables read `p_adj`/`significant`/the interval; CON-20; the Liking blanking moved into `compute_contrast` (`pairwise_suppressed=`, reason in `attrs['ui_warnings']`); the FDR "…match the CLD letters" captions are replaced by the generated D-C3 sentence. |

**Agreement with the R references** (max abs difference, every product as reference):

| | Closed-form paths | Dunnett p / interval | Other adjusted p / intervals | Decisions |
|---|---|---|---|---|
| DA, residual MS | ≈ 1e-14 | 2.6e-6 / 4.4e-6 | ≈ 1e-14 | 0 of 1,260 rows differ (all branches) |
| DA, interaction MS vs `lmer` | SE 3.4e-6 (REML optimum) | 9.7e-6 / 9.3e-6 | 8.9e-6 | |
| RATA | ≈ 1e-14 | 3.3e-6 / 5.9e-7 | ≈ 1e-15 | 0 of 1,260 |
| Liking | SE 3.9e-8 | 1.7e-6 / 2.7e-8 | 2.7e-7 | 0 of 90 |
| CATA | ≈ 1e-15 | — | ≈ 1e-14; Tango 9.8e-8 | 0 of 2,790; interval present exactly on the asymptotic branch |

**Decisions before → after** are in the CHANGELOG. Dunnett gains rows over all-pairs Tukey (+16 RATA, +12 DA of 420); CATA Bonferroni/Holm gain where the family shrinks; BH moves both ways (RATA −9/+1, squashes −102/+101). No estimate changes on a complete design.

**Pulled forward from later phases** (the rewiring needed them, and the alternative was a page that says false things in between):
- **Phase C:** the chart reads the contract, with per-row states (full / faded / hollow for not tested, D-C12) and a hover with interval and decision; the four summary tables are numeric (two CI columns, raw and adjusted p, `n (paired)`, note); the CLD columns are gone (D-C1); the export sheets carry the contract columns, and Liking/CATA colour `p_adj`.
- **Phase D:** shared `utils/contrast_view.py` (captions generated from `method`/`family_size`/`interval_type`/`interval_note`, the table, the spider inputs); the scipy probes and the unused CLD reads are removed.
- **Phase E:** `Statistical_Methods_README.md` §23 rewritten, plus §25 (Liking), §52 (CATA) and the ≈811 sentence; the TOC is regenerated. CLAUDE.md now states the "one error term, not one family" rule and the new CATA scope. `test_doc_identifiers` forced these, since the old text named removed identifiers.

**Found while doing it:**
- **A regression I introduced and fixed:** the CLD-read cleanup removed CATA Step 4's `cld_df` line, because `str.replace` replaced both copies. The CATA AppTests and the Markdown-injection walk caught the `NameError`. This is why the lint gate matters: F821 flags exactly this.
- **Speed:** the QMC path (an attribute with an empty cell, under Tukey) costs about 0.25 s per attribute, so about 3.5 s per reference on sensochoc with 6 empty cells. The result is cached per reference. Complete designs use the exact integral, at about 0.07 s per attribute.
- **R run time:** `contrast_reference.R` takes about 30 min, dominated by Kenward–Roger on the Liking LMM and the high-precision `pmvt` calls. It isn't in CI; the pins are.
- **Contract vs §5a:** the frame also carries `ref_mean`, `comp_mean`, `statistic`, `interval_level`, `std_name` and `error_term`, which §5a doesn't list. They are needed for the table subtraction (D-C9), the caption generation and the validation split by branch.

**After-coding audit** (`method-auditor`, 2026-10-06): **sign-off with conditions**. It reproduced the pinned R reference and checked the new paths independently against R: the Dunnett primitive against `mvtnorm` on its own cases (p within 7e-6 exact, 1.9e-5 QMC), and the empty-cell RATA blocked Dunnett against `emmeans` (estimates 1e-14, p 1e-5). Its findings and what was done:

| # | Sev. | Finding | Disposition |
|---|---|---|---|
| 1 | MAJOR | Exact-zero guards miss rounding noise: SD ≈ 3e-16 (replicate-averaged identical differences) gave p ≈ 1e-79; a blocked MS of ≈ 1e-29 gave p_adj ≈ 1e-308 | **Fixed.** Scale-relative zero (`posthoc.negligible_error_ms`, `RELATIVE_ZERO = 1e-12`) in `rcbd_error_term`, `resolve_da_error_term` and the paired branch. Two regression tests and a scale-freeness test. The letters fall back the same way. |
| 2 | MAJOR | The CATA export still described the old family and a `cohens_h` column | **Fixed** (Methods_Notes and the Contrast_Analysis sheet header). |
| 3 | MINOR | "One rule on every row" overstated (CATA exact rows have no interval) | **Fixed** in §23 and CLAUDE.md. |
| 4 | MINOR | QMC accuracy stated three ways | **Fixed**: "p ± 5e-5" (measured ≤ 1.9e-5) in the code label, the docstring and §23d. D-C11's "≈ 1e-4" stays as the owner's decision text. |
| 5 | MINOR | `validation/README.md` gap list stale | **Fixed.** |
| 6 | MINOR | DA empty-cell contrast unvalidated; divergence from `lmer` (estimates up to 0.046) and additive `lm` (SE 4–7 %) inherited from the letters | **Documented** as a deliberate divergence in `validation/README.md`. **Open:** freeze an empty-cell RATA set (pins the QMC path) and an incomplete Liking set. See Phase C.7. |
| 7 | MINOR | Liking: a failed fit reported as "> 5 % missing" | **Fixed**: separate note and warning, with a test. |
| 8 | MINOR | NaN df silently became z; `log1p(-1)` warning | **Fixed**: raises on a NaN df or a non-finite correlation; warning silenced; test. |
| 9 | MINOR | Spider ribbon (widest half-width) can disagree with the markers | **Open**, Phase C.2 (D-C6 removes the ribbon). Don't ship rc2 to testers without Phase C.2, or hide the ribbon first. |
| 10 | MINOR | Step 1 method notes stale | **Fixed** in DA, RATA, Liking (Tukey description) and CATA (correction help). This was Phase E's Step 1 item. |
| 11 | MINOR | 25-discordant threshold duplicated | **Fixed**: `stats.cata.EXACT_THRESHOLD` is the McNemar helper's constant. |
| tests | — | z-score view in the invariant test; CATA with incomplete exposure; high-λ QMC against a frozen value | The z-score view is **added** (all 35 cases, both views). The other two are **open** (Phase C.7). |


### Phase C. Visualisation on the new contract

*Adjusted after Phase B:* most of the original list was done in Phase B because the contract change forced it (see the Phase B report): stars, colour and error bars from the contract; hollow not-tested bars (D-C12); a hover stating the interval and the decision; generated captions with the D-C3 sentence (CON-13); numeric tables with raw and adjusted p, paired means and `n (paired)` (CON-15); no CLD columns; export sheets carrying the contract columns. What is left:

1. **Butterfly chart** (CON-17):
   - rows sorted by estimate within three bands (higher / no evidence / lower), with alphabetical order as an option;
   - one small chart per comparison product (shared x axis and attribute order) when more than 3 products are selected;
   - the hover as one sentence from a fixed template, e.g. "B is 1.2 points higher than Control (95 % Dunnett CI 0.6 to 1.8), p = 0.0021: significant". Today it is two lines (interval; decision).
   The owner keeps bars with error bars as the form (2026-10-06).
2. **Spider** (D-C6, CON-09, CON-14): no ribbon; filled or hollow points per product from `significant`; axis labels without stars; a legend explaining filled = significant vs the reference. *Today it still draws the ribbon,* now the widest half-width of the matching intervals (`utils.contrast_view.spider_inputs`), and its axis stars use the smallest `p_adj`. It no longer contradicts the bars, but D-C6 is not done. RATA FDR/LSD needs the caption about attributes with empty cells (D-C9 (3)).
3. **Captions:** move the long legend text into a "How to read this" expander. The generated sentences themselves are done.
4. **Table:** label the remaining snake_case in exports (IO-08). Show the CATA test used and the discordant count beside the note; CATA does this, the others have no equivalent.
5. **Export** (CON-16):
   - `Run_Parameters` records the reference, method, family size and interval type (today only the reference and comparisons);
   - `utils/reporting.py` gains the contrast "how to report" sentence;
   - the export step's sheet bullets, which the AppTest parses, say what the Contrast sheet now holds;
   - the DA `Results_Table` star column writes `—` (not `ns`) for an attribute with no product p-value (added after Phase A);
   - `significant` is exported as TRUE/FALSE/blank; decide whether to write Yes / No / Not tested;
   - decide whether the sheet keeps only the last viewed reference (and says so) or records each reference viewed. Recommendation: last viewed, stated in the sheet title row.
6. AppTests: every module's contrast step under each method. The bundled-dataset walk and the Markdown-injection walk already pass on the new contract; the per-method walk is new.
7. *Added after the Phase B audit:* freeze an empty-cell RATA set (sensochoc with 6 empty cells) and an incomplete Liking set in `validation/Contrast/`; a CATA test with incomplete exposure (an n = 0 row left out of m, BH over rows with different n); a high-λ QMC Dunnett case against a frozen `mvtnorm` value.

#### Phase C report (2026-10-06)

**Done, under the owner's decisions D-C15 to D-C20. Uncommitted.** Lint passes; the full suite as CI runs it: **973 passed, 0 failed**, coverage is 88.3 % overall (lowest `stats/` file 84.3 %), and `validation/Contrast/contrast_reference.R` passes end to end (62 checks).

| Item | Result |
|---|---|
| C.1 chart (D-C15, D-C17) | `utils.plotting.contrast_attribute_order`: three bands (higher / no evidence / lower), an attribute banded when any shown product differs, the sign from the mean standardised difference, ranked within the band; an "Order attributes" switch (`<prefix>_contrast_order`, persisted). `contrast_hover_sentence`: the approved template, in points, percentage points (CATA) or SD units naming the SD, with the exact-McNemar and not-tested variants. Small multiples are deferred (D-C16). |
| C.2 profile chart (D-C6, D-C18) | `plot_contrast_spider` replaces `plot_spider_with_ribbon`: filled / hollow / thin × per point from `significant`, the same hover sentence, a neutral legend key, omnibus ★ only, no ribbon (closes audit Finding 9 and CON-09, CON-14). The caption adds the D-C9 (3) note on RATA FDR/LSD paired means. |
| C.3 captions | `render_contrast_notes`: the D-C3 sentence on the page, everything else in a "How to read this" expander. |
| C.4/C.5 export (D-C19) | `_write_contrast_sheet` for all four modules: plain headers (`CONTRAST_SHEET_LABELS`), Significant as Yes / No / Not tested, a title row (reference viewed last, products, method, comparisons per attribute, intervals). `Run_Parameters` gains `contrast_method`, `contrast_comparisons_per_attribute` and `contrast_interval_type` (CATA included). `utils.reporting.contrast_sentence` adds the approved "how to report" sentence to Methods_Notes and the export step, generated from the frame, with Dunnett, Benjamini & Yekutieli and Tango references. The DA `Results_Table` already wrote `—` for a missing p (no change needed). |
| C.6 AppTests | `test_contrast_step_under_every_method` in each module's AppTest file: 13 cases (3 + 3 + 3 + 4). Each checks the method label, p_adj ⇔ decision, the caption and expander, opens every gated panel and switches the order both ways (`tests/conftest.py::assert_contrast_step`). |
| C.7 validation and tests (D-C20) | `validation/Contrast/` gains RATA with 6 empty cells (all 420 Dunnett rows on the QMC path: p within 1.2e-5, intervals within 2.7e-5 of `mvtnorm`) and Liking with 12 missing cells (containment df; two REML optimisers, so SE within 6.6e-6 and adjusted p within 5.3e-5). All decisions agree. New tests: a high-λ QMC Dunnett case against a frozen `mvtnorm` value; CATA with incomplete exposure (an n = 0 comparison left out of m, BH over rows with different n). |

**Also changed:** the standardised-difference names became phrases ("Hedges' g on √ interaction MS", …), because the hover, the axis title and the export column showed nested brackets. Two tests that read the contrast sheet with its header on row 1 now read the title-row layout.

**Not done, by decision:** small multiples (D-C16).

**Watch:** the "How to read this" expander has an icon, which AppTest exposes as a `status` block, not an `expander`. The helper searches labels across the whole tree.

### Phase D. One shared renderer, then streamlining

Only after A–C. *Adjusted after Phase C:* the shared pieces now cover captions, notes, order control, table, hover and the profile chart (`utils/contrast_view.py`, `utils/plotting.py`). Left:

1. Extract `render_reference_contrast(...)` into `utils/` and call it from the four modules with module-specific labels only. This closes CODE-07's contrast part. Remove Liking's no-op "Show significant attributes only" toggle (CON-18).
2. The streamlining discussed on 2026-10-05: a summary card per comparison product ("higher on 4, lower on 2, no evidence on 9"), display options in a popover, the reference and comparison selectors kept visible, the table as the place to confirm.
3. *Owner, 2026-10-06:* consider a filter for "attributes where a shown product differs from the reference" beside the omnibus filter.
4. Small multiples for many products, or another form, in a later visual pass (D-C16).
5. The chart becomes the main figure of the planned HTML report.
6. Speed of the QMC Dunnett path (about 3.5 s per reference with empty cells): a product-form starting point for the root, or caching the critical value per (correlation, df) across references.

#### Phase D report (2026-10-06)

**Done, under D-C21 to D-C24. Uncommitted.** Lint passes; the full suite as CI runs it: **974 passed, 0 failed**; coverage 88.5 % (lowest `stats/` file 84.3 %).

| Item | Result |
|---|---|
| D.1 one renderer (CON-19, CON-18) | `utils.contrast_view.render_reference_contrast(ContrastStepSpec)`. Each module keeps its header, readiness checks and state, and passes texts, keys, the compute call, the profile builder and table extras. All four use it. Liking's no-op toggle is gone. CODE-07's contrast part is closed in `docs/open-items.md`. Widget and tab keys are unchanged, so persisted choices and the AppTests carry over; the `*_contrast_sig_only(_prev)` keys are retired. |
| D.2 streamlining (D-C21, D-C22) | Summary cards above the tabs (`summary_counts`, `render_summary_cards`): higher / lower / no evidence / not tested per comparison product, over the attributes shown; Liking shows the difference and the verdict. The "Display options" popover sits in the selector row and holds the filter, picker, order switch and standardise toggle. The table stays the place to confirm. |
| D.3 filter (D-C23) | `Show attributes`: All / ★ product effect / Differs from reference, persisted per module. The filter, the reference and the comparison set each reset the picker in their callback, so "differs" always follows the comparison on screen. An empty match falls back to all attributes, with a caption. |
| D.4 small multiples | Deferred (D-C24). |
| D.5 HTML report | Not started; out of this plan's scope. |
| D.6 QMC speed | **Measured, no change shipped.** Baseline on RATA with 6 empty cells under Tukey: 3.7 s per reference, 14 QMC evaluations per attribute (about 9 for the critical value, 5 for the p-values). Starting the root search from the equicorrelated design's exact critical value saved nothing (15 evaluations), because brentq's cost is set by its tolerance, not its start. It was reverted. The real lever would be a control-variate estimate (QMC of the general minus QMC of the nearest product-form correlation, on common points, plus the exact product-form value), which needs fewer points for the same error. Worth it only if users hit empty-cell designs with Tukey often; the result is cached per reference. |

Tests: the per-method AppTests now also check one card per product and the three filter positions (the "differs" picker must equal the differing attributes); `summary_counts` is pinned.

### Phase E. Documentation

#### Phase E report (2026-10-06)

**Done. Uncommitted.** The documentation tests pass (`test_doc_identifiers`, `test_methods_reference`, `test_documented_defaults`, `test_version_identity`, `test_stats_docstrings`). No code changed in this phase.

- `README.md`: a shared section, "The contrast step (Liking, CATA, Descriptive Analysis, RATA)", under *Module guides*; the four module entries link to it and keep only their module-specific facts (error term, McNemar/Tango, paired means, Liking's verdict cards). The false claim "same error term and correction as the letters, so the two always agree" is gone from all four. "How the methods were checked" names `mvtnorm` and PropCIs and the incomplete-data references.
- `Statistical_Methods_README.md`: §23h *What the Step Shows* (references renumbered to §23i; TOC regenerated); §23d QMC accuracy; §23g incomplete-data validation sets.
- `ABOUT.md` needed no change ("contrasts" is still accurate).

**The plan is complete.** Phases A–E are done. Deferred by decision: small multiples for many products (D-C24), the control-variate QMC speed-up (D.6), the HTML report.

---

## 8. Not in scope

These were noted and parked:

- **"Meaningful difference" band and an equivalence verdict (TOST).** This needs its own method audit; the band without a verdict could come with Phase D.
- **Fixing the reference in Step 1 as the pre-specified main comparison.** Today the reference can be switched freely. The Run_Parameters record (Phase C) makes the reference used traceable. Revisit if users report results from exploratory reference switching.
- **HTML report, product cards and takeaway titles** (brainstorm, 2026-10-05).

---

## 9. References

- Benjamini, Y. & Yekutieli, D. (2005). False discovery rate–adjusted multiple confidence intervals for selected parameters. *JASA* 100, 71–81.
- Dunnett, C. W. (1955). A multiple comparison procedure for comparing several treatments with a control. *JASA* 50, 1096–1121.
- Tango, T. (1998). Equivalence test and confidence interval for the difference in proportions for the paired-sample design. *Statistics in Medicine* 17, 891–908.
- Meyners, M., Castura, J. C. & Carr, B. T. (2013). Existing and new approaches for the analysis of CATA data. *Food Quality and Preference* 30, 309–319.
