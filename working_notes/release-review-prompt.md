# Pre-release review and staged implementation plan

## 0. Release context (fill in before running)

- **App name and version to be released:** [name, version number]
- **Release type:** [e.g. public beta / general release / closed pilot with named partners]
- **Audience:** [e.g. sensory scientists in industry and academia; level of statistical literacy assumed]
- **Distribution / deployment:** [e.g. hosted on Posit Connect / shinyapps.io / Docker image / local R package install / desktop wrapper]
- **Licence and ownership:** [e.g. licence chosen or undecided; IP ownership confirmed or to be confirmed]
- **Platforms to support:** [OS, R version range, browsers]
- **Target release date:** [date]
- **Explicitly out of scope for this release:** [modules or features deliberately deferred]
- **Prior work to build on:** [paths to any earlier review outputs or reviewer prompts I want reused, or "none"]

Where a field is blank or says "undecided", treat it as an open decision to raise, not something to assume.

**Make no assumptions about the current state of the app.** It has changed substantially and any earlier description of it (including in old review documents, README files, comments or commit messages) may be out of date. Establish the current state from the code as it is now, and treat any document describing the app as a claim to verify, not a fact.

---

## 1. Your role and ground rules

You are the lead reviewer preparing a sensory and consumer data analysis application for its first release. Confirm the technology stack during orientation rather than assuming it. Your job in this session is to **review, diagnose and plan**. You must not modify application code, tests, data or configuration. The only files you may create are the output documents listed in section 6, written to `working_notes`.

Rules that apply throughout:

1. **Evidence before claims.** Every finding must cite file path and line range, a function name, or a reproducible command/input. If you could not verify something, label it `SUSPECTED` and say what would confirm it. Never present a suspicion as fact.
2. **Distinguish what you observed from what you infer.** Use `Observed:` and `Inferred:` where the distinction matters.
3. **Run things, don't just read them.** Where feasible, run `R CMD check`, the test suite, `lintr`, and execute analyses on test data to confirm behaviour. Record the exact commands and their outputs.
4. **No invented issues.** Do not pad categories for balance. An empty category with a one-line "reviewed, nothing material found, here is what was checked" is a valid result.
5. **Ask rather than assume** on anything that is a product, legal or scientific judgement call. Record it as a decision (section 5), not a finding.
6. **Handle prior work carefully.** If earlier review outputs are listed in section 0 or found in the repo, use them only as leads. For any fix they describe, confirm from the current code whether it is still present, still correct and covered by tests. Do not reopen a deliberate design choice unless you find a concrete defect, but do not treat anything as settled just because an old document says so.
7. **Writing conventions for all output:** British English spelling ("colour", "organise", "analyse"). Do not use em dashes; avoid en dashes as punctuation.

---

## 2. Phase A: Orientation (do this yourself, before spawning any subagents)

Build a shared map of the codebase that all later reviewers will use. Produce `working_notes/00-orientation.md` containing:

- Technology stack, repository structure, package structure (e.g. `DESCRIPTION`, `NAMESPACE`, `R/`, `inst/`, `tests/`, `vignettes/` if it is an R package), and how the app is launched.
- An inventory of every analysis module and feature that currently exists, with: entry point, UI module, server module, statistical functions called, inputs expected, outputs produced.
- Data flow from upload through validation, analysis, visualisation and export.
- Dependencies: every package in `Imports`/`Suggests`, its licence, and whether it is actually used.
- Current state of tests: framework, number of tests, what they cover, whether they pass (`devtools::test()`), and coverage (`covr::package_coverage()` if feasible).
- Result of `R CMD check --as-cran` (or `rcmdcheck::rcmdcheck()`), with every ERROR, WARNING and NOTE listed.
- Git state: branch, recent history, any TODO/FIXME/HACK comments (grep and list them).
- Any prior review outputs or prompts found in the repo, a one-paragraph summary of what they covered, and where they no longer match the current code.

Stop and check: if the orientation reveals the section 0 context is wrong or incomplete (e.g. a module exists that is not mentioned, or the app clearly targets a different deployment), flag it at the top of the orientation document.

---

## 3. Phase B: Parallel review

Spawn one subagent per review area below. Give each subagent: this prompt's section 1 rules, the orientation document, the relevant section 0 context, and its specific brief. Each subagent writes `working_notes/B<nn>-<area>.md` using the finding format in section 4. Subagents must not edit code.

### B01 Statistical correctness
- If a statistical reviewer prompt is listed in section 0, use it as an additional checklist, not a replacement for this brief.
- For every analysis: confirm the model specification matches the stated method (fixed vs random effects, panellist and session handling, interaction terms), the test statistic, degrees of freedom, multiple-comparison adjustment, and effect sizes.
- Validate numerical output against an independent reference for at least one dataset per analysis (e.g. published worked examples, `SensoMineR`, `FactoMineR`, `lme4`/`lmerTest`, `emmeans`, `ordinal`). Record the reference, the tolerance used, and the comparison.
- Edge cases: unbalanced designs, missing values, a single session, a single replicate, panellists who never use an attribute, all-zero or constant attributes, ties, very small panels, rank-deficient designs, convergence failures and singular fits. For each: what does the app do, and is that behaviour correct and communicated to the user?
- For any statistical fix described in prior review documents, confirm it against the current code as per section 1, rule 6.

### B02 Functional behaviour and user workflow
- Walk every module end to end as a user would, using the bundled or test datasets. Note anything that crashes, hangs, silently produces wrong output, or produces output the user would find confusing.
- Input validation: what happens with wrong column names, wrong types, extra columns, duplicated rows, factor levels with special characters or non-ASCII (including umlauts), very long attribute names.
- Error messages: are they understandable to a sensory scientist, and do they tell the user how to fix the problem?
- State handling: changing inputs mid-analysis, re-uploading data, navigating between modules, browser refresh.

### B03 Data import, export and reporting
- Supported formats (CSV, XLSX, others), encodings (UTF-8, Latin-1, Windows-1252), delimiters and decimal separators (including European decimal commas).
- Exports: tables, plots, reports. Check numerical precision, labelling, reproducibility (does the export record the method, settings, software version and date?), and file naming.
- Plot quality for publication: resolution, sizing, fonts, colour palettes (colour-blind safe?), axis labels and legends.

### B04 Code quality and architecture
- Shiny module structure, reactive graph (unnecessary recomputation, reactive leaks, observers that should be `bindEvent`), separation of statistical logic from UI.
- Duplication, dead code, unused functions and dependencies, inconsistent naming.
- Error handling (`tryCatch`, `validate`/`need`, `req`) and logging.
- `lintr` results summarised by rule, not listed exhaustively.
- Identify the few structural changes that would most reduce risk for this release; separate these from nice-to-have refactors.

### B05 Testing
- Map tests against modules and statistical functions; list untested critical paths.
- Are there reference-value tests (known inputs, known correct outputs) for every statistical method? If not, which are missing?
- UI testing: is `shinytest2` (or similar) used? What minimum smoke tests would give confidence for release?
- Propose a concrete minimum test set required before release, prioritised.

### B06 Performance and robustness
- Time each analysis on a realistic large dataset (state the size used, e.g. panellists x products x attributes x replicates). Identify bottlenecks with `profvis` or timing where useful.
- Memory use and behaviour with multiple concurrent users if the deployment target is hosted.
- Long-running operations: is there progress feedback, and can the user cancel?

### B07 Security, privacy and data handling
- File upload handling: size limits, file type checking, path handling, anything written to disk and whether it is cleaned up.
- Any code evaluation of user input (`eval`, `parse`, formula construction from user strings).
- Secrets, credentials or internal paths committed to the repository (search full git history, not only the current tree).
- Personal data: panellist data can identify people. Where is data stored, for how long, who can see it in a hosted deployment, and what the app should say about this. Flag relevant obligations (e.g. Australian Privacy Act, GDPR if EU users are expected) as decisions, not legal conclusions.

### B08 Packaging, licensing and release engineering
- `DESCRIPTION` completeness (version, authors and roles, licence, URLs, BugReports, dependencies with minimum versions).
- Licence compatibility of every dependency with the chosen (or candidate) licence for the app. Flag any GPL-family dependency and what it implies.
- Versioning scheme, `NEWS.md`, changelog, `CITATION` file, DOI (e.g. Zenodo) for academic citation.
- Build and deployment reproducibility: `renv` lockfile, Dockerfile or deployment manifest, CI (GitHub Actions for check and tests).
- Anything needed for the specific distribution channel in section 0.

### B09 Documentation and scientific transparency
- User documentation: getting started, data format specification with example files, per-module guidance.
- Method documentation: for each analysis, the model, assumptions, references to the literature, and interpretation guidance. A sensory scientist must be able to report "analysed with [app name and version] using X" and describe it in a methods section.
- In-app help text: accurate, consistent with the code, and consistent with the method documentation.
- Function-level documentation (`roxygen2`) completeness.

### B10 Interface, accessibility and presentation
- Visual consistency, layout on common screen sizes, terminology consistency across modules (e.g. "panellist" vs "assessor", "attribute" vs "descriptor").
- Accessibility basics: keyboard navigation, contrast, alt text or text equivalents for plots, colour-blind safe palettes.
- Branding, about page, version display, contact or feedback route, disclaimer.

---

## 4. Finding format

Every finding in every B-report uses this structure:

```
### <AREA>-<nn>: <short title>
- Severity: BLOCKER | HIGH | MEDIUM | LOW
- Confidence: VERIFIED | SUSPECTED
- Location: <file:lines, function, or module>
- Evidence: <what was observed, command run, input used, output seen>
- Impact: <who is affected and how; for statistical issues, whether results could be wrong>
- Recommendation: <specific fix>
- Effort: S (under 2h) | M (half day to 2 days) | L (more than 2 days)
- Dependencies: <other findings or decisions this relies on>
```

Severity definitions:
- **BLOCKER:** could produce incorrect scientific results without warning, loses or exposes user data, crashes a core workflow, or creates a legal/licensing problem. Must be fixed before release.
- **HIGH:** significantly degrades a core workflow or user trust; should be fixed before release unless explicitly accepted.
- **MEDIUM:** noticeable problem with a workaround; can be scheduled for a point release.
- **LOW:** polish.

---

## 5. Phase C: Verification and consolidation

Once all subagents have finished:

1. **Independent challenge pass.** Spawn a fresh subagent that has not seen the reviewers' reasoning. Give it the list of BLOCKER and HIGH findings only (titles, locations, evidence) and ask it to try to reproduce or refute each one. Downgrade or remove any that it cannot reproduce, and record why.
2. **Deduplicate and merge** overlapping findings across areas; keep the strongest evidence.
3. **Write `working_notes/01-findings-register.md`:** one consolidated table (ID, title, area, severity, confidence, effort, status after challenge) followed by the full findings, ordered by severity.
4. **Write `working_notes/02-decisions.md`:** every open question that needs my judgement rather than engineering effort. For each:
   - The decision to be made, and why it matters for release.
   - Two to four realistic options, with trade-offs.
   - Your recommendation and reasoning, clearly labelled as a recommendation.
   - What is blocked until it is decided.

   Expect decisions in areas such as: release scope (which modules ship), licence and IP ownership, deployment model, data retention and privacy statement, default statistical settings where more than one defensible choice exists, supported platforms and R versions, and naming/terminology conventions.

---

## 6. Phase D: Staged implementation plan

Write `/working_notes/03-implementation-plan.md` that turns the findings and decisions into staged work.

Requirements:

- **Stage 0: Decisions.** The decisions from `02-decisions.md` that block later stages, in the order they need to be made.
- **Stages 1 to N:** grouped so each stage is coherent and can be completed, tested and committed on its own branch. A sensible default ordering is: safety net first (tests and CI that later changes rely on), then correctness blockers, then data handling and robustness, then documentation and packaging, then polish. Change this ordering if the findings justify it, and say why.
- For each stage: goal; findings addressed (by ID); files likely touched; entry criteria; exit criteria (concrete and checkable, e.g. "`R CMD check` returns 0 errors, 0 warnings", "reference tests pass for every analysis within 1e-6"); estimated effort; risks.
- A clear **release line**: which stages must be complete before the release ships, and which can follow in a point or minor release.
- A **release checklist** as the final section: the short list of checks to run on the release candidate itself.
- Each stage should be written so that it could be handed to a Claude Code session as a self-contained task, with enough context to execute without re-reading all review documents.

---

## 7. Final summary and stopping point

Finish by writing `/working_notes/readme.md` with:

- Five to ten lines of overall assessment: is the app close to releasable, and what are the few things that matter most.
- Counts of findings by severity (before and after the challenge pass).
- The decisions I need to make first.
- Links to all other review documents.

Then **stop**. Do not begin implementing any stage. I will review the findings, make the decisions, and instruct you which stage to start.
