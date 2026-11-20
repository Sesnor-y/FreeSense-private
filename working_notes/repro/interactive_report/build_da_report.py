"""Build the DA report from a real AppTest run on sensochoc (manual check).

    env/bin/python working_notes/repro/interactive_report/build_da_report.py [--ids]
Writes working_notes/repro/interactive_report/out/da_report.html
"""
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from core.config import MODULES  # noqa: E402
from tests.conftest import open_every_gated_panel, upload_file  # noqa: E402
from tests.test_apptest_bundled_datasets import _click, _go, _select  # noqa: E402
from tests.test_apptest_smoke import _open_module  # noqa: E402

at = _open_module("Descriptive Analysis")
upload_file(at, "da_upload_main", REPO / "example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx")
_select(at, "da_assessor", "Panelist")
_select(at, "da_product", "Product")
_select(at, "da_replicate", "Session")
at.number_input(key="da_scale_max").set_value(10).run()
_click(at, "da_run_analysis")
for n in range(2, len(MODULES["Descriptive"]["steps"]) + 1):
    _go(at, "Descriptive", n)
    open_every_gated_panel(at)
state = dict(at.session_state.to_dict())

from modules.descriptive.report import build_report_html, SECTIONS  # noqa: E402
t = time.time()
html = build_report_html(state, sections=[s.id for s in SECTIONS], include_ids="--ids" in sys.argv)
out = Path(__file__).parent / "out" / "da_report.html"
out.write_bytes(html)
print(f"{len(html)/1e6:.2f} MB in {time.time()-t:.1f} s → {out}")
