import sys, io, warnings, json
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")
import pandas as pd, numpy as np
from tests.test_apptest_smoke import _open_module
import core.data as core_data, utils.ui_shell as ui_shell
from core.config import MODULES
S = sys.argv[2]; mod = sys.argv[1]
captured = {}
figs = []
def cap_export(build, module_name, **k): captured['build']=build; captured['name']=module_name
import modules.rata.ui as r_ui, modules.descriptive.workflow as d_wf, modules.cata.ui as c_ui, modules.liking.workflow as l_wf
for m in (r_ui, d_wf, c_ui, l_wf, ui_shell):
    if hasattr(m, 'render_export_section'): m.render_export_section = cap_export
real_rc = ui_shell.render_chart
def cap_chart(fig, key, **k):
    figs.append((key, fig.to_json(), k.get('wide', False)))
for m in list(sys.modules.values()):
    if getattr(m, '__name__', '').startswith(('modules.', 'utils.')) and getattr(m, 'render_chart', None) is real_rc:
        m.render_chart = cap_chart
class _U: name = "uploaded_input_file.xlsx"
if mod in ("RATA","DA"):
    raw = pd.read_excel("example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx")
    fake = lambda *a, **k: _U()
    ui_shell.render_data_upload_section = fake
    core_data.load_data = lambda f: raw.copy()
    p = {"RATA":"rata","DA":"da"}[mod]
    at = _open_module({"RATA":"Rate-All-That-Apply","DA":"Descriptive Analysis"}[mod])
    at.selectbox(key=f"{p}_assessor").set_value("Panelist").run()
    at.selectbox(key=f"{p}_product").set_value("Product").run()
    at.selectbox(key=f"{p}_replicate").set_value("Session").run()
    at.number_input(key=f"{p}_scale_max").set_value(10).run()
    [b for b in at.button if b.key == f"{p}_run_analysis"][0].click().run(timeout=600)
elif mod == "CATA":
    raw = pd.read_excel("example_data/01_CATA/CATA_bread_Meyners2013.xlsx")
    ui_shell.render_data_upload_section = lambda *a, **k: _U(); c_ui.render_data_upload_section = lambda *a, **k: _U()
    core_data.load_data = lambda f: raw.copy()
    at = _open_module("Check-All-That-Apply"); p="cata"
    at.selectbox(key="cata_assessor_col").set_value("consumer").run()
    at.selectbox(key="cata_product_col").set_value("product").run()
    at.selectbox(key="cata_liking_col").set_value("liking").run()
    [b for b in at.button if b.key == "cata_run_analysis"][0].click().run(timeout=600)
elif mod == "Liking":
    raw = pd.read_excel("example_data/03_Liking/Liking_chocolates_hedochoc.xlsx")
    ui_shell.render_data_upload_section = lambda *a, **k: (_U() if k.get("widget_key")=="liking_upload_main" else None)
    core_data.load_data = lambda f: raw.copy()
    at = _open_module("Consumer Liking"); p="liking"
    at.selectbox(key="liking_consumer").set_value("consumer").run()
    at.selectbox(key="liking_product").set_value("product").run()
    at.selectbox(key="liking_liking").set_value("liking").run()
    [b for b in at.button if b.key == "liking_run_analysis"][0].click().run(timeout=600)
print("exc after run:", at.exception)
steps = MODULES[{"DA":"Descriptive"}.get(mod,mod)]["steps"]
for i, lab in enumerate(steps[1:], start=2):
    at.radio(key="sidebar_nav_step").set_value(lab).run(timeout=600)
    print("step", i, lab, "exc:", bool(at.exception), [str(e.value)[:120] for e in at.exception][:1])
if 'build' in captured:
    b = captured['build']()
    data = b.getvalue() if hasattr(b,'getvalue') else b
    open(f"{S}/export_{mod}.xlsx","wb").write(data); print("wrote export", len(data))
json.dump(figs, open(f"{S}/figs_{mod}.json","w"))
print("figs:", len(figs), [f[0] for f in figs][:40])
