"""Build each module's report from a real AppTest run (manual visual check).

    env/bin/python working_notes/repro/interactive_report/build_reports.py RATA CATA Liking
Writes working_notes/repro/interactive_report/out/<module>_report.html
"""
import importlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from core.config import MODULES  # noqa: E402
from tests.conftest import open_every_gated_panel  # noqa: E402
from tests.test_apptest_bundled_datasets import _go  # noqa: E402
from tests.test_apptest_reports import CASES  # noqa: E402
from tests.test_apptest_smoke import _open_module  # noqa: E402

for name in sys.argv[1:]:
    case = CASES[name]
    at = _open_module(MODULES[case.module]["name"])
    case.run(at, REPO / "example_data" / case.data)
    for n in range(2, len(MODULES[case.module]["steps"]) + 1):
        _go(at, case.module, n)
        open_every_gated_panel(at)
    mod = importlib.import_module(case.report)
    html = mod.build_report_html(dict(at.session_state.to_dict()),
                                 sections=list(mod.SECTION_LABELS))
    out = Path(__file__).parent / "out" / f"{name}_report.html"
    out.write_bytes(html)
    print(name, f"{len(html) / 1e6:.1f} MB", out.name)
