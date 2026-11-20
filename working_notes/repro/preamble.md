You are one of ten parallel reviewers preparing FreeSense (a Python/Streamlit sensory and consumer data analysis app, repo root /var/home/Lukas/Projects/RATA-Flow-App) for its first release. This is a REVIEW-ONLY task.

READ FIRST: /var/home/Lukas/Projects/RATA-Flow-App/working_notes/00-orientation.md (shared codebase map, test/lint results, prior-review history, and the mapping from R/Shiny terms to the Python equivalents used here). Also skim CLAUDE.md for the project's stated conventions, but treat every document (CLAUDE.md, README, CHANGELOG, Statistical_Methods_README.md, docs/open-items.md, old reviews in git history) as a CLAIM TO VERIFY against the code, never as fact.

Release context: the owner has NOT filled in the release context. Version, release type, audience, deployment (local install vs hosted), licence/IP, supported platforms, date and scope are all undecided. Where your area depends on one of these, record it as a decision needed (a short "Decisions raised" section at the end of your report), and where useful assess both likely scenarios (e.g. local single-user vs hosted multi-user). Assume the audience is sensory scientists in industry and academia unless the code implies otherwise.

HARD RULES
- Do NOT modify application code, tests, data, configuration, the venv, or git state (no commits, no stash, no checkout). The ONLY file you may create in the repo is your report at the path given below. Put any scratch scripts, generated datasets or outputs in /tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/<your-area>/ . If you run something that writes .coverage, __pycache__ or _out/ files in the repo, that is tolerated, but nothing else.
- Use the project venv: /var/home/Lukas/Projects/RATA-Flow-App/env/bin/python . Run from the repo root so imports resolve. Headless use of stats functions: they are wrapped in @st.cache_data, which works outside `streamlit run` (with warnings); validation/_common.py shows how the repo stubs Streamlit. Streamlit AppTest (streamlit.testing.v1.AppTest) is available; see tests/test_apptest_*.py and tests/conftest.py for how to drive the app headlessly. The full test suite has already been run (366 passed) - do NOT rerun the full suite; run only targeted tests or your own scripts. Nine other reviewers share this machine's CPU, so keep heavy jobs modest.
- R is NOT installed. Do not try to install it. For independent references use Python (scipy, statsmodels, numpy hand calculations), the frozen R reference CSVs in validation/*/reference/, published numbers you can cite, or hand derivations.
- Do not spawn subagents.
- Evidence before claims. Every finding cites file path and line range, a function name, or a reproducible command/input. If you could not verify something, mark it SUSPECTED and say what would confirm it. Never present a suspicion as fact. Use "Observed:" and "Inferred:" where the distinction matters.
- Run things, don't just read them. Record exact commands and the relevant output in your evidence.
- No invented issues. Do not pad. An empty category with "reviewed, nothing material found, here is what was checked" is a valid result. Prefer 8 solid findings to 30 thin ones.
- Product, legal or scientific judgement calls go in "Decisions raised", not as findings.
- Prior work: old review docs in git history (e.g. `git show d9ac9d5^:docs/review/01_stats_findings.md`, and files under docs/review/, AUDIT_*.md in history) are leads only. For any fix they describe, confirm from current code whether it is present, correct and covered by tests. Do not reopen a deliberate, documented design choice unless you find a concrete defect.
- Writing: British English spelling (colour, organise, analyse). Do NOT use em dashes. Avoid en dashes as punctuation.

FINDING FORMAT (use exactly, one block per finding):

### <AREA>-<nn>: <short title>
- Severity: BLOCKER | HIGH | MEDIUM | LOW
- Confidence: VERIFIED | SUSPECTED
- Location: <file:lines, function, or module>
- Evidence: <what was observed, command run, input used, output seen>
- Impact: <who is affected and how; for statistical issues, whether results could be wrong>
- Recommendation: <specific fix>
- Effort: S (under 2h) | M (half day to 2 days) | L (more than 2 days)
- Dependencies: <other findings or decisions this relies on, or "none">

Severity: BLOCKER = could produce incorrect scientific results without warning, loses or exposes user data, crashes a core workflow, or creates a legal/licensing problem; must be fixed before release. HIGH = significantly degrades a core workflow or user trust; fix before release unless explicitly accepted. MEDIUM = noticeable problem with a workaround; point release. LOW = polish.

REPORT STRUCTURE: title; "Scope and method" (what you checked, commands run, datasets used); "Findings" (ordered by severity); "Checked, nothing material found" (list); "Decisions raised"; "Leads for other areas" (things outside your brief you noticed, one line each). When finished, reply with a short summary: counts by severity and the titles of any BLOCKER/HIGH findings.
