import sys, os, time, resource, warnings, logging, gc
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import gen, core.data as core_data, utils.ui_shell as ui_shell
from tests.test_apptest_smoke import _open_module
from core import config as core_config
class _Upload: name = "synthetic.xlsx"
ui_shell.render_data_upload_section = lambda *a, **k: _Upload()
def rss():
    return int(open("/proc/self/status").read().split("VmRSS:")[1].split()[0]) / 1024
keep = []
print(f"baseline RSS {rss():.0f} MB")
steps = core_config.MODULES["Descriptive"]["steps"]
for seed in range(6):
    raw = gen.da(20, 12, 30, 3, seed=50 + seed)
    core_data.load_data = lambda _f, raw=raw: raw.copy()
    at = _open_module("Descriptive Analysis")
    at.selectbox(key="da_assessor").set_value("Panelist").run(); at.selectbox(key="da_product").set_value("Product").run()
    at.selectbox(key="da_replicate").set_value("Session").run(); at.number_input(key="da_scale_max").set_value(10).run()
    t = time.perf_counter(); at.button(key="da_run_analysis").click().run(timeout=900); run_t = time.perf_counter() - t
    for s in steps[1:]: at.radio(key="sidebar_nav_step").set_value(s).run(timeout=900)
    keep.append(at); gc.collect()
    print(f"session {seed+1}: run {run_t:.1f}s, all steps visited, RSS {rss():.0f} MB", flush=True)
