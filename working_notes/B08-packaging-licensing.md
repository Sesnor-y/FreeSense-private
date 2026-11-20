# B08 Packaging, licensing and release engineering (prefix REL)

Reviewer: Claude (B08), review-only. Commit `bcaf9f8`. Date 2026-09-26.
Nothing in this report is legal advice. Licence statements below describe what the licence texts and package metadata say and what the usual interpretations are; every "what should we do" is carried into Decisions raised.

## Scope and method

Checked: project metadata (`pyproject.toml`, `requirements.txt`, `core/__version__.py`, `LICENSE`, README Installation/Citation/License sections, `CHANGELOG.md` headings), dependency licences (all installed distributions, runtime and transitive), assets, example-data notices, git tags against the remote, public reachability of the repository, wheel availability for the supported platform/Python matrix, kaleido 0.2.1 behaviour, a clean install and smoke test in a fresh venv, and the app's behaviour without pingouin.

Commands run (scratch dir `.../scratchpad/agents/B08/`):

1. Clean install: `python3 -m venv venv && venv/bin/pip install -q -r requirements.txt` with system `/usr/bin/python3` = **Python 3.14.7** (same minor as the project venv; no 3.11/3.12/3.13 interpreter on this machine). Result: **exit 0, 25.7 s wall**, all from wheels.
2. `pip freeze` diff, fresh venv vs project `env/`: 4 packages differ (`fonttools 4.65.0 -> 4.66.0`, `pytz 2026.3.post1 -> 2026.4`, `uvicorn 0.53.0 -> 0.54.0`, `wrapt 2.4.2rc1 -> 2.5.0rc1`).
3. Import check in the fresh venv: every `.py` under `core/ stats/ utils/ modules/` imported via `importlib` -> **52 imported, 0 failed**.
4. AppTest smoke in the fresh venv: `pytest tests/test_apptest_smoke.py tests/test_apptest_render_chart.py` -> 13 passed, 32 s.
5. kaleido 0.2.1 in the fresh venv: `fig.to_image` for png/svg/pdf -> 10856 / 6080 / 13471 bytes, 2.2 s. Works on Linux x86_64, Python 3.14.
6. Without pingouin: `pip uninstall pingouin` in the fresh venv, then `pytest tests/test_panel_performance_summary.py tests/test_validation_pins.py -rA` -> 19 passed, exit 0; `tests/test_apptest_da.py` also ran to exit without failures (5.5 min, output only warnings).
7. Wheel resolution matrix: `pip download --only-binary=:all: -r requirements.txt --python-version X --platform Y`:

   | Target | Result |
   |---|---|
   | Linux x86_64, py3.11 | OK (resolves numpy 2.4.6, scipy 1.17.1) |
   | Linux x86_64, py3.14 | OK (numpy 2.5.3, scipy 1.18.1) |
   | Linux aarch64, py3.14 | OK |
   | macOS arm64, py3.11 | OK |
   | macOS arm64, py3.14 | OK once `streamlit` is taken with `--no-deps` (the full-requirements failure on `watchdog` is an artefact of cross-platform `pip download`: pip evaluates `platform_system != "Darwin"` against the host, so it is not evidence of a real problem) |
   | Windows amd64, py3.11 and 3.14 | OK |
   | Linux x86_64, **py3.10** | **FAIL**: `No matching distribution found for numpy<3.0.0,>=2.3.2` |
   | kaleido 0.2.1 | wheels exist for manylinux1 x86_64, manylinux2014 aarch64, macOS 10.11 x86_64, macOS 11 arm64, win_amd64 (`py2.py3-none`, so Python-version independent) |
8. Licence metadata of every installed distribution in `env/` via `importlib.metadata` (License-Expression / License / classifiers).
9. `git ls-remote origin` (authenticated with the owner's credentials) and unauthenticated `curl` / `git ls-remote` against GitHub.
10. `pip index versions` for the pinned packages to compare ceilings with current releases.

## Findings

### REL-01: The GitHub repository is private, so README's clone command and citation URL fail for every user
- Severity: HIGH
- Confidence: VERIFIED
- Location: `README.md:45` (`git clone https://github.com/Sesnor-y/FreeSense.git`), `README.md:425` (citation URL)
- Evidence: `curl -o /dev/null -w "%{http_code}" https://github.com/Sesnor-y/FreeSense` -> `404`; the owner page `https://github.com/Sesnor-y` -> `200`; `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote https://github.com/Sesnor-y/FreeSense.git` -> `fatal: could not read Username`. `api.github.com/repos/Sesnor-y/FreeSense` -> 404. Authenticated `git ls-remote origin` works, so the repository exists and is private (Inferred; a deleted repo would fail authenticated too).
- Impact: the installation instructions and the recommended citation point at a URL that returns 404 for anyone but the owner. A paper citing it would carry a dead link. This is also the precondition for REL-02: making the repository public today would publish its full history.
- Recommendation: decide the distribution channel (Decisions raised). If the code is to be public, publish a repository whose history has been cleaned (REL-02) and only then make the README URLs true. If it stays private, replace the clone/citation instructions with whatever route users will actually get the code by.
- Effort: S (once the decision is made)
- Dependencies: REL-02, decision D1

### REL-02: Git history contains third-party copyrighted files; making the repo public as-is would redistribute them
- Severity: HIGH (becomes BLOCKER if the repository, or a clone with history, is made public)
- Confidence: VERIFIED for presence (details in B07); licensing status SUSPECTED
- Location: history only. `git log --all --diff-filter=A --name-only` lists `example_data/LIK_tuto_EN.xlsm`, `PLS.pptx`, `docs/PLS.pdf`, plus build artefacts `Rplots.pdf`, `validation/PrefMap/_out/carto_reference.pdf`. Commits touching them include `acf8ffa`, `1a6d701`, `01065d1`, `a6b5d33`, `fd50b56`, `bbd91e2`. B07 identifies the first two as XLSTAT (Addinsoft) tutorial material, the `.xlsm` with VBA macros.
- Evidence: see B07 for provenance. From the licensing side: none of these files is covered by the repo's MIT `LICENSE`, and no licence or permission notice for them exists anywhere in history I could find (`git ls-files` shows no NOTICE/COPYING file at any point).
- Impact: a public push of this history would redistribute a commercial vendor's tutorial workbook, slides and a PDF without a licence. Deleting the files in a later commit does not remove them from the published history. The repository being private today (REL-01) is what keeps this from being a live problem.
- Recommendation: before any public release, either (a) publish from a fresh repository with a squashed/new history, or (b) rewrite history with `git filter-repo --invert-paths --path example_data/LIK_tuto_EN.xlsm --path PLS.pptx --path docs/PLS.pdf ...` and force-push, accepting that existing clones/forks keep the old objects. Option (a) is simpler and also removes the absolute-home-path leaks noted in the orientation. Coordinate with B07.
- Effort: S to M
- Dependencies: B07 findings on history content, decision D1

### REL-03: pingouin (GPL-3.0) is installed by default and imported by the MIT-licensed app; licence position undocumented
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
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `requirements.txt` (ranges only); no lock/constraints file in the repo
- Evidence: a fresh install on the same Python on the same day as the project venv differed in four packages (step 2 above). `wrapt` resolves to a **pre-release** in both venvs (`2.4.2rc1` in `env/`, `2.5.0rc1` fresh) because `formulaic` (pulled in by statsmodels 0.15) declares `wrapt>=1.17.0rc1; python_version >= '3.13'`, and a pre-release in the specifier makes pip accept pre-releases. On Python 3.11 the resolver picks numpy 2.4.6 / scipy 1.17.1, versions the test suite has never run on. README (`README.md:35-41`) itself cites a past silent wrong-result incident caused by an unexpected build, which is exactly what a lock prevents.
- Impact: a user's results can come from a dependency set nobody tested; bug reports cannot be reproduced; a pre-release runtime library is installed silently.
- Recommendation: keep `requirements.txt` as the human-readable range file, and add a generated lock per supported Python (e.g. `pip-compile --generate-hashes` or `uv pip compile --python-version 3.1x`), referenced from README as the reproducible install. Optionally constrain `wrapt<2.5` or to a final release. Record the resolved versions (or `pip freeze` hash) in the `Run_Parameters` export next to `freesense_version`.
- Effort: S
- Dependencies: REL-06

### REL-05: Version string, tag and changelog disagree; `v1.0.0` tag is local only
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `core/__version__.py:1` (`1.0.0`), `utils/ui_shell.py:203` (sidebar caption), `utils/export.py:356` (every export's `Run_Parameters`), `README.md:3` and `:425` ("v1.0"/"Version 1.0"), `Statistical_Methods_README.md:4` ("Version: 1.0"), `CHANGELOG.md:8,201,286` (`[Unreleased]`, `[1.1.0] — Unreleased`, `[1.0.0] — Unreleased`)
- Evidence: `git tag -l` shows `v0.2.0` and `v1.0.0` (on `a4c3eb2`, 2026-05-18); `git rev-list --count v1.0.0..HEAD` = 146. Authenticated `git ls-remote origin` returns only `HEAD` and `refs/heads/main` -> **no tags have been pushed** (this corrects the orientation note, which said the tag is on the remote). No GitHub release is possible to confirm (repo private, `gh` not installed; unauthenticated API 404). Code that differs materially from `a4c3eb2` (Type II/LS-means changes, panel-performance fixes) still labels its exports `freesense_version = 1.0.0`, so two different computations are indistinguishable in an exported workbook.
- Impact: provenance of results is ambiguous; a user who reports "1.0.0" could mean either codebase.
- Recommendation: since nothing has been published, delete the local `v1.0.0` tag (or leave it and never push it) and cut the first public release from HEAD. Scheme: SemVer with the version in `core/__version__.py` only; collapse the three CHANGELOG headings into one dated `[1.0.0] - YYYY-MM-DD` (or `[0.9.0]` if beta modules ship, see D3) with the historical detail folded in; tag `vX.Y.Z` annotated on the release commit and push it; bump to `X.Y.(Z+1).dev0` after the tag so development builds never claim a release number. Optionally add the short git SHA to `Run_Parameters` for dev builds. Update the "v1.0"/"Version 1.0" strings in README and Statistical_Methods_README from the same source, or drop the version from those headers.
- Effort: S
- Dependencies: decision D3

### REL-06: Python support claim untested; `pyproject` ruff target contradicts the dependency floor; dev tools mixed into runtime requirements
- Severity: MEDIUM
- Confidence: VERIFIED
- Location: `README.md:35` ("Python 3.11–3.14"), `pyproject.toml:3` (`target-version = "py310"`), `requirements.txt:15-17` (`pytest`, `pytest-xdist` under "dev / test"), no CI (`.github/` absent)
- Evidence: py3.10 cannot install (numpy floor `>=2.3.2` has no 3.10 wheel, step 7). 3.11 installs from wheels on Linux, macOS arm64 and Windows, but with a different numpy/scipy set that has never been tested; this machine only has 3.14. pytest and pytest-xdist are installed into every user and Streamlit Cloud deployment. `ruff` is configured in `pyproject.toml` but not listed anywhere, and CLAUDE.md says "No linter is configured".
- Impact: the README claim is aspirational for 3.11 to 3.13. Users on 3.11/3.12 run an untested dependency set. Minor bloat on deployments.
- Recommendation: either narrow the claim to what is tested, or add a small CI matrix (3.11 and 3.14 on Linux, plus one Windows/macOS job) running `pytest` and `ruff`. Set `target-version = "py311"`. Split `requirements-dev.txt` (`-r requirements.txt`, pytest, pytest-xdist, ruff). Add `requires-python = ">=3.11"` if a `[project]` table is added (REL-07).
- Effort: S (split, target), M (CI)
- Dependencies: decision D4

### REL-07: No project metadata; no bug-report route
- Severity: LOW
- Confidence: VERIFIED
- Location: `pyproject.toml` (only `[tool.ruff]`); README has an Author line (`README.md:5`) but no contact, issues link or support statement
- Evidence: `pyproject.toml` contents; `grep -in "issue\|bug\|contact" README.md` finds only unrelated hits.
- Impact: no machine-readable name, version, licence, authors, `requires-python` or URLs; users have no stated route to report a wrong result, which for a statistics tool matters.
- Recommendation: add a `[project]` table (name, `dynamic = ["version"]` reading `core/__version__.py` or a static version, description, `license = "MIT"`, `license-files`, authors, `requires-python`, `dependencies`, `[project.urls]` Homepage/Issues/Changelog) even if the app is never built as a wheel; add a "Reporting problems" section to README naming the route (GitHub Issues once public, or an email).
- Effort: S
- Dependencies: D1

### REL-08: Example datasets: GPL notice present, but no copy of the GPL text is shipped
- Severity: LOW
- Confidence: VERIFIED (absence); requirement interpretation SUSPECTED
- Location: `example_data/README.md:11-23`, `README.md:435-452`; `git ls-files | grep -iE "copying|licen|gpl|notice"` returns only `LICENSE` (MIT)
- Evidence: attribution, source package, version, authors, licence name, download date and "reshaped" wording are present and good. GPL-2.0 s.1 and GPL-3.0 s.4 ask that recipients receive a copy of the licence with the material; none is in the repo. The files are modified (reshaped columns, dropped `Rank`), which the README states, satisfying the modification-notice point in spirit.
- Impact: small compliance gap for anyone redistributing the repo with `example_data/`. Whether data tables are copyrightable at all is a separate question (Decisions raised).
- Recommendation: add `example_data/COPYING` (GPL-2.0 text, since "GPL (>= 2)" lets you pick 2) and reference it from `example_data/README.md`. Consider whether the derived reference CSVs in `validation/*/reference/` need the same note (they are computed statistics, so probably not; owner's call).
- Effort: S
- Dependencies: none

### REL-09: kaleido 0.2.1 / plotly 5 pins will age out; ceilings exclude current major releases
- Severity: LOW
- Confidence: VERIFIED (versions); risk timing SUSPECTED
- Location: `requirements.txt:4-5,2`
- Evidence: current PyPI: plotly 7.1.0, kaleido 1.4.0, pandas 3.0.6; pins are `plotly<6`, `kaleido==0.2.1`, `pandas<3`. kaleido 0.2.1 works here (step 5) and has `py2.py3-none` wheels for Linux x86_64/aarch64, macOS x86_64/arm64 and Windows, so it is independent of Python version. Its wheel bundles a Chromium build (221 MB installed in `env/`, with `CREDITS.html` and `LICENSE.txt`). pandas 2.3.3 is the last 2.x and already has cp314 wheels.
- Impact: no current breakage. Over the release's life: no security updates for the bundled Chromium (it only renders app-built figures, so exposure is low); plotly 5 / pandas 2 will stop getting wheels for new Pythons (3.15). Docker images carry 221 MB of Chromium.
- Recommendation: accept for this release; add a backlog item to migrate to plotly 6+/kaleido 1.x (which uses a system Chrome, a different deployment story) and pandas 3 with the regression pins as the safety net.
- Effort: M (future)
- Dependencies: none

### REL-10: No citation metadata for academic users
- Severity: LOW
- Confidence: VERIFIED
- Location: `README.md:421-425`; no `CITATION.cff`; no DOI
- Evidence: file listing; the citation line says "Version 1.0" and a URL that 404s (REL-01).
- Impact: reference managers and GitHub's "Cite this repository" cannot pick it up; reviewers increasingly ask for a versioned, archived software citation (DOI) so a result can be tied to an exact code version.
- Recommendation: add `CITATION.cff` (cff-version 1.2.0, title, authors with ORCID, version, date-released, licence, repository-code, and `references` for SensoMineR/cata/the methods papers if desired); once public, connect Zenodo to the GitHub repository so each release tag gets a DOI, and put the concept DOI in README. Generate the README citation from the same data.
- Effort: S
- Dependencies: REL-01, REL-05

### REL-11: No deployment artefacts for any channel
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

### REL-12: Broken `.claude/skills` symlink tracked in git
- Severity: LOW
- Confidence: VERIFIED (tracked as mode 120000); breakage per B07
- Location: `.claude/skills/developing-with-streamlit` (`git ls-files -s` -> mode `120000`)
- Evidence: see B07. For packaging: a dangling tracked symlink also breaks naive archive or Docker `COPY` steps on some platforms and fails on Windows checkouts without symlink support.
- Recommendation: exclude `.claude/` (and `CLAUDE.md`, `working_notes/`) from release archives and images via `.gitattributes export-ignore` and `.dockerignore`, or vendor the skill as real files.
- Effort: S
- Dependencies: B07

## Checked, nothing material found

- Clean install on Python 3.14.7 (Linux x86_64): succeeds from wheels only, 25.7 s; all 52 app modules import; AppTest smoke passes in the fresh venv.
- Wheels exist for all runtime requirements on Linux x86_64/aarch64, macOS arm64 and Windows for Python 3.11 and 3.14 (3.12/3.13 not checked individually; bounded by the same floors).
- kaleido 0.2.1 export (png/svg/pdf) works on this platform and Python.
- App runs without pingouin (README claim holds; tests pass with it uninstalled).
- Licences of all other runtime and transitive dependencies are permissive (MIT, BSD-2/3, Apache-2.0, PSF, MIT-CMU, MPL-2.0 for certifi which is file-level copyleft and unmodified). Streamlit's bundled Material Symbols icons are Apache-2.0 (Google), shipped inside Streamlit itself; no action.
- `assets/freesense.svg` and `freesense_wordmark.svg`: hand-authored path geometry in the brand teal, no embedded raster or font; the wordmark only names system fonts (`Source Sans Pro`, Segoe UI, Helvetica, Arial) by `font-family`, which embeds nothing. Added in `71460d5`. No third-party asset concern found (origin is the owner's own commit; I cannot verify authorship beyond that).
- Example-data attribution (sources, versions, authors, citations, download date, modification statement): present and adequate. README's claim that no application code reads `example_data/` holds (`grep` in `app.py core modules stats utils` finds none); tests skip loudly when it is absent (`tests/conftest.py:26-34`).
- `LICENSE` is a correct MIT text with copyright holder and year.
- Dev-only packages (pytest, pytest-xdist, execnet, iniconfig, pluggy) are MIT.

## Decisions raised

- **D1 Distribution channel and visibility.** Local clone + pip, Streamlit Community Cloud, Docker/self-hosted, or institutional server; public or private repository. Drives REL-01, REL-02, REL-07, REL-10, REL-11.
- **D2 pingouin / GPL-3.0.** Replace with own ICC CI code, make optional and not installed by default, keep and document, or relicense FreeSense as GPL-3.0. This is a licensing/product decision; the review states the common interpretation only and it should be confirmed with whoever advises the owner or their institution on licensing.
- **D3 Version number of the first public release.** `1.0.0` from HEAD (discarding the unpushed local tag) or a `0.x`/`1.0.0` with the two beta modules excluded or labelled; interacts with scope decisions on Fusion/PrefMap.
- **D4 Supported Python/platform matrix.** Claim only what CI (or a manual pre-release run) actually covers.
- **D5 Example datasets.** Keep bundling GPL datasets in the main repo (with GPL text added), move them to a separate data repo/download, or ship only in source and not in images. Whether reshaped published data tables attract copyright at all is jurisdiction-dependent; not decided here.
- **D6 History rewrite vs fresh public repository** before publication (REL-02), coordinated with B07.

## Leads for other areas

- B01/stats: `pg.intraclass_corr` CI (`stats/panel_performance.py:252`) is computed on pingouin's complete-case targets x raters table, while the ICC point estimate uses harmonic-mean k on unbalanced data; CI and estimate can come from different data on unbalanced designs. The CIs are not covered by any validation pin (`validation/DA/reference/ref_icc.csv` has only `ICC_ref`).
- B01/stats: the stats layer rounds ICC and CI values (`round(icc, 3)`, `round(ci_row['CI95%'][0], 3)` at `stats/panel_performance.py:234,262`), contrary to the display-layer-rounding convention (that convention is stated for p-values only, so this may be accepted).
- B07: `docs/PLS.pdf`, `PLS.pptx`, `LIK_tuto_EN.xlsm` in history; see REL-02 for licensing side.
- Orientation doc correction: `v1.0.0` is not on `origin` (authenticated `git ls-remote origin` lists no tags).
- B06/ops: `Run_Parameters` records the FreeSense version but not dependency versions; with no lockfile (REL-04), a results workbook cannot be tied to a numpy/statsmodels version.
