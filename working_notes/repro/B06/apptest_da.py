import sys, os, time, pickle, resource, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import pandas as pd, gen
import core.data as core_data, utils.ui_shell as ui_shell
from tests.test_apptest_smoke import _open_module
from core import config as core_config
size = tuple(int(x) for x in sys.argv[1].split("x"))
raw = gen.da(*size)
class _Upload: name = "synthetic.xlsx"
ui_shell.render_data_upload_section = lambda *a, **k: _Upload()
core_data.load_data = lambda _f: raw.copy()
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
def T(label, fn):
    t = time.perf_counter(); fn(); dt = time.perf_counter() - t
    print(f"  {label:55s} {dt:7.2f}s  maxRSS={rss():.0f} MB  exc={bool(at.exception)}", flush=True)
print("start maxRSS", f"{rss():.0f} MB")
at = _open_module("Descriptive Analysis")
T("map assessor", lambda: at.selectbox(key="da_assessor").set_value("Panelist").run())
T("map product", lambda: at.selectbox(key="da_product").set_value("Product").run())
T("map replicate", lambda: at.selectbox(key="da_replicate").set_value("Session").run())
if len(sys.argv) > 2: T("post-hoc Tukey", lambda: at.selectbox(key="da_post_hoc_method").set_value("Tukey-Kramer HSD").run())
T("set scale max", lambda: at.number_input(key="da_scale_max").set_value(10).run())
T("RUN FULL ANALYSIS (click + rerun)", lambda: at.button(key="da_run_analysis").click().run(timeout=1200))
steps = core_config.MODULES["Descriptive"]["steps"]
for s in steps[1:]:
    T(f"visit {s} (first)", lambda s=s: at.radio(key="sidebar_nav_step").set_value(s).run(timeout=1200))
    T(f"rerun {s} (no change)", lambda: at.run(timeout=1200))
# widget interaction on Step 5 (PCA standardisation toggle)
at.radio(key="sidebar_nav_step").set_value(steps[4]).run(timeout=1200)
T("S5 interaction: PCA type -> Correlation", lambda: at.segmented_control(key="da_pca_type").set_value("Correlation").run(timeout=1200))
T("S5 interaction: PCA type -> Covariance (cached)", lambda: at.segmented_control(key="da_pca_type").set_value("Covariance").run(timeout=1200))
ss = at.session_state.to_dict()
def _sz(v):
    try: return len(pickle.dumps(v, protocol=5))
    except Exception: return 0
sizes = sorted(((_sz(v), k) for k, v in ss.items() if not k.startswith("$$")), reverse=True)
print(f"session_state pickled total: {sum(s for s, _ in sizes)/1e6:.1f} MB over {len(sizes)} keys; top: " + ", ".join(f"{k}={s/1e6:.2f}MB" for s, k in sizes[:6]))
print("final maxRSS", f"{rss():.0f} MB")
