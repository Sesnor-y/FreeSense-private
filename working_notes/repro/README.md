# Review reproduction material

These are copied from the review session's temporary scratchpad (2026-09-27) so the stage sessions can reuse them.

- **Tracked here, excluded from the release.** `working_notes/` is tracked in this private development repository, so the review record and these scripts are versioned with the code they describe. It is never copied into the public release repository: Stage 9A builds that repository from a clean tree without `working_notes/`.
- **Generated data files are not tracked.** The repository-wide `*.csv` / `*.xlsx` / `*.xls` / `*.xlsm` rule in `.gitignore` still applies inside `working_notes/`. Inputs and outputs the scripts write (for example `B02/data/`, `B03/*.xlsx`) exist only on the machine that ran them; re-run the script to regenerate them.

- `B01/` to `B10/`: each area reviewer's scripts, generated test inputs and outputs, cited in the matching `B<nn>-*.md` report and in `01-findings-register.md`.
- `CA/`, `CB/`, `CC/`: the independent challenge passes (A: statistics, workflow and import; B: testing, security, packaging and documentation; C: the two performance BLOCKERs), with their `challenge_*_results.md`.
- `challenge_*.md`, `challenge_list.md`: exactly what each challenger was given.
- `preamble.md`: the shared instructions every area reviewer received.
- `build_register.py`, `register_head.md`: the script that assembled `01-findings-register.md` from the B reports.

Notes for reuse:

- **Paths.** Scripts were written to run from the repository root with `env/bin/python`. Many refer to absolute scratchpad paths (`/tmp/claude-1000/...`); change those to `working_notes/repro/<dir>/` before running.
- **Deliberately not copied:**
  - a throwaway virtual environment and downloaded wheels (B08);
  - the full git history patch (B07);
  - coverage data;
  - the zip-bomb test workbooks (`B07/zipbomb.py` and `CB/sec02b.py` regenerate them);
  - the formula-injection test exports (`B07/formula_injection.py` and `CB/sec01.py` regenerate them; do not open those in Excel);
  - the third-party files extracted from git history for inspection (XLSTAT workbook, `PLS.pptx`, `PLS.pdf`). Those are the SEC-04 files and must not be redistributed.
- **Useful starting points:**
  - `B02/harness.py`: real-upload AppTest driver, for Stage 5 item 7.
  - `CC/perf01_apptest.py`: stale-cache reproduction, PERF-01.
  - `CA/f01.py`: the "Var"/"Cov" product-name bug, FUNC-01.
  - `CA/mkfiles.py`: builds bad input files, the starting point for Stage 3's fixture set.
  - `B05/t3.py`: DA Type III known-answer check.
