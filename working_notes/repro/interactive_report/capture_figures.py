"""Capture the exact Plotly specs the app sends to the browser (DA, sensochoc).

Run from the repository root:  env/bin/python working_notes/repro/interactive_report/capture_figures.py
Writes one JSON file per chart to working_notes/repro/interactive_report/out/specs/.
Each file holds the spec, the config and the width mode, as `st.plotly_chart`
put them in the protobuf, so the spike renders the same bytes the app does.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from tests.conftest import upload_file  # noqa: E402
from tests.test_apptest_bundled_datasets import _click, _go, _select  # noqa: E402
from tests.test_apptest_smoke import _open_module  # noqa: E402

OUT = Path(__file__).parent / "out" / "specs"


def _charts(at):
    return [e for e in at.get("plotly_chart")]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = REPO / "example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx"
    at = _open_module("Descriptive Analysis")
    upload_file(at, "da_upload_main", path)
    _select(at, "da_assessor", "Panelist")
    _select(at, "da_product", "Product")
    _select(at, "da_replicate", "Session")
    at.number_input(key="da_scale_max").set_value(10).run()
    _click(at, "da_run_analysis")
    n = 0
    for step in (2, 3, 4, 5):
        _go(at, "Descriptive", step)
        for el in _charts(at):
            p = el.proto
            rec = {"step": step, "id": p.id, "theme": p.theme,
                   "spec": json.loads(p.spec), "config": json.loads(p.config or "{}")}
            # width mode lives in the element's layout config in 1.64
            rec["width_proto"] = str(getattr(el, "width", ""))
            (OUT / f"da_s{step}_{n:02d}.json").write_text(json.dumps(rec))
            n += 1
            print(step, n, (rec["spec"]["layout"].get("title") or {}).get("text"))
    print("written", n)


if __name__ == "__main__":
    main()
