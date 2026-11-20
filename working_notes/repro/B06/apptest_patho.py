import sys, os, time, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import gen, core.data as core_data, utils.ui_shell as ui_shell
from tests.test_apptest_smoke import _open_module
class _Upload: name = "synthetic.xlsx"
ui_shell.render_data_upload_section = lambda *a, **k: _Upload()
for label, raw in [("1 product", gen.da(10, 1, 5, 2)), ("2 products", gen.da(10, 2, 5, 2)), ("1 attribute", gen.da(10, 5, 1, 2)),
                   ("2 products x 12 assessors x 3 reps x 8 attrs", gen.da(12, 2, 8, 3))]:
    core_data.load_data = lambda _f, raw=raw: raw.copy()
    at = _open_module("Descriptive Analysis")
    at.selectbox(key="da_assessor").set_value("Panelist").run(); at.selectbox(key="da_product").set_value("Product").run()
    at.selectbox(key="da_replicate").set_value("Session").run(); at.number_input(key="da_scale_max").set_value(10).run()
    btn = [b for b in at.button if b.key == "da_run_analysis"]
    if not btn:
        print(label, "-> Run button not rendered; errors:", [e.value[:120] for e in at.error]); continue
    btn[0].click().run(timeout=600)
    print(label, "-> exception:", [str(e.value)[:200] for e in at.exception] if at.exception else None,
          "| errors:", [e.value[:120] for e in at.error], "| complete:", at.session_state["analysis_complete"] if "analysis_complete" in at.session_state else None)
