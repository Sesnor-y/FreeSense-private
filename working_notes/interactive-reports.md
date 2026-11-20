# Interactive report export: review and plan

Review 2026-10-12, on `feature/interactive-exports` (branched from `main` at `fb54905`). This is the "HTML report" that `working_notes/contrast-fix.md` deferred (D.5, §8: "HTML report, product cards and takeaway titles"). It covers all six modules.

**Goal.** A single file a sensory scientist can send to a colleague, client or manager. It leads with the visuals and keeps the statistics one click away. It is not a replacement for the Excel workbook, which stays the complete numerical record.

**Two owner constraints (2026-10-12) override everything below:**

- **C-1. The charts stay as they are.** A lot of design work went into them. The report shows the same figures the app shows, with no restyling, resizing or re-colouring. Where the report cannot show a figure exactly as on screen, that is a defect in the report, not a reason to adjust the figure.
- **C-2. Easy to adjust later.** Sections, their order, captions, styling and report-only figure settings each live in one obvious place (§3.6), so a later tweak is a one-file change.

**Status (2026-10-13): all four phases done; Phases 1–2 committed, Phases 3–4 uncommitted; reports in §7.1–§7.4.** The owner decided D-R1, D-R2, D-R4 and D-R9 (§6) and accepted D-R3, D-R5–D-R8 as recommended.

---

## 1. What exists today

| Piece | Where | What it gives the report |
|---|---|---|
| Excel export, one builder per module | `utils/export.py` (≈3,100 lines) | The complete numbers. Builders read a `state` snapshot and never touch `st.session_state`. This is the pattern to copy. |
| Deferred download | `utils/ui_shell.render_export_section` | Builds on click, on a worker thread with no script context; inputs are snapshotted in the script thread. The report download works the same way. |
| Chart images | `utils/ui_shell.render_chart` + `utils/plot_theme.export_figure` | One PNG or SVG per chart, made with kaleido, at Word or PowerPoint size. The user goes back to each step and saves each chart separately. **This is the pain point.** |
| Print colours | `plot_theme._to_print_colours` / `export_layout` | Turns a figure built under the dark theme back into print colours without changing semantic colour. The report reuses it as-is. |
| "How to report" paragraph + references | `utils/reporting.how_to_report(module, state)` | Ready-made methods section. No Streamlit import. |
| Provenance | `core/provenance.environment_rows`, `<prefix>_source_files` | Version, git commit, package versions, file name and SHA-256, sheet, rows × columns. |
| p-value convention | `core.config.format_pvalue` | The report's tables use the same rule (4 dp, `< 0.0001`, `—`). |
| Plotters | `utils/plotting.py` (44 functions) + `plot_*` in `modules/*/ui.py` | **All pure**: no `st.session_state` or `st.context` inside them (checked). The report can call them from the download thread. |

**What makes this harder than it looks.**

1. **Figures are built inline in step code**, mixed with widget reads. For example, DA's spider is built at `modules/descriptive/workflow.py:577` from `selected_attrs` (a multiselect), `sig_attrs` and the scale. There is no "build the DA spider from state" function, so the report cannot call one. Copying those blocks into a report builder is how the report would drift from the screen.
2. **Some results are never stored.** PCA, CVA and CA are recomputed in the step through cached `stats/` calls (e.g. `modules/cata/ui.py:2091`; the CATA export already repeats it at `:2854`). The report has to call the same cached functions with the same parameters, which are persisted widgets.
3. **Many views depend on display choices** (spider attributes, bar-chart attribute, contrast reference, PrefMap map settings, Fusion component count). The report needs a rule for each one: the last value shown, the run record, or "show all, with an in-report switch".
4. **Streamlit themes the charts on screen, and the report will not have that theme (affects C-1).** `render_chart` calls `st.plotly_chart` with the default `theme="streamlit"`, and no FreeSense figure sets a Plotly `template`. Streamlit's frontend merges its own template *under* each figure, supplying whatever the figure leaves unset: background, grid and zero lines, axis lines, hover-label style, default colourway. Only 25 of the 59 plotting functions even set `plot_bgcolor`. In a standalone HTML file Plotly's default `plotly` template fills those gaps instead (grey `#E5ECF6` plot area, white grid), so **an unchanged figure would not look the same**. The fix is a Python template that reproduces Streamlit's, applied at report time under the figure: the same mechanism Streamlit uses, so the figure's own settings still win (§3.3). Streamlit's template lives in its frontend JavaScript, not in Python, so the values have to be copied from the pinned 1.64 source and checked side by side (Phase 1, step 0). *Probably also true of today's Word/PowerPoint images:* `export_layout` sets white backgrounds but no template, so kaleido renders the rest with Plotly's defaults. I have not rendered one to confirm.
5. **Payload size.** `plotly.min.js` 5.24.1 is 4.56 MB. Embedding it once is fine. Embedding one figure per attribute × view for a 30-attribute DA could add several MB more.

---

## 2. Design principles

0. **Same figure as on screen (C-1).** The report embeds the figure the step draws, as the step draws it. Report code never edits a figure's traces, layout, colours, fonts or size. The only thing added is the Streamlit-equivalent template underneath (§3.3).
1. **Visual first, statistics one click away.** Each section is: a takeaway title, then the figure, then a one-line method caption, then a collapsed `<details>` "Statistics" holding the table that backs the figure. The reader should never have to open the Excel file to check a star.
2. **One source per figure.** The report and the step call the **same** figure function (§3.2). A figure exists in one place, or the two will diverge. This matters more than anything else in the plan.
3. **Same numbers as the screen and the workbook.** The report reads the result frames that the Excel builder reads. It computes no statistic of its own (layer rule). Recomputing PCA, CVA or CA through the cached `stats/` call with recorded parameters is allowed; a new statistic is not.
4. **The house rules carry over unchanged.** ★ ⇔ full colour ⇔ the interval excludes 0 on contrast rows; colour-blind palette; no red against green; sentence-case bold chart titles; p-value convention; segments described, never tested (STAT-01, D-07); PrefMap's beta note.
5. **One self-contained offline file.** No CDN. The data statement says data never leaves the machine (`server.address = "localhost"`), and a report that pulls plotly.js from a CDN breaks that promise on opening and fails on an offline laptop. The report also has to open in an email client's "save and open" flow.
6. **Aggregates by default.** No raw data, consumer IDs or assessor IDs unless the user opts in (§5, Data minimisation). A report gets forwarded far more widely than a workbook.
7. **Takeaway titles state only what a test decided.** "Sample B is higher than Control on 4 of 15 attributes (Dunnett, α = 0.05)" comes from `summary_counts`. "B is sweeter" with no test behind it is not allowed. Every generated sentence comes from one function per module, in the style of `utils/reporting.py`, and is tested against the frame.

---

## 3. Architecture

### 3.1 Layout

```
utils/html_report.py          # assembly only: Section/Figure/Table dataclasses → one HTML string.
                              # No Streamlit import. Escaping, template, plotly.js inlining, TOC,
                              # print CSS, provenance header, methods footer.
utils/report_template.html    # Jinja2 template with autoescape on (or string.Template, see D-R5)
modules/<m>/figures.py        # NEW: pure figure builders `<view>_figure(state, **choices) -> go.Figure`
                              # called by BOTH the step and the report. Extracted from workflow/ui.
modules/<m>/report.py         # NEW: `report_sections(state, options) -> list[Section]` per module.
                              # No Streamlit import (test it like utils/reporting.py).
utils/ui_shell.render_report_section(build_html, module)   # second download button, beside Excel
```

`figures.py` is per module, not added to `utils/plotting.py`. The plotters stay generic; the new functions hold the module glue that sits inline in the steps today (which frame, which attributes, which colour map, which sort order).

### 3.2 Extract figure builders first

This is the refactor that makes everything else safe, and it is worth doing even if the report never ships: it shrinks `workflow.py`, and AppTests can pin figures directly.

```python
# modules/descriptive/figures.py
def spider_figure(state, attributes=None) -> go.Figure:
    """DA product profile. `attributes=None` = the step's default pool."""
    ...
# step:   fig = da_figs.spider_figure(st.session_state, attributes=selected_attrs)
# report: fig = da_figs.spider_figure(snapshot, attributes=options.attributes)
```

**The extraction is move-only.** The glue code moves from `workflow.py` / `ui.py` into `figures.py` verbatim. The plotters in `utils/plotting.py` are not touched. Before the first extraction, a golden test is taken **on `main`**: `fig.to_dict()` for every chart on every bundled dataset, built through the step with its default views and frozen as JSON. After each extraction the step must produce the identical dict. A figure that changes shape fails the test, which is how C-1 is enforced during the refactor, not by review.

The rule is: **a figure function reads only result frames, run records and persisted widget values, all passed in through `state`**, and the caller passes display choices as arguments. AppTest: for each module, the figure on screen equals the figure the report builds from the same snapshot (compare `fig.to_dict()` after `export_layout`).

### 3.3 Building the HTML

- `plotly.io.to_html(fig, full_html=False, include_plotlyjs=False, config=…)` per figure, with **one** inlined `<script>` of `plotly.min.js` in the `<head>`. Plotly escapes `</script>` and `<` inside the figure JSON as `<…` (checked on 5.24.1 with a product named `</script><img onerror=…>`), so figure data cannot break out of the script tag.
- **Figures go in unchanged (C-1).** No `_to_print_colours`, no `export_layout`, no resize. Built on the download thread, the theme-aware neutrals fall back to their light values (`plot_theme._is_dark_theme` is guarded and returns False without a script context; Phase 1 step 0 checks this on a worker thread). That is exactly what a light-theme user sees on screen.
- **The Streamlit-equivalent template** (`utils/report_theme.py::STREAMLIT_LIGHT`, a `go.layout.Template`) is set as `layout.template` on a *copy* of each figure at embed time, and is the only thing the report adds. A template only fills what the figure leaves unset, as on screen. Its values come from Streamlit 1.64's frontend theme together with this app's `.streamlit/config.toml` light theme (font, text and background colours). A Streamlit upgrade can change them, so the pinned version is recorded beside the values.
- **Sizing follows `render_chart`.** A figure drawn `width="stretch"` fills the report's content column, as it fills the main column on screen. A `width="content"` figure (square biplots) keeps its own width. Heights are the figure's own. So each section records the `width=` its step passes. `app.py` uses `layout="wide"`, so on screen a stretch figure already follows the window width; in the report it follows the reader's window the same way (`responsive: true`), with a maximum content width near a typical wide-layout main column so a figure is not stretched further than it ever is in the app.
- The modebar's camera button exports SVG or PNG **in the browser** (`toImageButtonOptions`), with no kaleido needed. That makes the report a partial answer to the kaleido pin risk (IO-11, REL-09): readers get vector images with no server-side renderer.
- Tables are plain HTML generated from the result frames, with the p-value convention applied in Python (`format_pvalue`). The numeric value goes in a `data-sort` attribute so an optional ~30-line vanilla-JS sort orders p-values as numbers. That JS is the only script besides plotly.js.
- `@media print` CSS: `<details>` print open, figures avoid page breaks, the TOC is hidden. "Print to PDF" from the browser then gives a usable static PDF for free.
- Light theme only in v1. A dark theme would need a second colour set for every figure and adds nothing to a document people share.

### 3.4 Interactivity: what is worth having

| Interaction | How | Verdict |
|---|---|---|
| Hover for exact values, legend toggle, zoom | Plotly built-in | Yes, free |
| Attribute switch for bar-CLD charts (DA, RATA, Liking clusters, CATA citation bars) | One figure per attribute, each built by the step's own figure function, pre-rendered as hidden `<div>`s, with a `<select>` above them and a few lines of JS to show one | Yes, but **not** with Plotly `updatemenus`: that would merge traces and add buttons inside the figure, which breaks C-1. Each attribute's figure is exactly what the step draws for that attribute. Cap the number of attributes (D-R3). |
| Contrast reference switch | Would need the contrast for every reference: k − 1 `compute_contrast` calls with QMC Dunnett at ≈3.5 s each on empty-cell designs | **No in v1.** The report shows the reference and comparison products the user viewed last (D-R2), as the Excel sheet does (D-C19). |
| Product highlight across all figures | Custom JS across plots | No. Too much JS for the value it adds. |
| Sortable tables | ~30 lines of JS | Yes |
| Search or filter | — | No |

### 3.5 Recording "last shown" (D-R2)

The display choices are persisted widgets on other steps, and the project's convention forbids reading those by bracket access from elsewhere: a widget on a step that is not rendered may hold a value it never drew with. So the report does not read the widgets. Each step **records what it drew** in one storage key per module, as PrefMap already does with `prefmap_map_settings`:

```python
# in the step, right after the figure is built
record_view(st.session_state, 'da', 'spider', attributes=selected_attrs)
record_view(st.session_state, 'da', 'bar_cld', attribute=selected_bar_attr, sort=_sort)
# → st.session_state['da_report_views'] = {'spider': {...}, 'bar_cld': {...}}
```

- `<prefix>_report_views` is a storage key: listed in `MODULE_STATE_KEYS`, so it is cleared with the results on a reset or a new upload, and never reused as a widget key.
- The report calls `figures.<view>_figure(snapshot, **views.get(view, {}))`. A missing entry means the step was never opened, and the figure function's own defaults apply. Those are the same defaults the step uses on first render, because both call the same function (§3.2).
- A recorded value that no longer exists (an attribute dropped by a re-run) cannot occur, because the record is cleared with the results. The figure function still drops unknown names defensively.
- The contrast already records its reference (`<prefix>_contrast_ref_last`, and the Excel sheet holds the reference viewed last). The comparison set, filter, order and standardise toggle join that record.

### 3.6 Designed for later adjustment (C-2)

| To change… | Edit only… |
|---|---|
| How a chart looks (on screen **and** in the report) | its function in `modules/<m>/figures.py`, or the plotter in `utils/plotting.py`. There is one copy, so both follow. |
| Which sections a module's report has, their order, titles, default on/off | the `SECTIONS` list at the top of `modules/<m>/report.py`: one `SectionSpec(id, title, figure=…, table=…, caption=…, takeaway=…, width=…, default_on=…)` per section. Adding a section is one entry. The export step's stated section list is generated from it, so the end-to-end test follows automatically. |
| Captions and takeaway sentences | the named functions in `modules/<m>/report.py` that `SectionSpec` points to, one per section, pure and unit-tested |
| Page styling (fonts, spacing, card look, colours of the page itself) | the CSS custom properties (`--fs-*`) at the top of `utils/report_template.html`. The template holds markup and loops, no logic. |
| How embedded charts are themed | `utils/report_theme.py` (the Streamlit-equivalent template), one dict |
| A report-only exception for one chart (if ever unavoidable) | `REPORT_FIGURE_OVERRIDES` in `modules/<m>/report.py`: an explicit, empty-by-default mapping from section id to a layout patch, applied in one place and listed in the report's settings block. Anything there is a deliberate, visible deviation from C-1, never a scattered `update_layout`. |
| Table columns and labels | the section's `table=` function, which returns a frame plus labels; formatting rules (p-values, percentages, decimals) come from the shared helpers |

Nothing in `utils/html_report.py` knows about a specific module, so adding Fusion and PrefMap in Phase 4 is two new `report.py` files and no change to the assembly code.

---

## 4. Content per module

The report follows the sidebar's step order, so a reader who knows the app finds the same story. Each module opens with an **at-a-glance** block of 3–5 metric cards and the headline figure, then the sections. "Stats" means the table in the section's `<details>`.

| Module | At a glance | Sections (figure → stats) |
|---|---|---|
| **DA** | products × attributes × assessors; N attributes ★ product effect; panel verdict | Product discrimination: driver scatter → ANOVA table. Profiles: spider + bar-CLD with attribute switch → Results_Table (mean ± SD, letters). Contrast: contrast bars + spider + summary cards → contrast table. Attribute overview: correlation heatmap / dendrogram → dropped attributes. Mapping: PCA biplot, CVA biplot → explained variance, loadings. Panel performance: discrimination, repeatability, agreement heatmaps, RV bars → the four performance tables. Diagnostics: **left out by default** (an analyst's view, not a reader's). |
| **RATA** | as DA plus a ticking rate | Attribute usage: ticking heatmap → Cochran's Q. Discrimination: driver scatter → LMM LRT table. Profiles, contrast, mapping: as DA. Panel stability → table. Diagnostics left out by default. |
| **CATA** | consumers, products, attributes kept after the citation filter | Frequency heatmap → Cochran's Q. Citation bars with letters / grouped bars → McNemar letters. Contrast. CA biplot with ellipses + scree → inertia table. Penalty quadrant + mean-drop bars → penalty table + the independence caveat (verbatim, as in Methods_Notes). |
| **Liking** | consumers, products, top product by LS mean, acceptance | Hedonic overview: bar-CLD, score distribution, love/hate, acceptance threshold → LMM, LS means, letters. Demographics: per-variable bars → association tests. Contrast (difference + verdict cards). Segmentation: profiles small multiples, heatmap → `cluster_separation` **descriptive only, no p-value or star**. JAR: distribution grid, weighted penalty → penalty table. Preference map biplot → loadings. |
| **Fusion** | X/Y blocks, components, Q², permutation p | PCA overlay biplot. PLS biplot, VIP bars, coefficients, observed vs predicted → model-quality table, VIP table, `fusion_pls_config` (the run record, never the pending widgets). |
| **PrefMap** (beta note at the top) | products, consumers, model mix | External preference map overlay using `prefmap_map_settings` (the settings the map was actually drawn with) → consumer model table, drivers. |

**Always present:** title block (module, dataset name, date, FreeSense version); the "How to report this analysis" paragraph, references and software citation (`how_to_report`); run parameters and provenance (`build_run_parameters_sheet`'s rows, rendered as a two-column table); disclaimer.

**Section list stated on the page.** Following the AppTest convention for sheet lists, the export step says "Your report will contain: …" in a parseable form, and the end-to-end test checks it against the `<section>` ids in the generated HTML.

---

## 5. Export-step UI

On each module's **Results & export** step, below the Excel button:

```
Interactive report (HTML)
  Sections        [pills: Profiles ✓  Contrast ✓  Mapping ✓  Panel ✓  Diagnostics ☐]
  Include assessor / consumer IDs and raw data   [toggle, off]
  Report settings  (caption) Charts use the views you last saw on each step: spider ★ attributes, bar chart "Sweetness", contrast vs "Control"…
  [ Download interactive report ]        (primary, deferred, on_click="ignore")
  File: FreeSense_DA_<dataset>_InteractiveReport_<stamp>.html · about 6 MB
```

- Widgets are persisted (`persist_state="session"`, `<prefix>_report_*` keys). They are display choices, so they do **not** trigger `reset_analysis_state`.
- There is no attribute or view control here (D-R2): to change what a chart shows, go back to its step. The caption names the recorded views so the user sees what they will get before downloading.
- Inputs are snapshotted in the script thread (`dict(st.session_state)` plus the options) and bound as lambda defaults, exactly as in `render_export_section`.
- Sections whose results do not exist (contrast not run, no clusters) are left out and listed in a caption ("Not included: Contrast, because the step was not run").
- The step's banner text and caption change: they currently say charts must be saved one by one from their steps.

### Data minimisation

Decided (D-R4): off by default. Off means no raw data tables, and every assessor and consumer ID (CVA assessor overlay, panel-performance tables and heatmaps, assessor profiles, segmentation, preference-map hover, demographics) is replaced by a stable pseudonym, with a line in the report saying so. One mapping per report, built from the sorted IDs in the snapshot, is applied to the frames **before** any figure or table is built, so no figure builder needs to know about it. The cost: a panel leader who wants to name assessors in the panel section has to turn the toggle on, and the export step says so beside the toggle.

---

## 6. Decisions

Decided rows say **Decided (owner, 2026-10-12)**. The others are proposals that stand unless the owner objects.

| ID | Question | Decision / recommendation |
|---|---|---|
| D-R1 | Format: one self-contained HTML (plotly.js inlined, ~5 MB+) or a small file loading plotly.js from a CDN? **Decided (owner, 2026-10-12): self-contained.** plotly.js is inlined once; no CDN, no network request on opening. |
| D-R2 | Which display choice does a figure use: the last one shown on screen, or a report default (all attributes, alphabetical order)? | **Decided (owner, 2026-10-12): last shown.** Every figure is drawn with the display choices the user last saw on its step: spider attributes, bar-CLD attribute and sort order, contrast reference, comparison products, filter, order and standardise toggle, PrefMap map settings, Fusion components. How this is recorded: §3.5. A step the user never opened uses the step's own first-render default. The report lists the settings it used in a "Report settings" block. |
| D-R3 | Cap on attributes in switchable figures? | *Revised for D-R2:* the bar-CLD chart **opens on the last-shown attribute and sort order**, and the in-report switch offers the other attributes (all, or ★ only when there are more than 40). Spider: the last-shown attribute set. If the owner reads "last shown" strictly (no switch), drop the switch; it is Phase 3, so nothing earlier depends on it. |
| D-R4 | Assessor and consumer IDs by default? | **Decided (owner, 2026-10-12): removed by default, assessors and consumers alike, panel sections included.** A toggle on the export step puts them back. With it off, IDs are replaced by stable pseudonyms (`A1…An` assessors, `C1…Cn` consumers) assigned once per report, in sorted order, so one person has the same pseudonym in every section, and the report says so. |
| D-R5 | Template engine: Jinja2 (autoescape; already installed as 3.1.6 through Streamlit/Altair) or `string.Template` + `html.escape`? | **Jinja2, added explicitly to `requirements.txt`** and the locks. Autoescape by default is the safer SEC-07 posture; relying on a transitive dependency is not. |
| D-R6 | Include diagnostics (residuals, QQ) and Fusion's iteration history? | Off by default, available as a section pill. |
| D-R7 | Takeaway titles: generated, or plain figure titles only? | Generated, from one tested function per module, limited to test decisions and counts (principle 7). Fall back to the plain title when no test applies. |
| D-R8 | Does the HTML report replace the per-chart Word/PowerPoint export? | **No.** Those make images sized for print; the report is for reading on screen. Keep both. |
| D-R9 | Scope of v1: all six modules, or DA + RATA + CATA + Liking first, with Fusion and PrefMap (beta) later? | **Decided (owner, 2026-10-12): DA, RATA, CATA and Liking first;** Fusion and PrefMap in Phase 4. |

---

## 7. Phased plan

**Phase 0 — decisions (owner).** §6. Agree the per-module section list (§4).

**Phase 1 — infrastructure + DA end to end.** DA first: it is the richest and best validated module, and it has the contrast chart that contrast-fix named as the report's main figure.
0. **Fidelity spike, before anything else (C-1).** Write `STREAMLIT_LIGHT` from the 1.64 frontend source. Embed three demanding DA figures (spider, bar-CLD with letters and footnote, CVA biplot with ellipses) in a bare HTML page, built on a worker thread. Compare each with a screenshot of the same chart in the app on the light theme. Go on only when they match. If some property cannot be matched, bring it to the owner instead of adjusting the figure. While at it, render one kaleido export to see whether the Word/PowerPoint images have the same template gap (§1, item 4); if so, that is a separate fix for the owner to schedule.
1. Golden figure snapshots on `main` (§3.2), committed before any extraction.
2. `utils/html_report.py` + template: sections, figure embedding (one plotly.js), tables with the p-value convention, provenance header, methods footer, print CSS, TOC.
3. `modules/descriptive/figures.py`: extract the spider, bar-CLD, driver scatter, heatmaps, PCA/CVA, panel figures and the contrast figures from `workflow.py`. Rewire the step to call them; move-only, held by the golden snapshots and the existing AppTests.
4. `record_view` + `da_report_views` (§3.5): each DA step records what it drew.
5. ID pseudonymisation (D-R4) in `utils/html_report.py`, applied to the snapshot's frames before any figure is built. It belongs in Phase 1 because the default is on, and retrofitting it after figures exist is where IDs leak.
6. `modules/descriptive/report.py` (with its `SECTIONS` list) + `render_report_section` on DA Step 8.
7. Tests (§8).

### 7.1 Phase 1 report (2026-10-12)

**Done. Uncommitted.** Ruff gate passes; the full suite (as CI, without coverage — `pytest-cov` is not installed in the local venv): **994 passed, 0 failed**. Coverage floors not run locally.

**Step 0, fidelity spike: passed, by measurement.** Findings that changed the design:
- Streamlit's chart theme is not guesswork to reproduce. Importing Streamlit registers a `"streamlit"` Plotly template with placeholder colours (`#000001`…) that every figure built in the app carries; the frontend replaces the placeholders, deep-merges a fixed layout into `layout.template.layout` and bolds the title. `utils/report_theme.py` ports those three steps from the 1.64.0 frontend (and reads the light theme from `.streamlit/config.toml`).
- **Streamlit 1.64 draws with plotly.js 4.0.0**, not the 2.35.2 bundled with the Python `plotly` 5.24. The report embeds 4.0.0 (`assets/vendor/plotly-4.0.0.min.js`, MIT, sha256 `14461f3b…cd7ca`, from the `plotly.js-dist-min` npm package). `tests/test_report_theme.py` fails when the installed Streamlit or its bundled plotly.js moves.
- The app's font is Source Sans (shipped inside Streamlit, OFL); the report embeds it (170 kB).
- **Result:** the 8 DA charts of a sensochoc run (driver scatter, spider, CLD bars, heatmap, dendrogram, contrast, PCA, CVA), captured as the app sends them and drawn by Streamlit and by the report page in headless Edge, are **pixel-identical** (0 differing pixels each). A naive embed (Python plotly's own plotly.js, no theme) differs on 28,903 of 422,400 pixels of the first chart. Harness: `working_notes/repro/interactive_report/` (`capture_figures.py` → `spike_html.py` → `reference_app.py` + `shoot.py`); re-run it after a Streamlit upgrade.
- **For the owner (not fixed, separate scope):** the Word/PowerPoint image exports have the same template gap. `export_layout` sets white backgrounds but no template, so kaleido draws with Plotly's default template: centred, larger title, vertical grid lines, heavier axis lines. Some of that is the deliberate print styling; the template part is not. Candidate for `docs/open-items.md` if the owner agrees.

| Item | Result |
|---|---|
| 1. Golden snapshots | `tests/figure_golden.py`, `tests/test_figure_golden.py`, `scripts/freeze_figure_golden.py`. 32 DA charts on sensochoc (default views, every gated panel, plus varimax PCA, CVA overlay + tolerance ellipses, bar chart on another attribute and order), frozen **before** the extraction. Numbers compared to 1e-9 relative. ~9 s. |
| 2. Assembly | `utils/html_report.py` (content model: `Report` / `Section` / `Chart` / `Table`), `utils/report_template.html` (Jinja2, autoescape; page styling only in `--fs-*` tokens), `utils/report_theme.py`. Jinja2 declared in `requirements.txt`; the six locks gained only a `-r requirements.txt` line (same 3.1.6 pin). |
| 3. Extraction | `modules/descriptive/figures.py`: every DA chart, `(state, **view) -> figure`, no Streamlit. The steps call it; move-only, **golden test identical after the move**. The contrast difference chart moved to `utils.contrast_view.difference_figure` (shared by the four modules). The ANOVA table labels moved to `da_ui.anova_table_labels` (step and report). |
| 4. Last shown (D-R2) | `utils/report_views.record_view` writes `<prefix>_report_views` (storage key, in `MODULE_STATE_KEYS` for DA, RATA, Liking, CATA). Every DA chart site records its view; the shared contrast renderer records reference, comparisons, attributes, order and standardise for all four modules. |
| 5. Pseudonyms (D-R4) | `utils/pseudonymise.py`: one mapping per report, in the IDs' own sort order and zero-padded (`A01`…), applied to every `<prefix>_*` frame before anything is built, so groupbys and seeded resamples see the same order. |
| 6. DA report + UI | `modules/descriptive/report.py`: `SECTIONS` (discrimination, profiles, contrast, correlations, mapping, panel; diagnostics off by default), takeaways from test decisions only, tables from the result frames, methods paragraph and Run_Parameters rows (`utils.export.run_parameters_rows`, split out of the sheet writer so both show the same rows). `utils.ui_shell.render_report_section`: section pills, "Include assessor IDs" toggle (off), the stated section list, a deferred download. Step 8 banner and caption updated. |
| 7. Tests | `test_report_theme.py` (version guards, theme port), `test_html_report.py` (p-value convention, injection via an HTML parser, chart JSON cannot close its script, nothing fetched), `test_pseudonymise.py`, `test_apptest_da_report.py` (stated sections = file sections; each report chart equals the chart the step drew; last-shown views; distinctive assessor IDs absent by default, present with the toggle). `capture_exports` now also builds `*_report_download` on a worker thread. |

**Measured:** sensochoc report 4.9 MB, built in about 1 s.

**Watch:** a persisted section-pills selection keeps its choices when a section becomes available later (Streamlit does not re-apply `default=`); "Contrast analysis" is in the default, so this only matters if a user removed it. The export step lists sections it cannot include ("open the contrast step first").

#### Owner follow-up after testing DA (2026-10-12)

Four requests, all done without changing a chart:
1. **Bar charts for every attribute** (product profiles): a `ChartGroup` — one chart per attribute, each built by `figures.bar_cld` exactly as the step draws it, a selector above them (plus "All", listing them one under another). It opens on the attribute and sort order last shown (D-R2). Above 40 attributes it keeps the ★ attributes (D-R3).
2. **Assessor profile plot**: the same selector. Applied too, for consistency, to the other per-attribute charts the step shows one at a time: repeatability, agreement and (diagnostics) residuals.
3. **Contrast overview**: bordered cards, one per comparison sample — higher / lower / no evidence (/ not tested) — the app's summary cards (D-C21), instead of a sentence.
4. **Sortable tables**: click a header for ascending, again for descending; numbers by value (`data-sort`, so p-values sort as numbers), text alphabetically, `—` last. About 30 lines of vanilla JS in the template, no library.

Charts in a hidden group member are drawn only when shown (a hidden chart would be laid out at zero width). Checked in headless Edge (`working_notes/repro/interactive_report/check_interactions.py`): a picked attribute draws at full width, "All" draws all 14, both sort directions work. Sensochoc report: 5.9 MB (was 4.9), built in about 2 s.

### 7.2 Phase 2 report (2026-10-12)

**Done. Uncommitted.** Ruff gate passes; full suite as CI (without coverage): **1006 passed, 0 failed**.

| Item | Result |
|---|---|
| Golden snapshots, frozen before any move | RATA sensochoc 12 charts (+ bar on another attribute, varimax PCA), CATA bread 10, Liking hedochoc 23 (demographics, both segmentations, the map with clusters + KDE), Liking JAR 20. All identical after the moves. |
| Extraction | `modules/rata/figures.py`, `modules/cata/figures.py`, `modules/liking/figures.py`. Liking's demographics panel, JAR frames and preference map moved as blocks: the functions return the charts plus what the step shows beside them (frames, p-values, notes such as "no segments yet"), so every message is still rendered by the step. The Liking chart constants moved with the builders. CATA's figures import the step module lazily (it holds two data helpers), so there is no import cycle. |
| Shared report pieces | `utils/report_builder.py`: section spec, per-attribute chart groups with the 40-attribute cap, the contrast section (cards, difference chart, profile, table — single-attribute cards for Liking), the assembly. DA's report moved onto it unchanged. |
| Reports | RATA: attribute usage, discrimination, profiles (bars for every attribute), contrast, mapping, diagnostics (off). CATA: frequency, discrimination (bars per significant attribute), profiles, contrast, CA (the step's stored map, or the step's defaults if never shown), penalty (with the independence caveat). Liking: hedonic overview, demographics, contrast, segmentation (descriptive only: no p, no star — STAT-01), JAR penalty, preference map. |
| Pseudonyms | Extended for Liking: Series indexes, wide consumer × product tables (IDs as column labels), nested result dicts, and IDs found only in the demographics file — the mapping is built from every ID in the module's state, sorted, so the analysis order is unchanged. |
| Tests | `tests/test_apptest_reports.py`: one case per module (RATA, CATA, Liking, Liking JAR) with distinctive renamed IDs — stated sections equal the file's; every report chart equals the chart its step drew; no ID in the default file; IDs present with the toggle where the sections show people at all (Liking yes; RATA and CATA show no assessor/consumer, which is correct). The four new `figures.py` files are in the chart-title sentence-case scan. |
| Tidying | Imports and locals the moves left unused in the three step files removed (plus the few that were already unused in those files). |

**Measured:** reports of 4.7–5.2 MB for the bundled datasets.

**Layout note (not C-1):** charts that sit in narrow columns on screen — Liking's demographic main-effect bars (30 % of the row), CATA's scree plot beside the CA map — are full width in the report. The figures are identical; only the column differs.

### 7.3 Phase 3 report (2026-10-12)

**Audit of Phases 1–2 first.** The full suite passed before any change. What the audit found, all fixed here:

| Finding | Fix |
|---|---|
| Liking's takeaway read **"p p = 0.0816"**: `format_pvalue(p, inline=True)` already prefixes `p`. | Takeaway rewritten; a test pins one `p`. |
| When the Liking LMM cannot be fitted its p is NaN, and the takeaway said "show no evidence of a difference" for a test that never ran. | No takeaway (and no verdict card) without a p-value. |
| The ID toggle's help said "A01, A02, …" in CATA and Liking, whose codes are `C01…`. | `render_report_section(id_letter=…)`. |
| D-R2 promised "a Report settings block listing the settings it used", and §5 a caption naming the recorded views. Neither existed. | Done (below). |
| The JAR table dumped the raw 20-column frame, including `actionable_text` with its unfilled `{too_low}` placeholder. CATA's penalty table dumped 22 columns, including `unmatched_*` bookkeeping. | Both are curated to the step's columns and wording (the step's `_substitute_jar_keywords` and quadrant labels). |
| §8 hover-text injection: not done. | **Checked and not needed.** `working_notes/repro/interactive_report/check_hover_injection.py` puts `<img onerror>`, `<svg onload>`, `<b onmouseover>` and a `javascript:` link into a chart's title, axis title, legend, annotation, tick labels, bar text and hover template, opens the report in headless Edge and hovers the points. plotly.js 4.0 shows unknown tags as text, ran no handler, and left no `img`/`on*`/`javascript:` in the DOM. Escaping in the figure builders would also change the on-screen charts (C-1), so none is added. Re-run the script after a plotly.js upgrade. |
| §8 "every bundled dataset: sections match the stated list, one number matches": only one dataset per module was checked. | `test_apptest_bundled_datasets._assert_report` on every DA, RATA, CATA and Liking dataset: section ids = the stated list, and the report's tables carry the result frames' F / LRT / Q / LS-mean values. With the existing screen = `stats/` checks, that closes the chain. |
| §8 contrast rule on the report's JSON. | Covered transitively: each report chart equals the chart the step drew (C-1 tests), and `test_contrast_consistency.py` checks the drawn figure. |

**Phase 3 items.**

| Item | Result |
|---|---|
| Attribute switch | Already delivered in the Phase 1 follow-up (`ChartGroup`), for every per-attribute chart in all four modules. |
| Sortable tables | Already delivered in the Phase 1 follow-up. |
| Takeaway titles (D-R7) | One named function per section, `takeaway_<section id>(state)` in each `report.py`, pointed to by `SectionSpec(takeaway=…)` (C-2: one place, unit-tested in `tests/test_report_takeaways.py`). Each states test decisions or counts of them, then the basis as a second sentence ("Test: Cochran's Q, α = 0.05."; "Post-hoc: …"; "Adjustment: …" for the contrast). New: DA/RATA profiles (pairs the letters separate, read from the CLD), DA panel (assessors discriminating, from `stats.panel_performance.summarise_panel_performance`, the call Step 6 and the export make), CATA discrimination (McNemar letters) and penalty (sign of the mean drop, the step's own gate), every contrast (higher / lower per sample, or a count above three samples), Liking demographics (exploratory, uncorrected, said so) and JAR (split by the sign of the penalty: the test is two-sided). Mapping, correlations, CA, preference map and diagnostics have no test behind them and keep their plain title. Segmentation keeps its descriptive sentence (STAT-01). |
| At-a-glance cards | `Glance(label, value, detail)`. DA adds "Assessors discriminating N of M" (the panel verdict of §4); RATA states intensity and ticking decisions with their tests; CATA the citation filter; Liking the LMM verdict with its p, the highest LS mean and the most accepted product at the threshold last shown (`stats.liking.acceptance_share`, the chart's own call). §4's "ticking rate" for RATA is left out: no single overall rate is shown anywhere in the app, and a mean of rates would be a new number in the report layer. The §4 "headline figure" in the glance block is not added: it would repeat a section's chart and add its weight to the file. |
| Chart views (D-R2) | `VIEWS` in each `report.py` (`ViewSpec(label, section, keys)`) says which recorded choices to state. The report's "Report settings" table lists them ("Chart view: Bar chart, opens on — attribute: Sweet; order: by mean"), or "step not opened: its default view". The export step shows the same rows in a "Chart views in the report" expander, for the chosen sections only. |
| File-size check | The report must be built on the worker thread (on the script thread a dark-theme user's charts would get dark neutrals, breaking C-1), so its size is only known after a build. The build records its per-section sizes in `<prefix>_report_sizes` (storage key, in `MODULE_STATE_KEYS`); from the next run the step states "about N MB" for the chosen sections (exact for sections built before, "or more" otherwise) and warns above 15 MB (`report_builder.LARGE_REPORT_BYTES`), naming the two largest sections. Before the first build it says "about 5 MB or more". |

**Measured.** Bundled datasets: 4.7–5.9 MB. Synthetic DA, 40 attributes × 12 products × 30 assessors × 3 sessions: 7.4 MB with the default sections (3 s), 11.1 MB with diagnostics (6 s); diagnostics' residual plots are the heaviest charts (≈ 90 kB each). 15 MB needs a larger panel with diagnostics on, so the warning should be rare.

**Owner follow-up (2026-10-12): the omnibus caution, done.** On hedochoc the LMM finds no product effect (p = 0.0816) while the BH contrast finds choc3, choc4 and choc6 liked more than choc1: the many-to-one contrast is its own family, not gated on the omnibus (D-C2). When the overall test is not significant and a shown comparison is, one sentence (`utils.reporting.liking_omnibus_note`, the only copy) says so and asks the reader to treat such a difference as tentative. It is shown on the Liking contrast step under the summary cards (`ContrastStepSpec.note`, an `st.warning`), at the top of the report's contrast notes, and in row 2 of the workbook's Contrast sheet. `test_liking_examples` checks all three carry the same text on hedochoc, and none on the JAR example (overall effect present).

**CI (ubuntu, Phase 2 commit): two golden failures, fixed in the test, and a finding.** `test_charts_match_golden[liking_hedochoc]` (and, by the adjacent failure, `liking_jar`) failed on x86_64 Linux and pass on arm64 macOS. Two causes: the Liking LMM converges to estimates that differ at ~1e-6 relative between architectures, and Ward linkage on integer ratings meets exact ties (hedochoc: 115 of 221 merges tie with another) that last-bit differences break differently. The Liking goldens are now compared number for number only on the platform that froze them (`tests/figure_golden.PLATFORM_BOUND`, `FROZEN_ON = "darwin-arm64"`: the maintainer's machine and CI's macos-latest); elsewhere the chart set is checked and the test is skipped with that reason. The freeze script refuses to freeze them on another platform. The tie problem is not only a test problem: shuffling the consumer rows changes hedochoc's k = 3 AHC segments in 16 of 20 orders. Owner decision (2026-10-12): report the instability and recommend k-means for tied data. Done: every clustering result carries its order stability (20 seeded reorderings, adjusted Rand index), shown on Step 5, in the report's segmentation takeaway and in the export (CHANGELOG 1.0.0rc2, methods reference §27).

### 7.4 Phase 4 report (2026-10-13)

**Done. Uncommitted.**

| Item | Result |
|---|---|
| Golden snapshots, frozen before any move | `fusion_cocktail` (14 charts: PCA biplot and scree, model quality, per-response Q², VIP, iteration history, both PLS biplots, t–u, coefficients, observed vs predicted, three diagnostics) and `prefmap_cocktail` (6: the pre-fit map, the Step 2 map with no surface / heatmap + ideal points / contour + R² weighting + hull mask + R² filter, and the Step 3 mirror). Identical after the moves. Not reached: `fusion_coef_reg`, the coefficient chart for a model fitted without per-fold coefficients, which Step 3 never produces. |
| Extraction | `modules/fusion/figures.py` (every Fusion chart; the parsimony rule `recommended_components` moved with the charts that mark it). `modules/prefmap/figures.py`: the map is one function, `overlay`, from explicit inputs plus `prefmap_map_settings`. Step 2 passes the inputs it has just computed (they reach session state only after the map is drawn); Step 3 and the report call `overlay_from_state`. Step 3's near-copy of Step 2's map code is gone. Dead imports and locals the moves left are removed. |
| Last shown (D-R2) | Fusion records the PCA biplot (component pair, variable layer), the Step 4 PLS biplot (pair, VIP display filter), the regression tab's response and the t–u component. PrefMap needs no new record: `prefmap_map_settings` already is one, and the report lists it as "Map setting: …". |
| Reports | Fusion: exploratory map, PLS model (takeaway: the permutation test's decision, only when the test was run, with the post-selection caveat after pruning), model interpretation (coefficients and observed vs predicted per response, opening on the response last shown), diagnostics (off by default, with the iteration history: D-R6). No IDs, so no toggle. PrefMap: the preference map with the step's arrow readout, the consumer models table, loadings and cluster drivers; takeaway: counts of the per-consumer AICc decisions, named as such (a model-selection decision, not a significance test). Beta note at the top (any beta module, from `build_report`). |
| Pseudonyms (PrefMap) | Consumer IDs sit in the vectors, the PREFMAP results, the liking block's columns and (for segments taken from Liking) an index named after Liking's consumer column. The report names every one of those axes `consumer_id` before pseudonymising. Without that, the coded map silently lost its cluster centroids: 150 traces against 44; the test fails when the naming is removed. |
| Found and fixed: Streamlit theme port | `utils.report_theme` replaced any template other than Streamlit's with Streamlit's, and could not even build Streamlit's (`pio.to_json` does not take a `Template`). Neither showed up before: every DA/RATA/CATA/Liking chart already carries Streamlit's template. Fusion's scree sets `plotly_white`. Streamlit's frontend keeps a figure's own template and merges its layout into it (`Ce` in the 1.64.0 PlotlyChart chunk, read for this), so the port now does the same and adds Streamlit's template only to a figure with none or with Plotly's default. Checked by code reading and a unit test, not by the pixel harness. |
| Tests | `test_fusion_report` (permutation test on, 199 permutations) and `test_prefmap_report` (renamed consumer IDs, contour surface and ideal points; coded map equals plain map, including Liking-style segments) in `test_apptest_reports.py`; both bundled-dataset tests check the report's sections and numbers; takeaway unit tests; the template test in `test_report_theme.py`. |
| Documentation | README "The interactive report" (under Module guides), CONTRIBUTING (pinned charts, and the Liking goldens being compared only on arm64 macOS: change a Liking chart on Linux, run the golden test on a Mac before committing), CHANGELOG 1.0.0rc2, CLAUDE.md report conventions (10)–(12). |

**Measured.** Fusion cocktail 5.0 MB (0.8 s), PrefMap cocktail 4.6 MB (1.9 s, with the contour surface).

**CI after Phase 4 (2026-10-13).** `test_charts_match_golden[prefmap_cocktail]` failed on all three runners (arm64 macOS included); the Fusion goldens passed everywhere. The only differences were PrefMap's arrow colours, `rgba(180,180,180,<alpha>)` with the alpha taken from each consumer's R², differing at ~1e-16 relative: a float written into a *string*, which the comparator compared exactly while it gives numbers a 1e-9 tolerance. `tests/figure_golden.differences` now compares the decimals inside a string with the same tolerance and everything else in it exactly (`test_numbers_inside_text_get_the_numeric_tolerance`). No chart changed, and PrefMap does not need to be platform-bound. The key-set failure message now also says where each added or removed chart was drawn.

**Phase 2 — RATA, CATA, Liking.** Same three steps per module. RATA reuses most of DA's figures. Contrast figures for all four come from `utils/contrast_view.py`, so extract them there once.

**Phase 3 — interactivity and polish.** Attribute switch (pre-rendered figures, §3.4), at-a-glance cards, takeaway titles (D-R7), sortable tables, file-size check (warn above ~15 MB).

**Phase 4 — Fusion, PrefMap; documentation.** README export section, "How to report" note, CHANGELOG. The version bump policy is triggered only by `stats/` changes; this plan should need none (if it does, a statistic has leaked into the report layer).

Rough size: Phase 1 is the largest because of the figure extraction (DA's `workflow.py` builds 15 figures inline). Phases 2–4 are mostly repetition of the pattern.

---

## 8. Tests

- **End to end (extend `tests/test_apptest_bundled_datasets.py`):** for every bundled dataset, build the report with `capture_exports` / `run_deferred_download` (worker thread, no script context). Assert it parses, that the `<section>` ids match the list stated on the export step, and that one on-screen number (e.g. a contrast `p_adj` or an LS mean) appears in the report's table and matches a direct `stats/` call.
- **Same figure (C-1):** the step's figure equals `figures.<view>_figure(snapshot)` (§3.2), and the figure JSON embedded in the report equals it too, apart from `layout.template`. This is the test that stops report code from modifying a chart.
- **Golden snapshots:** every chart's `to_dict()` on every bundled dataset matches the JSON frozen on `main` before the extraction (§3.2). Regenerating the snapshots is a deliberate, reviewed act (a script, not a pytest flag), for a chart change made on purpose.
- **Contrast rule:** run `tests/test_contrast_consistency.py`'s ★ ⇔ colour ⇔ interval check on the figure JSON extracted from the report.
- **Injection (SEC-07):** a product, attribute and cluster named `</script><img src=x onerror=alert(1)>` and a Markdown image. Assert no unescaped `<img`, `<script` or `on…=` outside the template's own script tags, in table cells, titles, the TOC and **Plotly hover text**. Plotly.js renders a subset of HTML in hover labels and titles (`<b>`, `<br>`, `<a href>`), so user strings in hover and annotations must be escaped before they reach the figure. Add a helper in `figures.py` and test it. *Phase 3: measured in headless Edge — plotly.js 4.0 renders no markup or handler from a user string, so no helper (§7.3).*
- **Offline:** the HTML contains no `http(s)://` script or stylesheet source (links in the references are fine).
- **Data minimisation (D-R4):** with the toggle off, no assessor or consumer ID from the upload appears anywhere in the file, figure JSON included; the same person has the same pseudonym in every section. Use bundled datasets whose IDs are distinctive strings, plus a synthetic file with IDs like `Panelist_Jane`.
- **Last shown (D-R2):** an AppTest changes the spider attributes, the bar-CLD attribute and the contrast reference, then builds the report and asserts those choices are in the report's figures; a fresh session with steps never opened gets the first-render defaults.
- **Copy rules:** chart titles in sentence case (extend `test_plotting_labels` to the new `figures.py` files), no p-value printed as `0.0000`, ★ never `*` as the significance marker.

---

## 9. Risks

| Risk | Mitigation |
|---|---|
| The report drifts from the screen | §3.2 extraction; same-figure test |
| Charts look different outside Streamlit (C-1) | Streamlit-equivalent template, checked in the Phase 1 spike; a Streamlit upgrade re-runs that check (note it in the upgrade checklist) |
| The extraction refactor changes a chart by accident (C-1) | Move-only rule; golden `to_dict()` snapshots taken on `main` first |
| Download-thread time (PCA/CVA/CA recomputed, many figures) | Cached `stats/` calls usually hit because the user has visited the step; measure on the largest bundled dataset; a spinner is impossible on a deferred download, so keep it under ~5 s or move the build to a button that prepares the file in the script body first (as Fusion queues refits) |
| File size on large studies | ★-only cap (D-R3), one plotly.js, `to_json` without validation, size shown on the export step |
| Hover HTML injection | Escape user strings in figure builders (§8) |
| Plotly 6/7 upgrade (REL-09) changes `to_html` output | Tests parse the structure and figure JSON, not exact HTML |
| The report reads as more authoritative than it is (beta PrefMap, descriptive segments) | Beta note and the "descriptive, no test" captions are part of the section, not optional |
