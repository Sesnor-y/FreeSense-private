# 02 Decisions for the owner

Review of FreeSense at `bcaf9f8`, 2026-09-26. These are the questions that need your judgement rather than engineering effort. Each is written so it can be answered on its own. Finding IDs refer to `01-findings-register.md`.

Section 0 of the review prompt (release context) was left blank, so decisions D-01 to D-04 are the context itself. They come first because almost every severity rating for security, performance and packaging changes with them.

Order in which to decide: **D-02 deployment, D-03 repository and history, D-01 version, D-06 scope**, then D-04 and D-05 (licensing), then the statistical policies D-07 to D-09, then the rest. Section "Blocked until decided" at the end gives the dependency map.

---

## D-01 Version number and version policy

**Decision.** What version the release carries, and when the version string must change.

**Why it matters.** `core/__version__.py` says `1.0.0`. A local, unpushed tag `v1.0.0` sits on a commit from 2026-05-18, 146 commits behind `main`, and `CHANGELOG.md` has `[1.0.0] Unreleased`, `[1.1.0] Unreleased` and `[Unreleased]`. Every export writes `freesense_version = 1.0.0` into `Run_Parameters`, so today that stamp cannot tell a user which statistical engine produced a workbook (IO-06, REL-05, DOC-09). A reviewer or journal asking "which version?" has no reliable answer.

**Options.**
1. **Delete the local tag, release `main` as 1.0.0.** Clean story ("first public release"); the tag was never pushed, so nobody depends on it. Changelog sections merge into one 1.0.0 entry.
2. **Keep history honest: release as 1.1.0** (the May state was 1.0.0 internally). Accurate to the changelog, but implies a public 1.0.0 that never existed.
3. **Release as 0.9.x / 1.0.0-beta** and reserve 1.0.0 for when Fusion/PrefMap leave beta and the validation gaps close. Signals maturity honestly; some users read 0.x as "not for publication work".

In all cases add a policy: any change under `stats/` bumps at least the patch version, and exports also record the git commit (IO-06).

**Recommendation.** Option 1, with the policy. The tag is local, so re-tagging costs nothing, and "1.0.0" matches every document already. If you choose to ship Fusion/PrefMap, the beta label on those modules is enough; the whole app does not need a 0.x number.

**Blocks.** Stage 5 (version single-sourcing, changelog, citation), the About rewrite, CITATION.cff.

**Decided.**: Option 1

---

## D-02 Deployment model

**Decision.** How users will run FreeSense: local install only, a hosted instance, or both.

**Why it matters.** It sets the severity of about a dozen findings. Hosted, Streamlit runs every user in one process: CPU-bound runs block each other (PERF-04, measured 0.95x speed-up with 4 threads), uploads up to 200 MB and zip-bomb xlsx files are unrestricted (SEC-02), panellist data sits in shared memory with no expiry (SEC-05), users see full tracebacks (SEC-06), and a browser refresh loses all work (FUNC-09). Locally most of these are LOW. Streamlit has no authentication of its own.

**Options.**
1. **Local install only** (clone + `pip install`, or a packaged installer later). Minimal extra work; data never leaves the user's machine once SEC-03 is fixed. Barrier: users must install Python.
2. **Public hosted instance** (for example Streamlit Community Cloud). Easiest for users; needs upload/size caps, a privacy notice, cross-border data questions (Community Cloud is US-hosted), resource limits, and makes SEC-02/SEC-05/PERF-04 release blockers.
3. **Institutional or private hosted instance** (behind your organisation's login). Controlled audience; needs a Docker image or server config and an operator.
4. **Local first, hosted later.** Ship option 1 now; plan option 2 or 3 for a point release.

**Recommendation.** Option 4. Everything needed for a safe local release is small (Stage 1 to 4 of the plan); a hosted instance adds a block of work (limits, privacy, auth) that should not hold up the first release.

**Blocks.** Severity of SEC-02, SEC-05, SEC-06, PERF-04, FUNC-09; content of Stage 6 (deployment); the privacy statement (D-11).

**Decided.**: Option 1: local install only
---

## D-03 Repository visibility and git history

**Decision.** Whether the GitHub repository becomes public, and if so whether the existing history is published.

**Why it matters.** The repository is private today (REL-01: unauthenticated requests return 404), so README's clone command and citation URL fail for everyone else. The pushed history contains third-party files: an XLSTAT tutorial workbook with VBA macros (`LIK_tuto_EN.xlsm`, creator Fabien Llobell), XLSTAT PLS training slides (`PLS.pptx`) and `docs/PLS.pdf` of unknown origin (SEC-04). Publishing the history redistributes them. The history also contains 130 absolute home paths and private dataset file names (SEC-08). Whether you may redistribute those files is a legal question this review does not answer.

**Options.**
1. **Fresh public repository** with a single squashed initial commit from the release state; keep the private repo as the development archive. Simplest and safest; loses public commit history.
2. **Rewrite history** (`git filter-repo`) to strip the files and paths, then make the repo public. Keeps history; every existing clone must be re-cloned; easy to miss something.
3. **Stay private**, distribute releases as source archives (for example Zenodo). No history exposure; users cannot file issues or see development.
4. **Publish as-is.** Only if you have confirmed permission to redistribute the three files. Not recommended.

**Recommendation.** Option 1. It removes SEC-04, SEC-08 and the broken `.claude/skills` symlink (REL-12) in one step, and you can decide separately whether `.claude/` (agent definitions) belongs in the public repo (default: exclude).

**Blocks.** REL-01, SEC-04, REL-10 (DOI via GitHub-Zenodo integration needs a public repo), the support channel (D-12).

**Decided.**: I've already renamed the repo to FreeSense so not sure if I can re-name? If re-naming and then preparing a fresh public repo with the correct name works happy with option 1.

---

## D-04 pingouin (GPL-3.0) dependency

**Decision.** What to do about the one GPL-3.0 package the MIT-licensed app installs and imports.

**Why it matters.** `pingouin` is in `requirements.txt` and imported (inside `try/except`) at `stats/panel_performance.py:22` for ICC confidence intervals only. The README licence section does not mention it (REL-03). The common reading, which is not legal advice, is: publishing MIT source that imports a GPL library is generally accepted; a hosted service is not distribution under GPL-3.0; a Docker image or installer that bundles pingouin is distribution and carries GPL obligations. Separately, pingouin's CI block is the cause of the DA crash on small designs (PERF-02) and about 75% of DA run time (PERF-03).

**Options.**
1. **Replace it** with a closed-form F-based ICC(3,1) confidence interval (about 10 lines of code plus a reference test). Removes the licence question, the crash and most of the run time. Needs a validation against the published formula (McGraw and Wong 1996).
2. **Make it a genuinely optional extra** (not in `requirements.txt`; documented `pip install pingouin` for CIs). Licence exposure only for users who opt in; CIs absent by default.
3. **Keep and document** it in the README licence section. Least work; any bundled distribution becomes GPL-bound.
4. **Relicense FreeSense as GPL-3.0.** Consistent with the GPL example data and R ecosystem; restricts some commercial reuse.

**Recommendation.** Option 1. It fixes a BLOCKER-class crash and a performance problem at the same time as the licence question.

**Blocks.** Stage 2 (the PERF-02 fix is simplest once this is decided), Stage 5 licence text.

**Decided.**: option 1

---

## D-05 Bundled example datasets (GPL >= 2)

**Decision.** How the seven SensoMineR / cata datasets in `example_data/` ship.

**Why it matters.** They are the validation data for `tests/test_validation_pins.py` and the only worked examples users get. They are GPL (>= 2) and README says so, but no copy of the GPL text ships (REL-08). Two of them do not load in the module the docs point them to (FUNC-07/DOC-06: the Cocktail consumer file is long-format but PrefMap wants wide; the JAR example uses text levels).

**Options.**
1. **Keep bundling**, add `example_data/COPYING` (GPL text), and fix or reshape the two examples.
2. **Move to a separate data repository or download**; tests fetch or skip. Cleaner licence boundary; 94 tests skip without the data (TEST-08).
3. **Replace with synthetic MIT datasets** for the user-facing examples, keep the GPL sets for validation only.

**Recommendation.** Option 1 for this release (small effort), with option 3 considered later if the GPL mix bothers downstream users.

**Blocks.** Stage 5 (docs and licence files).

**Decided.**: Option 1

---

## D-06 Release scope: Fusion and PrefMap (beta)

**Decision.** Whether the two modules marked beta in `core/config.py` ship in this release.

**Why it matters.** Both are flagged beta in the UI and export. Fusion has a verified silent Q² collapse (STAT-04). PrefMap's shipped example does not load (FUNC-07). Both have the lowest test coverage in the app (44% to 75% line coverage for their UI files) and no test of the precomputed-means loader (TEST-06). Shipping them adds roughly a day of fixes and tests to the release line.

**Options.**
1. **Ship both as beta**, with STAT-04 and FUNC-07 fixed and the loader tested.
2. **Ship with beta label, fix nothing extra.** Fast; STAT-04 can give a wildly wrong Q² silently, which is a BLOCKER even for beta.
3. **Hide both** (remove from `MODULES` or put behind a flag) for 1.0.0 and release them in 1.1.
4. **Ship PrefMap only** (small, 0.1 s runtime, lower risk) and hold Fusion.

**Recommendation.** Option 1. The two fixes are small (STAT-04 is a one-line tolerance guard plus a test), and the beta label already sets expectations.

**Blocks.** Scope of Stages 2 and 3; test set items for Fusion/PrefMap.

**Decided.**: Option 1

---

## D-07 Liking statistics: contrast degrees of freedom and cluster p-values

**Decision.** Two scientific policies in the Liking module.

**Why it matters.**
- *Contrast df (STAT-02).* Pairwise contrasts use df = n_consumers minus n_products, which is neither the paired-t df nor the RCBD df; for 10 consumers x 6 products it gives 4 where the complete-design RCBD error df is 45. The contrast and the CLD letters disagree on a large share of comparisons.
- *Cluster ANOVA (STAT-01).* After segmentation, the app tests liking differences between the clusters it just built from the same liking scores and marks them ★. On pure noise this flags products as significant every time. This is a well-known circularity ("double dipping").

**Options for contrast df.**
1. RCBD residual df from the fitted model (exact for complete designs); flag incomplete designs.
2. Satterthwaite or Kenward-Roger df (correct for incomplete designs; needs an implementation, statsmodels does not provide it for MixedLM).
3. Paired-t per pair (df = n_pairs minus 1), consistent with RATA's FDR/LSD path.

**Options for cluster tests.**
1. Remove p-values and ★ from the cluster comparison; present it as descriptive (means and effect sizes).
2. Keep p-values with a prominent "not valid inference: clusters were formed on these data" caveat.
3. Replace with a validity check (for example split-sample or permutation of the clustering).

**Recommendation.** Contrast df option 1 (it matches the CLD and the LMM; the incomplete-design case is flagged until option 2 exists). Cluster option 1: descriptive only. Both are the textbook position; neither needs new dependencies.

**Blocks.** Stage 2 items STAT-01 and STAT-02.

**Decided.**:  agree with recommendations and option 1 for contrast df and cluster tests

---

## D-08 RATA Tukey: one error term

**Decision.** Which error term the RATA Tukey path uses for both the letters and the pairwise contrast.

**Why it matters.** The RATA Tukey CLD uses the pooled assessor-blocked residual MS; the RATA contrast step, also labelled Tukey, uses a paired SE with df n minus 1 (STAT-03). On sensochoc 16 of 420 pairs disagree in both directions, so a user can see "same letter" and "significant difference" for the same pair. DA and RATA's FDR/LSD paths are consistent.

**Options.** (1) Use the pooled blocked error term in both (matches Tukey HSD's definition and the CLD). (2) Use the paired SE in both (robust to heterogeneous pair variances, but then it is not Tukey HSD). (3) Keep both but relabel the contrast.

**Recommendation.** Option 1.

**Blocks.** Stage 2 item STAT-03.

**Decided.**: Optpion 1

---

## D-09 Input formats in scope

**Decision.** Which file conventions the release supports.

**Why it matters.** Decimal-comma numbers are silently zero-filled in RATA and dropped in DA (IO-02, FUNC-06); semicolon CSVs load as one column; Latin-1/Windows-1252 files give raw codec errors; `.xls` is offered but cannot be read (no `xlrd`); upper-case `.CSV` fails; only the first sheet of a workbook is read (IO-03/04/05, FUNC-05). A European sensory audience will hit these on day one. Whatever is decided, the loader must refuse input it cannot read correctly rather than guess (that part is not optional and is in Stage 2).

**Options.** (1) Support European CSV (auto-detect delimiter and decimal, try UTF-8 then cp1252) and let the user choose the sheet; drop `.xls` or add `xlrd`. (2) Support UTF-8 comma CSV and `.xlsx` only, reject everything else with a clear message telling the user how to re-save. (3) Option 2 now, option 1 in a point release.

**Recommendation.** Option 3. Refusal with a clear message is small and closes the silent-wrong-result path; auto-detection is more work and needs its own tests.

**Blocks.** Stage 3 scope.

**Decided.**: Happy with option 2

---

## D-10 Supported Python versions and platforms

**Decision.** What the release promises.

**Why it matters.** README claims Python 3.11 to 3.14; only 3.14 has ever been tested; Python 3.10 cannot install (numpy floor) although ruff targets py310; there is no CI and no lockfile (TEST-01, REL-04, REL-06). kaleido 0.2.1 (image export) has a suspected Windows hang (IO-11, not tested). A fresh install today already resolves a release-candidate `wrapt`.

**Options.** (1) Promise 3.11 to 3.14 on Linux, macOS and Windows, backed by a CI matrix. (2) Promise 3.12 to 3.14, Linux and macOS tested in CI, Windows "best effort". (3) Promise exactly one Python and ship a lockfile.

**Recommendation.** Option 2 plus a constraints/lock file for reproducibility. Windows is likely important for sensory scientists, so run at least one manual Windows smoke test before release, specifically the kaleido export.

**Blocks.** Stage 1 (CI matrix), Stage 5 (README claims).

**Decided.**: Option 2

---

## D-11 Privacy statement and raw identifiers in exports

**Decision.** What the app says about data handling, and whether raw panellist/consumer IDs and demographics go into every export.

**Why it matters.** There is no privacy or data-handling statement anywhere (SEC-05). Every workbook includes a `Raw_Data` sheet with IDs, and Liking can include demographics. For a hosted instance, obligations under the Australian Privacy Act 1988 and, for EU users or panellists, the GDPR may apply; this is a legal question for you or your institution, not concluded here.

**Options.** (1) Local-only statement: "your data never leaves your computer; nothing is stored after you close the tab" (true once SEC-03 is fixed). (2) Full privacy notice for a hosted instance. (3) Additionally make `Raw_Data` opt-in, or pseudonymise IDs in exports.

**Recommendation.** Option 1 now (with D-02 option 4); make raw data an export checkbox defaulting to on, so users who share workbooks can leave it out.

**Blocks.** Stage 4 text; Stage 6 if hosted.

**Decided.**: Option 1 as only local deployment

---

## D-12 Support channel and disclaimer

**Decision.** How users report problems, and whether the app carries a "verify your results" disclaimer.

**Why it matters.** There is no help or bug-report route in the app or README (UI-08, REL-07), and no disclaimer beyond the MIT text (not reachable in-app) and the beta note.

**Options.** Support: GitHub issues (needs a public repo, D-03), an email address, or a form. Disclaimer: none; one line in About and the landing footer; also in every export's `Run_Parameters`.

**Recommendation.** GitHub issues plus one disclaimer line in About, landing footer and exports. Set Streamlit's `menu_items` to point at them.

**Blocks.** Stage 4 (UI-08, UI-09).

**Decided.**: happy with recommendation, need to set up an email to use for the app and can add later


---

## D-13 How strongly to claim "validated against R"

**Decision.** The wording of validation claims in README, About and methods docs.

**Why it matters.** The frozen R references are genuine R output, but several are R re-implementations of FreeSense's own algorithm rather than independent engines (DA CLD, PrefMap model selection, VIP, ICC), every reference uses one balanced complete dataset, R has not been re-run since July, and the September unbalanced-data paths have no reference (TEST-05, B01 validation note).

**Options.** (1) Keep the claim, add a precise coverage table (already in `validation/README.md`) linked from the About page. (2) Weaken to "cross-checked against R on published datasets" and list exceptions. (3) Close the gaps before release (re-run R, add unbalanced references).

**Recommendation.** Option 2 for release plus a re-run of the R suite on the release candidate (release checklist). Option 3 over the next minor release.

**Blocks.** Stage 5 wording.

**Decided.**: Option 2

---

## D-14 User-facing name of the DA model

**Decision.** Whether DA keeps calling its model "mixed-effects ANOVA".

**Why it matters.** The computation is fixed-effects two-way OLS with a conditional error term (Assessor x Product MS used as the error when the interaction is significant). The UI and docs call it "mixed-effects ANOVA" (DOC-05; `modules/descriptive/workflow.py:389`). Some sensory texts do call this the "mixed model" approach because the interaction-MS denominator is what a random-assessor model implies, so this is a communication choice, not a defect in the arithmetic.

**Options.** (1) "Two-way ANOVA (assessor as random: product tested against the interaction when significant)". (2) Keep "mixed-effects ANOVA" and explain the equivalence in the methods doc. (3) "Mixed-model ANOVA (conditional F-test)".

**Recommendation.** Option 3 with one explanatory sentence; it matches sensory convention and states the mechanism.

**Blocks.** Stage 5 doc edits only.

**Decided.**: Option 3

---

## D-15 Accessibility target and default palette

**Decision.** Whether the release claims a WCAG level, and whether the colour-blind-safe palette becomes the default.

**Why it matters.** The brand teal on primary buttons is 3.74:1 (fails AA for text, UI-03); the Liking penalty table is near-invisible on the dark theme (UI-02); the default product palette has pairs indistinguishable under deuteranopia/protanopia and the "colour-blind safe" palette contains a yellow at 1.32:1 on white (UI-06, IO-10); semantic red/green ignores the colour-blind setting (UI-05).

**Options.** (1) No formal claim; fix UI-02 and UI-03 (cheap, affect everyone). (2) Claim WCAG 2.1 AA for the UI; all of UI-02, -03, -05, -06, -11 become release work. (3) Option 1 plus make a corrected colour-blind palette the default.

**Recommendation.** Option 3. Colour-blind-safe defaults cost nothing for other users and about 1 in 12 men benefit.

**Blocks.** Stage 4 palette work.

**Decided.**: Option 3 is fine and if it looks weird we can always change it to some other scheme

---

## D-16 RATA positioning

**Decision.** Whether RATA is presented as a consumer method or a trained-panel method.

**Why it matters.** The landing page files RATA under "Trained panel"; README says "consumer / semi-trained" (UI-09). The literature mostly uses RATA with consumers (Ares et al. 2014, Food Quality and Preference 36; Meyners, Jaeger and Ares 2016). This affects labels only.

**Recommendation.** Consumer (and semi-trained) panels, consistently.

**Blocks.** Stage 4 copy.

**Decided.** The 3 column layout doesn't really reflect the purpose of the methods. As there are 3 consumer method, one trained-panel, 2 data matching. Or alternatively my pefered classification 3 profiling methods DA, RATA and CATA, then 1 consumer acceptance and 2 data matchning and mapping.

---

## D-17 Supported study size

**Decision.** Whether to state and enforce a maximum study size.

**Why it matters.** A 1,000-attribute file ran for 102 s; DA at stress size with Tukey took 190 s; a 194 MB CSV extrapolates to about 10.6 GB in long format (PERF-03, PERF-04). Locally this is only slow; hosted it can take the server down.

**Options.** (1) Document tested sizes, no enforcement. (2) Soft warning above a threshold (for example 200 attributes or 500,000 long rows). (3) Hard caps (required if hosted).

**Recommendation.** Option 2 locally; option 3 if D-02 includes hosting.

**Blocks.** Stage 3 (limits), Stage 6.

**Decided.** Warning is good but would make it a bit stricter as more than 50 attributes are a lot, similarly more than 50000 rows seems excessive  

---

## D-18 Export precision policy

**Decision.** Whether exported workbooks hold full-precision values with display formats, or rounded "report" values.

**Why it matters.** p-values are exported at full precision with a display format, but many other values are rounded to 3 dp in the stats layer or builders, and some rates are stored as text (IO-08, TEST-04). Rounded exports cannot be re-analysed or compared to other software beyond 3 dp.

**Recommendation.** Full precision everywhere, rounding only through Excel number formats (the convention already used for p-values). Keep the stats layer free of rounding.

**Blocks.** Stage 3 export work.
**Decided.** agree with the recommendation

---

## D-19 Citation route

**Decision.** How academic users cite FreeSense.

**Why it matters.** README has a citation line pointing to a private URL; there is no `CITATION.cff`, no DOI, and no ready-made methods paragraph per module (DOC-02, REL-10).

**Options.** (1) `CITATION.cff` plus a Zenodo DOI per release (needs a public repo, D-03). (2) A software paper (for example JOSS) later. (3) Per-module "how to report this analysis" text in the app and in each export's `Methods_Notes`.

**Recommendation.** (1) and (3) for this release; (2) later.

**Blocks.** Stage 5.

**Decided.** 3 for realease now and consider 1 and 2 down the track. 

---

## D-20 CATA and JAR penalty independence

**Decision.** Whether shipping Welch t-tests for penalty analysis, which assume consumer evaluations are independent across products, is acceptable for release.

**Why it matters.** This is a documented, deliberate design choice (CLAUDE.md; a caveat caption is shown in CATA and JAR). B01 did not classify it as a defect. It is raised only because a reviewer of a paper might question it.

**Options.** (1) Ship as is with the caveat. (2) Replace with a consumer-blocked model (mixed model or permutation within consumer) in a later release.

**Recommendation.** Option 1 for this release; option 2 on the roadmap.

**Blocks.** Nothing in the release line.

**Decided.** ship as is

---

## D-21 About page audience

**Decision.** Whether the in-app About page is a user guide or the repository README.

**Why it matters.** The About overlay renders the whole README, including developer and agent notes, 7 relative links that do not work in-app, and step names that no longer match the app (UI-09, DOC-08).

**Recommendation.** A short user-facing About (what it is, version, how to cite, licence, disclaimer, support link) with the README kept for developers.

**Blocks.** Stage 4.

**Decided.** Yes, short user-facing about and clean up readme for release

---

## Blocked until decided

| Decision | Blocks |
|---|---|
| D-02 deployment | Severity of SEC-02/05/06, PERF-04, FUNC-09; Stage 6 entirely; D-11, D-17 |
| D-03 repository | REL-01, SEC-04, REL-12; D-12 support channel; D-19 DOI |
| D-01 version | Stage 5 version/citation work; About rewrite |
| D-06 scope | Fusion/PrefMap parts of Stages 2, 3 and the test set |
| D-04 pingouin | Simplest fix of PERF-02; Stage 5 licence text |
| D-07, D-08 | Stage 2 statistical fixes STAT-01/02/03 |
| D-09 formats | Stage 3 loader scope beyond "refuse clearly" |
| D-10 platforms | Stage 1 CI matrix |
| D-05, D-12 to D-21 | Stage 4 and 5 content only; none blocks correctness work |
