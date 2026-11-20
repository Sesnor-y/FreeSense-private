# B10 Interface, accessibility and presentation

Reviewer: B10 (UI). Commit reviewed: `bcaf9f8`. Review only; no application files were changed.

## Scope and method

Checked: visual and terminology consistency across the six modules and the in-app About page; layout at common widths; theme colour contrast (light and dark); plot text colours and palettes; colour-blind safety of palettes and semantic colour scales; reliance on colour alone; text equivalents for charts; keyboard implications of the `st.html` scroll reset; branding, About page, version display, feedback route and disclaimers.

Commands and scripts (all scratch files in `.../scratchpad/agents/B10/`):

- `steprefs.py`: parses every string constant in `modules/*` with `ast`, extracts "Step N ..." references and compares them against `core.config.MODULES`.
- `terms.py`: counts terminology in UI strings per module (docstrings excluded).
- `contrast.py`: WCAG 2.x relative-luminance contrast ratios for the theme in `.streamlit/config.toml`, the plot neutrals in `utils/plot_theme.py`, and every palette in `utils/colours.py`.
- `cvd.py`, `pal.py`: CIELAB ΔE between colour pairs under simulated deuteranopia and protanopia (Machado et al. 2009 matrices, severity 1.0).
- `walk_da.py`: AppTest walk of the Descriptive module on `example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx` through all eight steps, counting rendered elements. The run completed with no exception.
- `palette_persist.py`: AppTest check of sidebar settings across the About and Methods overlays.
- `landing_order.py`: AppTest element order on the landing page.
- `disc_norep.py`: headless `compute_discrimination` plus `plot_discrimination_heatmap` on sensochoc restricted to Session 1 (a design with no replicates).
- The app was started with `env/bin/streamlit run app.py --server.port 8598 --server.headless true`. `/_stcore/health` returned `ok`. The served HTML is only the Streamlit shell (`<html lang="en">`, `<title>Streamlit</title>` until JS sets "FreeSense", plus a `<noscript>` notice). No browser was available (no chromium, firefox or playwright), so nothing was checked visually. The server was stopped afterwards.
- To confirm how the Streamlit 1.64 frontend treats the theme, I grepped the frontend bundle in `env/.../streamlit/static/static/js/`. Primary buttons use `color:e.colors.white` on `primary`. Captions use `fadedText60`, which is body text at 60% alpha. In dataframes, a Styler `background-color` does not change the cell text colour, except when the background is the literal `yellow`.

Anything described as a visual outcome below comes from code and computed ratios, not from something I saw on screen. Where that matters, the finding says so.

## Findings

### UI-01: Opening About or the methods reference silently resets the colour scheme and export format
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `utils/ui_shell.py:210-259` (`render_sidebar` returns early while an overlay is open) and `:354-418` (`_render_settings`: `st.selectbox(..., index=0, key="colour_palette_selector")` without `persist_state`; `st.session_state["global_colour_palette"] = ...` is written unconditionally from the widget value)
- Evidence: `palette_persist.py` sets the palette to "Colour-blind safe" and the format to PNG, then opens About and presses Back. Output: `before colourblind png` / `about open; selector present? False` / `after back default svg Default`. The methods overlay does the same (`after methods default`). While an overlay is open the settings widgets are not rendered, so Streamlit drops their state. On return they come back at `index=0`, and that value is copied into `global_colour_palette` and `export_format`.
- Impact: A colour-blind user who picked the safe palette loses it without any message just by reading About or the methods reference. Charts that read the palette live (liking ramps, preference surface, cluster colours) switch back to red/green. On steps 2 and later, the "Colour scheme changed, re-run analysis" warning also appears (`render_step_header`) even though the user changed nothing. Chart downloads switch back to SVG.
- Recommendation: Give both widgets `persist_state="session"`, as CLAUDE.md requires for widgets that must survive un-rendering. Alternatively, keep rendering the settings expander in the overlay sidebar. Add an AppTest for this round trip next to the one in `tests/test_apptest_shell.py`.
- Effort: S
- Dependencies: none

### UI-02: Significant rows in the Liking penalty table are near-invisible on the dark theme, and greyed rows fail contrast on light
- Severity: MEDIUM
- Confidence: VERIFIED (code path and frontend rule); rendering not observed in a browser
- Location: `modules/liking/workflow.py:84` (`FLAGGED_ROW_BG = "#ffe0e0"`), `:2878-2886` (`_style_row`: `background-color` only; untestable rows `color: #9e9e9e`)
- Evidence: The frontend applies a Styler `background-color` as `bgCell` and keeps the body text colour (`textDark`) unless the background is literally `yellow` (bundle excerpt: `let a=Zh(t,'background-color',n);a&&(r.bgCell=a),a==='yellow'&&i===void 0&&(r.textDark='#31333F')`). With the dark theme (`textColor #F1F5F9`), text on `#ffe0e0` has a contrast of **1.13:1**. Untestable rows use `#9e9e9e` on white: **2.68:1**. WCAG AA for normal text is 4.5:1. The dark theme is declared in `.streamlit/config.toml` and is chosen automatically for users whose OS is in dark mode. Other significance-shaded tables use `rgba(40,167,69,0.15-0.2)` (`modules/rata/ui.py:532,637`, `modules/cata/ui.py:1308`, `modules/descriptive/workflow.py:847`). These are translucent, so they stay legible on both themes.
- Impact: Dark-theme users of Liking Step 6 cannot read the rows the table exists to highlight: the significant penalties.
- Recommendation: Use a translucent tint such as `rgba(214,39,40,0.18)`, as the other modules do, or set a text colour together with the background. Raise the greyed text to at least `#6b6b6b` on light.
- Effort: S
- Dependencies: none

### UI-03: The brand teal fails WCAG AA contrast for text on primary buttons
- Severity: MEDIUM
- Confidence: VERIFIED (computed ratio; the frontend uses white text on `primary`)
- Location: `.streamlit/config.toml` `[theme] primaryColor = "#0D9488"`
- Evidence: `contrast.py`: white on `#0D9488` is **3.74:1**. Teal on white (links, tertiary accents) is also 3.74:1, and on the sidebar `#F8FAFC` it is 3.58:1. On the dark background it is 4.77:1. Every "Open module", "Run full analysis & continue", "Run preference map" and "Fit PREFMAP models" button is `type="primary"` with normal-weight label text of about 14 to 16 px, which needs 4.5:1. The rest of the theme passes: body text 17.9:1 (light) and 16.3:1 (dark), captions at 60% alpha 4.69:1 (light) and 6.48:1 (dark), plot text 17.4 and 16.3, muted plot lines 7.5 and 7.0. Borders are 1.23:1 (light) and 1.72:1 (dark). That is decorative and acceptable only because widgets also have other cues.
- Impact: Primary actions are harder to read for low-vision users. If an institutional customer requires WCAG AA, this fails their audit.
- Recommendation: Use `#0F766E` (teal-700): white on it is 5.47:1, and on the dark background it is 3.26:1, which meets the 3:1 bar for non-text indicators such as the radio dot and slider. If the logo's teal must stay, keep it only in the logo and use the darker shade for `primaryColor`.
- Effort: S
- Dependencies: none

### UI-04: The preference-surface guide says "green = high, red = low", but the colour-blind palette makes red mean high
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `utils/plotting.py:111-127` (`diverging_liking_ramp` returns `RdBu_r`, red = high, when the palette is `colourblind`; otherwise `RdYlGn`, red = low); `utils/ui_shell.py:892-951` (`render_prefmap_explanation_expander` hard-codes "Green regions: high predicted average liking; Red regions: low"); used at `modules/prefmap/workflow.py:1388-1390`
- Evidence: With the colour-blind palette, `modules/prefmap/workflow.py:1374` renders the caption "Red = high predicted average liking, blue = low …". A few lines further down, the expander says red is low. The same ramp flip applies to the Liking consumer heatmaps (`modules/liking/workflow.py:1051,1486,1709`), where the captions are correct but red changes meaning when the palette changes. The expander also names the model-selection criterion "AIC", while `stats/prefmap.py:128-140` uses AICc, and it describes a "Heatmap/Contour" surface style option.
- Impact: A user reading the guide can invert the surface: the high-liking region is taken for the low one. That is a wrong product-positioning conclusion drawn from a correct computation.
- Recommendation: Keep one direction across palettes. For example, low = blue or purple and high = orange or brown on both, or a sequential cividis/viridis ramp for this one-directional quantity. Generate the expander's colour sentence from `describe_liking_ramp`. Change "AIC" to "AICc".
- Effort: S
- Dependencies: UI-05

### UI-05: Semantic red/green colours ignore the colour-blind setting, and some carry meaning by colour alone
- Severity: MEDIUM
- Confidence: VERIFIED (colour values and ΔE computed); perceptual effect is simulated, not user-tested
- Location: `utils/colours.py:66-72` (`DRIVER_COLOUR_MAP`, documented as "must NOT change with the user's global palette"); used by `utils/plotting.py:525-531` (RATA frequency vs intensity driver scatter) and `:1355-1360` (DA driver classification); `modules/descriptive/ui.py:159-166` (discrimination heatmap red→yellow→green); `modules/liking/ui.py:42-46` (JAR distribution red/green); `modules/fusion/ui.py:733` (Q² heatmap red-white-green); `modules/descriptive/ui.py:41-43` plus `modules/descriptive/workflow.py:1712-1718` (per-assessor ICC and r below threshold shown only as red text)
- Evidence: `cvd.py`: "Robust Driver" `#2ca02c` against "No Discrimination" `#d62728` gives ΔE 119.8 with normal vision and **7.3 under deuteranopia**, which is close to indistinguishable. The DA heatmap's orange against light green gives ΔE 8.0 (deutan). In both scatters the class is carried by colour plus position relative to the dashed α lines. The marker symbol is the same for every class and attribute names appear only on hover. In the DA "By attribute" table, values below the ICC/r threshold differ from the others only in red text. The Styler-shaded "Yes" cells elsewhere are fine because they contain text.
- Impact: About 8% of men (deuteranopia and deuteranomaly) cannot reliably tell "robust driver" from "no discrimination", or see which assessor/attribute cells are below threshold, even after choosing the "Colour-blind safe" palette.
- Recommendation: Route semantic colours through the palette setting, or pick semantic colours that are CVD-safe by default (blue/orange/grey classes). Add a second channel: `symbol=` per class in the driver scatters, and a text flag column (for example "below 0.50") in the DA detail table.
- Effort: M
- Dependencies: none

### UI-06: The "Colour-blind safe" product palette includes a yellow that almost disappears on white, and the default palette has a deuteranopia-confusable pair
- Severity: MEDIUM
- Confidence: VERIFIED (computed)
- Location: `utils/colours.py:19-33` (`PRODUCT_PALETTES`)
- Evidence: `contrast.py`/`pal.py`: in the `colourblind` palette, colour 4 is `#F0E442` at **1.32:1** on white. WCAG 1.4.11 asks for 3:1 for graphical objects such as spider lines, markers and thin bars. Six of the eleven colours are under 3:1 on white. In the default `Bold` palette, colour 4 `#F2B701` is 1.82:1, and colours 2 and 5 (`#11a579`, `#e73f74`) have ΔE **7.1** under deuteranopia. Products are assigned colours alphabetically (`get_product_colour_map`), so any study with 5 or more products gets that pair. The `muted` (Pastel) palette is under 3:1 for all eleven colours, and the default cluster palette (`Set2`) for all eight.
- Impact: Users who choose the accessibility option lose one product's line in spider plots and profile charts. With the default palette, two products can look the same to colour-blind users when the legend is the only key.
- Recommendation: In the `colourblind` list, move `#F0E442` last or drop it. Okabe-Ito guidance itself warns against yellow for lines on white. Consider making the colour-blind palette the default. Mark the Pastel options as "for dark backgrounds or large fills".
- Effort: S
- Dependencies: none

### UI-07: The DA discrimination heatmap is empty for designs without replicates and always states α = 0.05
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `modules/descriptive/workflow.py:1233-1238` (`plot_discrimination_heatmap(disc_df, col_map)` called without `alpha`); `modules/descriptive/ui.py:145-186` (pivots `neg_log_p`; title "Colour centred at significance threshold (α={alpha})"); `stats/panel_performance.py:93-103` (the no-replicate path sets `neg_log_p = NaN` and fills `range_score`)
- Evidence: `disc_norep.py` on sensochoc Session 1 only: `neg_log_p count 0`, `range_score count 406`, `heatmap z finite cells: 0 of 406`. The panel still renders the empty chart under the caption "uses an alternative proxy measure". The expander above it says "The heatmap then shows the percentile rank of this range score". For replicated designs, the colour midpoint and title use the default 0.05 whatever `da_alpha` the user set (for example 0.10, which `tests/test_apptest_da.py` uses).
- Impact: Panel leaders without replicate sessions, a common screening design, get a blank discrimination panel whose text says otherwise. With a non-default α, the green/red boundary and the title do not match the α used in the rest of the module.
- Recommendation: Plot `score` (or `range_score`) with its own legend when there are no replicates, or hide the chart and say why. Pass `alpha=st.session_state['da_alpha']`.
- Effort: S
- Dependencies: none

### UI-08: The only help or feedback route is the README; the Streamlit menu is left unconfigured
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `app.py:26-31` (`st.set_page_config` has no `menu_items`); `utils/ui_shell.py:343-351` (About button); `grep -rniE "mailto|issues|github.com|feedback|contact" app.py core modules utils` finds nothing user-facing
- Evidence: Per `streamlit docs st.set_page_config`, when `menu_items` is omitted, "Get help" and "Report a bug" are hidden and the menu's own About shows Streamlit's default dialog. Inside FreeSense, the only outward link is the `git clone https://github.com/...` line in the README shown as the About page. There is no issue-tracker link, no email, and no "how to cite this version" beyond the README citation, which says "Version 1.0".
- Impact: A scientist who hits a suspicious result or a crash has no route to report it. For a statistics tool, that is also how validation gaps get found after release.
- Recommendation: Set `menu_items={"Get help": <docs/methods URL>, "Report a bug": <issues URL or mailto>, "About": <one paragraph with version, licence, disclaimer>}`. Add a "Report a problem" tertiary link beside the sidebar About button. Include the version and module in the prefilled issue.
- Effort: S
- Dependencies: Decision D-2 (support channel)

### UI-09: The in-app About page is the developer README: 7 broken links, developer-only content, and step names that do not match the app
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `app.py:57-67`, `utils/docs.py:15` (`ABOUT_README = README.md`); `README.md` headings at lines 131-331
- Evidence: README has seven relative links (`CHANGELOG.md`, `CLAUDE.md`, `example_data/`, `example_data/README.md`, `LICENSE`, `Statistical_Methods_README.md`, `validation/README.md`). Rendered by `st.markdown` inside the app, they resolve against the app URL and do not open the files. The About footer tells users to "see LICENSE", and they cannot open it from the app. The page also contains Installation, `git clone`, Project Structure, Development Notes, and "Agent guidance … CLAUDE.md … `.claude/agents/`". The CATA step headings do not match the app: README has "Study Setup / Citation Frequencies / Cochran's Q / McNemar Post-Hoc & CLD / Reference-Product Contrast / Correspondence Analysis Map / Penalty Analysis vs Liking / Export", while `MODULES` has "Data upload & setup / Attribute frequency / Product discrimination / Product profiles / Contrast analysis / Correspondence analysis / Penalty analysis / Results & export". The same happens for RATA Step 1 ("Study Setup" vs "Data upload") and PrefMap Step 2 ("Preference Map" vs "External preference map"), and everything is in Title Case against the app's sentence case. README's module table calls RATA's panel "Consumer / semi-trained", while the landing page files RATA under "Trained panel" (`utils/ui_shell.py:45-48`, card text "trained or semi-trained assessors"). README line 154 says the penalty caveat renders "under every significant row", while CLAUDE.md says one caption for the whole table. The sidebar "Statistical methods reference" caption says "every statistical method used in this module" but opens the whole 257 KB document at the top.
- Impact: The page users open to learn what the tool does contradicts the step names they see, and it exposes internal tooling notes. It is also where a licence, a disclaimer and a feedback route would naturally go (UI-08, D-1).
- Recommendation: Write a short user-facing `ABOUT.md` for the overlay: purpose, modules with the panel type agreed per D-4, version, licence text or a summary, disclaimer, how to report problems, how to cite. Keep README for developers. Link to the methods document by section per module, or open it at the module's heading.
- Effort: M
- Dependencies: D-1, D-4

### UI-10: Wrong step numbers in three user-facing cross-references
- Severity: LOW
- Confidence: VERIFIED
- Location: `modules/rata/ui.py:186-190` ("product profiling bar charts (Step 5) … contrast analysis (Step 6)"; actual steps 4 and 5); `modules/descriptive/workflow.py:1228` ("(Step 3 — Product Discrimination)"; actual Step 2); `modules/liking/workflow.py:3248` ("Run Step 4 (Consumer Segmentation) first"; actual Step 5)
- Evidence: `steprefs.py` scanned every "Step N" string in `modules/` against `MODULES`. These are the only mismatches that name a step. The DA equivalent of the RATA note (`modules/descriptive/workflow.py:196-203`) is correct.
- Impact: Sends users to the wrong step. Minor, but it undermines trust in the guidance text.
- Recommendation: Fix the three strings. Better, build step references from `ui_shell.step_title(module, n)` so they cannot drift, and add the scanner as a test.
- Effort: S
- Dependencies: none

### UI-11: Charts have no text equivalent in some mapping steps, so screen-reader users get nothing
- Severity: LOW
- Confidence: VERIFIED for the listed sites (AST scan plus reading the functions); a full step-by-step audit was not done
- Location: `modules/rata/ui.py:1109-1335` (`render_step_5`, Product mapping: PCA and CVA biplots, no scores or loadings table); DA CVA (`modules/descriptive/workflow.py` around 2094 onwards; only PCA gets a loadings expander at `:2082`); `modules/liking/workflow.py:2929-3411` (`render_step_7`, preference map, no table); DA panel-performance chart panels (`_render_repeatability_panel`, `_render_agreement_panel`, `_render_consistency_panel`, `_render_assessor_profiles_panel`)
- Evidence: `charts.py` (functions that call `render_chart` but no table widget) listed 12 functions. By contrast, CATA CA shows row and column coordinate tables (`modules/cata/ui.py:2422-2476`), and DA PCA has a loadings expander. `st.plotly_chart` has no alt-text parameter (`streamlit docs st.plotly_chart`), so the Plotly SVG is opaque to assistive technology.
- Impact: The same analysis is inspectable in one module and not in its sibling. Blind or low-vision users cannot get biplot or preference-map content in the app, only from the Excel export.
- Recommendation: Put a coordinates and loadings table in a collapsed expander under every biplot and map, as CATA does. Add a one-sentence caption summarising the key result, such as PC1% and the products with the largest separation.
- Effort: M
- Dependencies: none

### UI-12: The landing page loses its grouping on narrow screens
- Severity: LOW
- Confidence: VERIFIED (element order); rendering not observed
- Location: `utils/ui_shell.py:168-203` (`render_landing_page` builds a row of section titles, then one `st.columns(3)` per card row)
- Evidence: `landing_order.py` gives the main-area subheader order: `['Consumer methods', 'Trained panel', 'Mapping & integration', 'Check-All-That-Apply', 'Descriptive Analysis', 'Preference Mapping', 'Consumer Liking & Acceptance', 'Rate-All-That-Apply', 'Data Fusion']`. `streamlit docs st.columns`: columns stack when the viewport is at most 640 px. On a phone or a narrow split window, the three section headers therefore stack together at the top and the cards follow in the order CATA, DA, PrefMap, Liking, RATA, Fusion, detached from their headers.
- Impact: Narrow-window and tablet-portrait users see mislabelled groups.
- Recommendation: One `st.columns(3)`, each column holding its header and its two cards. Equal card heights are then lost; accept that, or use `st.container(horizontal=True)` per section with `height="stretch"`.
- Effort: S
- Dependencies: none

### UI-13: Colour-scheme changes apply to some charts immediately and to others only after a re-run
- Severity: LOW
- Confidence: VERIFIED (code)
- Location: product colour maps are frozen at run time (`modules/descriptive/workflow.py:397`, `modules/rata/ui.py:436-437`, `modules/cata/ui.py:997`, `modules/liking/workflow.py:777`). Diverging ramps and cluster maps read `global_colour_palette` live (`modules/liking/workflow.py:1052,1399,1487,1608,1710`, `modules/prefmap/workflow.py:1230,1373,1588`). The warning is at `utils/ui_shell.py:618-627`.
- Evidence: After a palette change, product colours stay on the old palette until "Run full analysis" runs again (for Liking, that includes segmentation), while heatmaps and surfaces switch at once. The warning says a re-run is needed for "cached figures" in either case.
- Impact: A mixed-palette screen, and a full re-analysis just to change colours. That is friction for exactly the users who need the colour-blind option.
- Recommendation: Build product colour maps at render time from the stored product list (cheap) and drop the re-run requirement and the warning.
- Effort: S
- Dependencies: UI-01

### UI-14: The cluster-size KPI uses the metric delta for a share, which renders as a green "increase"
- Severity: LOW
- Confidence: VERIFIED (code); rendering not observed
- Location: `modules/liking/workflow.py:1171-1174` (`metric(..., delta=f"{pct:.0f}% of panel")` with the default `delta_color`); `st.columns(len(cluster_sizes))`
- Evidence: With default `delta_color` and `delta_arrow`, st.metric draws an up arrow in green for a positive delta string. DA's panel KPIs do this correctly with `delta_color="off", delta_arrow="off"` (`modules/descriptive/workflow.py:1681`). With up to k clusters in one `st.columns` row, the cards get narrow at 1366 px with the sidebar open (SUSPECTED, not observed).
- Impact: Cosmetic. It suggests growth or goodness where there is only a proportion.
- Recommendation: `delta_color="off", delta_arrow="off"`, or put the share in the value ("n = 57 (26%)"). Use `st.container(horizontal=True)` instead of `st.columns(k)`.
- Effort: S
- Dependencies: none

## Checked, nothing material found

- **Terminology across modules** (`terms.py`, UI string constants only, docstrings excluded). Counts per group (assessor / panellist / judge / consumer / attribute / descriptor / session / replicate / product / sample):
  - CATA 2/0/0/39/115/0/2/9/100/10
  - RATA 40/0/0/3/101/0/5/33/92/10
  - Descriptive 186/1/0/0/219/0/8/41/219/16
  - Liking 0/0/0/136/20/0/0/0/120/7
  - Fusion 0/0/0/7/16/0/7/1/47/8
  - PrefMap 0/0/0/65/27/0/15/0/48/5
  - shell 2/0/0/28/3/0/1/0/21/0

  The terms are consistent: "assessor" for trained panels, "consumer" for consumer modules, "attribute" throughout (no "descriptor" or "judge"). The two "panellist" sites are prose (`modules/descriptive/workflow.py:2211`, a plot axis at `utils/plotting.py:718`). "Sample" appears mainly as "product/sample column" and "in-sample". "Session" is used alongside "replicate" in DA, deliberately (the sensochoc column is `Session`). British spelling is consistent ("colour" in UI, "color" only in code identifiers).
- **Plot text colours on both themes**: `plot_theme` neutrals pass everywhere (17.4, 16.3, 7.46, 6.96:1). A grep for hard-coded dark font colours in `modules/` and `utils/` found only `'#856404'` (`modules/descriptive/ui.py:236`, 3.25:1 on dark, a zone label next to other cues) and `'#444'` (a line colour). Nothing material.
- **Significance by colour alone in most charts**: contrast bars use opacity plus ★ text (`utils/plotting.py:~1015`). Spider and frequency charts mark ★ in labels (`:179`, `:3408`). CLD letters are text. Styler shading in RATA, CATA and DA tables sits on a "Yes" text column. Exceptions are in UI-05.
- **Keyboard**: all controls are native Streamlit widgets. There is no custom HTML control. The `st.html` scroll reset (`app.py:41-54`) only sets `scrollTop` and does not trap focus. It also does not move focus to the new step heading, so after "Next step" keyboard focus stays at the bottom of the page. This is a minor issue and was not observed.
- **Version display**: the version is shown on the landing footer (`ui_shell.py:203`), the sidebar About button (`:348`), the About caption (`app.py:64`) and the export `Run_Parameters`. It comes from a single source (`core/__version__.py`). Whether "1.0.0" is the right string is D-3.
- **Beta labelling**: consistent on the landing badge, sidebar badge with help text, Step 1 caption and export.
- **Error bars and SE conventions**: out of scope here (B01).
- **Step header and sidebar names**: both derive from `MODULES` (`step_title`), so they cannot drift.
- **Liking contrast spider with a single axis** (coordinator lead): already handled. `modules/liking/ui.py:1217-1232` shows the spider tab only when `len(selected_attributes) >= 2`. With one attribute, only the butterfly and table tabs are shown.
- **Methods reference navigation** (coordinator lead, confirmed): `app.py:69-74` renders the whole 257 KB `Statistical_Methods_README.md` (391 headings) as one `st.markdown`, with no search, no table of contents and no jump to the active module. Browser find (Ctrl+F) still works. This is folded into the UI-09 recommendation (open the page at the module's section) and not raised as a separate finding.
- **AppTest walk of DA Steps 1 to 8**: no exceptions. Every step has a header, captions and nav controls. There is no `st.info` misuse on the happy path.

## Decisions raised

- **D-1 Disclaimer.** The app has no statement about warranty or result verification except the MIT text in `LICENSE`, which is not reachable from inside the app (UI-09), and the beta note on Fusion and PrefMap. Decide whether stable modules get a short "results are provided without warranty; verify critical conclusions" line in About or on the landing footer, and whether exports carry one in `Run_Parameters` or `Methods_Notes`. This is a legal and product call.
- **D-2 Support channel.** GitHub issues, email, or none. UI-08 depends on it. For a hosted deployment, also decide whether `client.showErrorDetails` stays at its default "full" (see leads).
- **D-3 Version string.** "1.0.0" is shown in four places while `v1.0.0` is tagged 146 commits earlier (orientation §4). Choose the release version before the About rewrite.
- **D-4 RATA positioning.** The landing page puts RATA under "Trained panel". README says "Consumer / semi-trained". In the literature, RATA is mostly used as a consumer method (Ares et al., 2014, Food Quality and Preference 36; Meyners, Jaeger & Ares, 2016). Pick one framing and use it in both places.
- **D-5 Accessibility target.** Decide whether the release claims any WCAG level. If AA is targeted, UI-02, UI-03, UI-05, UI-06 and UI-11 become release blockers for that claim.
- **D-6 Default palette.** Whether the colour-blind-safe palette (after the UI-06 fix) should be the default.

## Leads for other areas

- `client.showErrorDetails` resolves to `full` (`streamlit.config.get_option`): uncaught exceptions show full tracebacks with server paths to users (B07 security / hosted deployment).
- `modules/liking/ui.py:966` `plot_mdpref_heatmap` is dead code (callers import `utils.plotting.plot_mdpref_heatmap`) and hard-codes `RdYlGn` (code quality).
- The PREFMAP guide claims "ideal point: 5 parameters". Check this against the circular and elliptical forms actually fitted in `stats/prefmap.py` (B01).
- The landing card describes DA as "Mixed-effects ANOVA", while README says "Two-way OLS ANOVA (Type III) + conditional F-test". Check which wording is accurate (B01/docs).
- The DA Step 1 default scale max is 100 (`tests/test_apptest_da.py` asserts it), while the bundled DA dataset is 0 to 10. Check whether the scale validation catches this (B02/UX).
- 16 Fusion figures set `template='plotly_white'` (`modules/fusion/ui.py`). How Streamlit's dark theme merges with an explicit template was not verified. SUSPECTED white panels or low-contrast text on the dark theme; confirm in a browser.
- Some chart heights are unbounded or large (`utils/plotting.py:1020`, contrast chart `18 × products × attributes + 150` px; several fixed at 800 to 1000 px). On a 1366×768 laptop, the title, axis and legend cannot be seen together. SUSPECTED, not observed.
- The sidebar "Plot export format" is a 2-option vertical `st.radio`, where the house convention is `st.segmented_control` (polish).
