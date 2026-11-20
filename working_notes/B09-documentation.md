# B09 Documentation and scientific transparency

Reviewer: B09 (read-only). Commit reviewed: `bcaf9f8` on `main`. Date: 2026-09-26.

## Scope and method

Checked:

- `README.md` (also rendered in-app as the About overlay, `app.py:60-70`), `example_data/README.md`, `validation/README.md` (links only), `CHANGELOG.md` (recent entries), `docs/open-items.md`.
- `Statistical_Methods_README.md` (2,869 lines, 257 KB, rendered in-app with one `st.markdown` call, `app.py:72-77`): structure, TOC anchors, and the documented model/defaults for each module against the code in `stats/` and `modules/`.
- In-app help: `help=`, `st.caption`, expander and status text in `modules/*` and `utils/ui_shell.py`, targeted by grep on method names, defaults and correction wording.
- Docstrings of every module-level function in `stats/` (AST scan).

Scripts (all in `/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B09/`):

- `anchors.py`: builds GitHub-style slugs and an approximation of Streamlit's heading slug for every heading, then checks every `](#...)` link. Streamlit's slug rule comes from the bundled frontend (`streamlit/static/static/js/StreamlitMarkdown.URFTuuY_.js`, function `Fp` calls a `slugify` with `separator:"-"`, `transliterate:true`, and collapses repeated separators).
- `refs.py`: pulls every backticked path and identifier out of the docs and greps for it across all tracked `*.py/*.R/*.sh/*.toml` files.
- `da_alpha.py`: runs `stats.da_anova.run_da_anova` on `example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx` with `alpha_interaction=0.10` and `0.0001` (Streamlit stubbed with `validation/_common._stub_streamlit`).
- Inline AST scripts for docstring coverage and for matching docstring parameter lists to signatures.

Datasets: sensochoc (DA), plus a structural read of all example files (shapes, dtypes, first rows).

## Findings

### DOC-01: Statistical methods reference contradicts the implemented code in places a user would copy into a methods section
- Severity: HIGH
- Confidence: VERIFIED
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
- Impact: the numbers the app produces are not affected. But this document is the only source a sensory scientist has for writing "analysed with FreeSense using ...". Items 1, 3, 4 and 8 would lead to a wrong methods description in a manuscript, and item 1 tells a reviewer that the implemented DA post-hoc is anti-conservative. That undermines trust in a tool whose selling point is statistical transparency.
- Recommendation: fix the ten passages above. Then add a check to `tests/`: a small table of documented defaults (bootstrap B, seeds, permutation counts, n_init, correction option lists, alpha_interaction default) asserted against the constants in code, so the two cannot drift again.
- Effort: M
- Dependencies: DOC-03 (same pattern for alpha_interaction); B01 for whether df = n_consumers - n_products is the right df.

### DOC-02: No ready-to-use methods text or per-module citation, and exports do not carry what a methods section needs
- Severity: HIGH
- Confidence: VERIFIED
- Location: `README.md:421-425` (Citation); `utils/export.py:334-560` (`build_run_parameters_sheet`); `Methods_Notes` writers at `utils/export.py:272` (RATA) and `2085` (CATA)
- Evidence: A grep of README and the methods reference for "cite", "methods section" and "reporting" finds only the single software citation "Danner, L. (2026). FreeSense ... (Version 1.0) [Software]", with no DOI, no `CITATION.cff` and no archived release. No module has a template paragraph (model, SS type, error term, post-hoc and correction family, software and version). A `Methods_Notes` sheet exists only for RATA and CATA. DA, Liking, Fusion and PrefMap have only `Run_Parameters`. `Run_Parameters` records `freesense_version` (`1.0.0`, which is also the tag on a commit 146 commits older, per 00-orientation flag 4) but no versions of statsmodels, scipy, scikit-learn or pingouin, which set the numerical engine.
- Impact: every user who publishes has to reverse-engineer a methods paragraph from a 257 KB developer-oriented document (and see DOC-01 for its errors). The recorded version string does not identify the code that ran, so a results table cannot be traced to a build.
- Recommendation: add a "How to report" block per module, both to the methods reference and as a `Methods_Notes` row in every export. It should be auto-filled from the run: model, SS type or LMM estimation method, error term actually used, post-hoc method and correction family, alpha, seeds and B, FreeSense version and git hash, and key dependency versions. Add a `CITATION.cff` and archive releases (for example with Zenodo) so the citation carries a DOI. Bump the version so the exported string identifies the build (see DOC-09).
- Effort: M
- Dependencies: Decisions D1 (version) and D3 (citation route).

### DOC-03: The interaction pre-test alpha is documented as not affecting product p-values; it does
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `Statistical_Methods_README.md:728`; `stats/da_anova.py:135-141` (docstring of `run_da_anova`)
- Evidence: both say the alpha_interaction threshold "does not affect the product p-values reported" or "Has no effect on the reported product p-values". The code (`stats/da_anova.py:353`, `int_sig = p_int < alpha_interaction`) uses it to pick the product F denominator. Run of `da_alpha.py` on sensochoc: with alpha_interaction 0.10 vs 0.0001, 8 of 14 attributes change p_product. For example, MilkF goes from 3.74e-40 (tested against Interaction) to 2.39e-51 (Residual), and Melting from 4.58e-12 to 5.24e-20. The in-app help (`modules/descriptive/workflow.py:242-249`) describes the behaviour correctly. The `run_da_anova` docstring also omits the `empty_cells` and `ss_type` columns it now returns.
- Impact: a user or reviewer who believes the setting is cosmetic may change it freely or fail to report it, although it changes the reported p-values and significance calls.
- Recommendation: replace the sentence in both places with "it selects the error term for the Product (and Assessor) F-test and therefore changes those p-values; it is recorded in Run_Parameters as alpha_interaction". Update the docstring's column list.
- Effort: S
- Dependencies: none

### DOC-04: README user guide is out of date with the code in several module sections
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `README.md` lines 136-157, 198, 207, 243, 263, 275, 283, 308, 368, 398
- Evidence:
  - Line 207 says the DA post-hoc default is Tukey-Kramer HSD. The default is FDR: `_DA_POSTHOC_OPTIONS = ["FDR (Benjamini-Hochberg)", "Tukey-Kramer HSD", ...]` with `index=0` (`modules/descriptive/workflow.py:231-236, 2496`).
  - Line 275 (and 368, 398) says the JAR penalty correction is configurable to Holm, Bonferroni, Sidak or BY "via the radio". `modules/liking/workflow.py:2596-2597` says "(not user-configurable)" and sets `correction_method = 'fdr_bh'`.
  - Line 263 says Liking Step 3 is a "two-way ANOVA (Type III SS ...)". Methods §24a and `stats/liking.py:952` are a mixed model with Wald chi-square tests (the OLS version was replaced, "review issue A1").
  - Line 154 (the orientation lead) says the CATA penalty caveat is "rendered as `st.caption` under every significant row". The code renders one caption that lists the significant attributes (`modules/cata/ui.py:2980-2990`), as CLAUDE.md states.
  - Line 142 says a banner warns when "more than 20%" of consumer blocks are dropped. `stats/shared/frequency.py:144-148` adds `q_warning` whenever `n_dropped > 0`, and the UI shows every warning (`modules/cata/ui.py:1330-1333`). The code is stricter than documented, and there is no 20% threshold.
  - Line 308 sends users to "Statistical Methods README §32 caveat" for the Q² CI. §32 is Autoscaling; the caveat is in §39 (line 2250).
  - Export sheet inventories: DA (line 243) says 14 or 15 sheets. The test pins 16 (`tests/test_export_rata.py:129-135`, including `Perf_Panel` and `Perf_Training`), or 17 with Contrast. RATA (line 198) says "12-sheet", but `TickingRatePerRep_Wide` is conditional (`utils/export.py:958`). CATA (line 157) omits `CLD_Summary` (`utils/export.py:2440`). Liking (line 283) omits `JAR_Distribution` (`utils/export.py:1447`).
  - Line 380 describes `utils/module_theme.py` as "per-module accent colours (RATA teal, ...)"; `utils/docs.py` is missing from the structure tree.
- Impact: users set up and interpret analyses from this page (it is also the in-app About page). A wrong default (DA post-hoc) and a non-existent option (JAR correction) directly mislead what gets reported.
- Recommendation: correct each line above. Generate the export sheet lists from the builders (or drop the counts) so they cannot drift.
- Effort: S
- Dependencies: none

### DOC-05: In-app help text mislabels the DA model and misdescribes the post-hoc options
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `modules/rata/ui.py:188-193`; `modules/descriptive/workflow.py:5, 199-208, 389, 755, 758-762, 791, 814, 1185`; `utils/ui_shell.py:72-74`
- Evidence:
  - The RATA and DA "Transparency note" captions say "FDR (Benjamini-Hochberg) is the most lenient and is the recommended default". Fisher LSD, which is also offered and is uncorrected, is more lenient than BH. The same captions call Tukey "the most conservative".
  - The DA model is labelled "mixed-effects ANOVA" or "Two-way mixed ANOVA" on the landing card and badge, the Step 2 banner, the "How to interpret" text, the results expander title and the run status text (line 389, the orientation lead). It is a fixed-effects OLS with Type III SS and a conditional error-term rule (`stats/da_anova.py:224-228, 292-298, 353`). Methods §15 explains the framing, but the UI labels alone would lead a user to write "mixed-effects model" in a paper. That implies a REML/lmer fit, which a mixed model would not make conditional in this way.
  - The Step 2 caption (line 759) says "a conditional F-test on the assessor term". The conditional rule selects the denominator of the Product (and Assessor) tests based on the interaction pre-test.
  - Line 1185 carries a stale inline comment, "model is mixed ANOVA (pingouin)"; the ANOVA does not use pingouin.
  - Minor, UX: the Step 1 run `st.status` writes all five progress lines (lines 386-391) before `run_full_da_analysis` is called, so the "Running ..." lines do not reflect progress.
- Impact: users choosing a post-hoc method are told the wrong ordering of leniency. The model name shown everywhere in the UI does not match what is computed, and that name is what users will report.
- Recommendation: rename to "Two-way ANOVA (OLS, Type III) with conditional error term" or "ANOVA with assessor as block", with one line pointing to §15 for the mixed-model rationale. Rewrite the correction caption as "LSD: no correction (most liberal); BH-FDR: controls FDR within attribute; Tukey: controls FWER within attribute (most conservative)". Fix the Step 2 caption. Emit the status lines between the actual pipeline stages.
- Effort: S
- Dependencies: none

### DOC-06: Data-format documentation does not let a new user format every module's file, and two shipped examples do not load where the docs say they should
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `README.md:78-93, 103-112, 320`; `example_data/README.md` (04_JAR and 05_Fusion_PrefMap sections); `modules/prefmap/workflow.py:548-600`; `modules/liking/workflow.py:571-640`
- Evidence:
  - README "Data Format" describes only the wide assessor x product x attributes layout, with one RATA/DA-style example. It does not describe:
    - Liking's single-liking-column long layout (README line 80 groups Liking under "wide format");
    - JAR coding (integers 1..k, with the middle code as JAR, and 3, 5 or 7 points; `modules/liking/workflow.py:579-583, 634-640`);
    - the demographics/secondary file keyed by consumer;
    - CATA's companion liking file;
    - PrefMap's three consumer inputs (Liking session, uploaded PC1/PC2 vectors, raw liking wide).

    In-app, every uploader shows an example table (10 `example_table=` sites), so the app itself is better than the README.
  - `Cocktail_consumer_liking.xlsx` is documented as "the consumer block for PrefMap" (example_data/README), and README line 320 says the PrefMap liking source is a "wide table: rows = products, columns = consumers". The file is long (`consumer, product, liking`; 1600 x 3, checked with pandas). PrefMap's raw-liking path treats every numeric non-product column as a consumer and rejects fewer than 5 (`modules/prefmap/workflow.py:590-600`). So the shipped example produces an error on the path the docs send the user to.
  - `JAR_sensominer.xlsx` holds French text levels (for example `sucre_pasassez`, `jar`), so JAR auto-detection (integer columns with 7 or fewer levels) never offers it. example_data/README says so, but adds that FreeSense "expects a numeric 5-point scale with a `_jar` suffix". No suffix rule exists in the code, and 3, 5 and 7 points are supported. As a result, no shipped dataset exercises the JAR penalty in the app.
- Impact: new users trying the documented example files for PrefMap and JAR hit errors or empty steps. Users formatting their own Liking/JAR/demographics files must rely on the in-app hints.
- Recommendation: add a per-module "File format" subsection to README (one small table each, including JAR coding and the demographics key). Ship a wide products x consumers version of the cocktail liking (or let PrefMap pivot a long file) and a numerically recoded JAR example. Correct the `_jar` suffix sentence.
- Effort: M
- Dependencies: B03 (upload/data handling) if the PrefMap loader is changed.

### DOC-07: Methods reference structure: TOC out of sync, broken in-app anchors, stale identifiers, internal jargon
- Severity: LOW
- Confidence: VERIFIED (anchor behaviour in a live browser SUSPECTED; see evidence)
- Location: `Statistical_Methods_README.md` TOC lines 13-114; headings at lines 1255, 1433
- Evidence:
  - The Chapter 3 TOC lists sub-sections 23a-23f with different names from the body: the body has 23a error term, 23b post-hoc options, 23c FDR consistency, 23d k_total, 23e CIs, 23f Hedges' g, 23g z-score, 23h edge cases, 23i references. §18e (panel flags) is missing from the TOC. "14b" has no 14a. Chapters 3 and 4 are `##` while the other chapters are `#`, so they render at a different level. Chapter 4's intro says "the five stats files" and then lists six.
  - Anchors (`anchors.py`): 55 TOC links; 1 is dead under GitHub slugs (`#10-hotellings-t-confidence-ellipses`, because the `²` is kept in the slug; SUSPECTED, since GitHub's exact handling of superscripts was not tested). Under Streamlit's slug rule (from the bundled JS: transliterate, `/` and `.` become `-`, repeated `-` collapse), 10 are dead in the in-app overlay: the `--` links (§12, 29, 32) and every `(stats/...py)` heading (§24-29), plus §10 and §48. Streamlit renders `#` links as same-page anchors (function `um` in the same bundle), so these 10 silently do nothing. This was not clicked in a real browser.
  - Stale identifiers (`refs.py`): `cochran_q_per_attribute` (lines 2547, 2819; actual `run_cochrans_q`), `_init_liking_state` (line 1614; no such function), `liking_pref_show_prefmap`, `liking_pref_show_vectors` and `liking_pref_grid_resolution` (line 1789; not keys in the code). The DA CHANGELOG entry points to "§17 (Empty assessor x product cells)", which is in §15.
  - Internal process codes ("Stage B, B.14", "R-25", "MAJOR-3", "D-7"): 31 in the methods reference, 38 in README. They mean nothing to users. None reach UI strings (grep of quoted strings in `modules/ utils/ core/` found none).
  - Developer material (session-state key lists, function names, "written for future developers") is mixed into the user-facing methods reference.
- Impact: navigation in the in-app reference partly fails. Readers meet references to things that do not exist and to internal ticket codes.
- Recommendation: regenerate the TOC from headings. Use heading text without `/`, `.` or dashes (or add explicit `{#id}`-free short headings) so both slug schemes agree. Normalise chapter levels. Replace or remove stage codes in user docs. Move session-state and function-level notes to docstrings or a developer doc.
- Effort: S
- Dependencies: DOC-08

### DOC-08: In-app About and Methods overlays: developer content, dead relative links, no search in a 257 KB page
- Severity: LOW
- Confidence: VERIFIED
- Location: `app.py:60-77`; `README.md:333-411` and links at lines 119, 393, 411, 417, 431-451
- Evidence:
  - The About overlay renders the whole README, including installation, "Project Structure", "Development Notes" and "Agent guidance: CLAUDE.md, .claude/agents".
  - The README's 7 relative links (`validation/README.md`, `Statistical_Methods_README.md`, `CLAUDE.md`, `CHANGELOG.md`, `LICENSE`, `example_data/`, `example_data/README.md`) are opened by Streamlit in a new tab against the app server, where those paths are not served.
  - The Methods overlay is a single `st.markdown` of 2,869 lines. It has no search beyond the browser's find, no per-module filtering, and no deep links from the steps: only two UI captions mention a section number (`modules/descriptive/workflow.py:762` §15, `modules/cata/ui.py:2465` §50), and neither is a link.
- Impact: end users see contributor material. Links in About go nowhere. Finding the method for the step you are on means scrolling a very long page.
- Recommendation: split user and developer content (for example `docs/USER_GUIDE.md` for the About overlay). Render the methods reference per chapter with a chapter selector (`st.selectbox` or `st.tabs` gated by `.open`), and add "Method details" links from each step to its chapter. Replace relative links in in-app documents with absolute GitHub URLs.
- Effort: M
- Dependencies: DOC-07

### DOC-09: Version and status claims in documents are inconsistent
- Severity: LOW
- Confidence: VERIFIED
- Location: `README.md:3, 338, 386, 425`; `Statistical_Methods_README.md:4`; `CHANGELOG.md:8, 201, 286-294`; `core/__version__.py`
- Evidence: README and the methods reference say v1.0. `__version__ = "1.0.0"`, and tag `v1.0.0` sits on a commit from 2026-05-18. CHANGELOG has `[Unreleased]`, `[1.1.0] - Unreleased` and `[1.0.0] - Unreleased`; the 1.0.0 entry says the tag "ships after sign-off", but it is already pushed. README line 40 refers users to "CHANGELOG 1.1.0, Fixed" for a version they cannot have, since the app reports 1.0.0. The methods reference does not say that Fusion and PrefMap are beta, although README and the UI do. CHANGELOG test pins were spot-checked and are accurate: all 12 `test_*` names cited in CHANGELOG.md and CLAUDE.md exist.
- Impact: the citation string and the exported version do not identify what users ran, and readers of the methods chapter on Fusion/PrefMap are not told the methods are beta.
- Recommendation: after the version decision, set one version in `core/__version__.py`, date the CHANGELOG heading, remove the stale "tag ships after sign-off" line, and add a beta note at the top of Chapters 5 and 6.
- Effort: S
- Dependencies: Decision D1

### DOC-10: stats/ docstrings are nearly complete; a few are stale or incomplete
- Severity: LOW
- Confidence: VERIFIED
- Location: `stats/multivariate.py:97, 163, 224`; `stats/pls.py:660`; `stats/shared/lsmeans.py:42`; `stats/da_anova.py:121`
- Evidence: an AST scan found 82 public module-level functions in `stats/`, of which 81 have docstrings. The one missing is `calculate_panel_stability` (multivariate.py:224). Of 39 private helpers, 1 lacks a docstring. Documented parameters vs signature (numpydoc sections only):
  - `calculate_pca` does not document `summary_df, selected_attrs, product_col, pca_type, apply_varimax`;
  - `run_cva` does not document `df_long, col_map`;
  - `fit_pls` does not document `seed`;
  - `additive_lsmeans` does not document `product_col, assessor_col`.

  No stale (documented but absent) parameters were found. `run_da_anova`'s docstring is wrong on behaviour and on columns (DOC-03). `stats/liking.py` names `n_consumers - n_products` "Satterthwaite" (DOC-01 item 4).
- Impact: small; the docstrings are generally good and match their signatures.
- Recommendation: add the missing docstring and parameter entries, and fix the two behavioural claims.
- Effort: S
- Dependencies: DOC-01, DOC-03

## Checked, nothing material found

- Methods §4 (RATA LMM: ML fits, random assessor intercept on replicate-averaged means) matches `stats/mixed_models.py:60-81`.
- §5a DA post-hoc SE description matches `stats/posthoc.py:144-157`.
- §15 SS type and empty-cell Type II switch match `stats/da_anova.py:224-326`; the alpha_interaction default 0.10 matches `_DA_DEFAULT_ALPHA_INTERACTION`.
- §24 imbalance threshold 5%, love/hate ratios 0.78/0.33 and the Kendall W 15% rule match `stats/liking.py:89-90, 147, 414`.
- §26 Welch test, two BH families and default penalty threshold (range x 0.055) match `stats/jar_penalty.py:174-250`.
- §27 Ward/Euclidean, `n_init=50`, k range min(n-1, 8), silhouette argmax, continuous guard (unique > 3 x clusters) match `stats/segmentation.py`.
- §29 `IDEAL_POINT_STABILITY_FACTOR = 3.0` matches `stats/prefmap.py:24`.
- §34b CV rules (LOO / 5-fold, seed 42), 1,000 default permutations and 1,000 Bayesian-bootstrap Q² draws for n < 10 match `stats/pls.py:19-24, 227-233, 570, 892`.
- §48 McNemar exact below 25 discordant pairs and no continuity correction match `stats/shared/frequency.py:446-489`.
- CATA filter default 20% (any product) matches `modules/cata/ui.py:92-93` and `stats/shared/frequency.py:358`.
- Panel stability 500 bootstraps with seed 42 match `stats/multivariate.py:11-12`, and the UI caption states it.
- The significance-star ladder in the methods preamble matches `utils/plotting._sig_stars`.
- README pingouin-optional claim matches `requirements.txt` comment and `modules/descriptive/workflow.py:1279-1298` captions.
- All example files listed in README exist.
- No internal stage/ticket codes appear in UI strings.
- CHANGELOG's cited test pins all exist.
- `docs/open-items.md` references a retired file only as history; that is not a defect.

## Decisions raised

- D1 Version: whether this release is 1.0.0 (re-tag) or 1.1.0/1.x. This drives the README and methods headers, the citation string and the exported `freesense_version` (DOC-09, DOC-02).
- D2 Model naming for DA: whether to keep "mixed-effects ANOVA" as the user-facing name, given that the computation is fixed-effects OLS with a conditional error term (DOC-05). This is a scientific-communication call.
- D3 Citation route: a DOI via an archived release, and/or a software paper, and what users should cite per module (FreeSense plus the method papers). Also whether to add a `CITATION.cff` (DOC-02).
- D4 Audience split: whether the in-app About page is a user guide or the repository README (DOC-08).
- D5 Shipping example data for PrefMap and JAR in a format the app accepts, or documenting the reshaping. This interacts with the GPL example-data decision already raised by B08.

## Leads for other areas

- B01: Liking pairwise df `n_consumers - n_products` (`stats/liking.py`) is neither Satterthwaite nor the RCBD residual df (n_c - 1)(n_p - 1). Check whether it is appropriate.
- B01: the JAR penalty Welch test pools consumer x product rows (dependence across products). The CATA penalty discloses this caveat; the JAR penalty does not appear to.
- B01/B03: Liking JAR auto-detection flags any integer column with 7 or fewer levels (`modules/liking/workflow.py:579-583`). Coded demographics (for example an age band 1-5) in the main file would be pre-selected as JAR columns, since `default=jar_candidates`.
- B01: unverified citations to check before release: "0.055 constant ... Gacula & Singh, 1984" (methods §26), "consistent with ISO 13299 practice" (§16), the McNemar cut-off at 25 "follows Meyners (2013)" (§48), and ISO 11132 as the source of the 0.10 pre-test alpha.
- B05/UX: Fusion hard-codes alpha 0.05 in "Restrict Y to significant attributes only (p < 0.05)" (`modules/fusion/workflow.py:767`) and in the permutation line "at alpha = 0.05" (line 2830), independent of the source module's alpha.
- B05/UX: the DA run status lines are cosmetic (DOC-05). Check the other modules' run handlers for the same pattern.
- B03: the CATA Cochran's Q dropout warning fires on any dropped consumer, one `st.warning` per distinct message. On data with scattered NaN this could flood Step 2.
