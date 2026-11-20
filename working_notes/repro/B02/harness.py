import sys, os, warnings, logging, json, time, io
sys.path.insert(0, '/var/home/Lukas/Projects/RATA-Flow-App')
os.chdir('/var/home/Lukas/Projects/RATA-Flow-App')
warnings.filterwarnings('ignore')
logging.disable(logging.WARNING)
from pathlib import Path
from streamlit.testing.v1 import AppTest
from core import config as core_config
APP = '/var/home/Lukas/Projects/RATA-Flow-App/app.py'
MIME = {'.csv': 'text/csv', '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}

def new_app():
    return AppTest.from_file(APP, default_timeout=300).run()

def open_module(label):
    at = new_app()
    b = [b for b in at.button if label in b.label]
    b[0].click().run()
    return at

def upload(at, key, path=None, name=None, data=None):
    if data is None:
        data = Path(path).read_bytes(); name = name or Path(path).name
    at.file_uploader(key=key).set_value((name, data, MIME.get(Path(name).suffix, 'application/octet-stream'))).run()
    return at

def report(at, tag):
    out = []
    for e in at.exception:
        out.append(f"  EXCEPTION: {e.value[:300] if isinstance(e.value,str) else e.value} | {getattr(e,'message','')}")
        try: out.append('    ' + '\n    '.join(e.stack_trace[-6:]))
        except Exception: pass
    for e in at.error:
        out.append(f"  ERROR: {e.value[:600]}")
    for e in at.warning:
        out.append(f"  WARNING: {e.value[:300]}")
    print(f"[{tag}] exc={len(at.exception)} err={len(at.error)} warn={len(at.warning)} info={len(at.info)} charts={len(at.get('plotly_chart'))} dfs={len(at.dataframe)} step={at.session_state['current_step'] if 'current_step' in at.session_state else None}")
    for e in at.info: out.append(f"  INFO: {e.value[:200]}")
    for o in out: print(o)
    return out

def steps(mod):
    return core_config.MODULES[mod]['steps']

def go(at, mod, n):
    t = time.time()
    at.radio(key="sidebar_nav_step").set_value(steps(mod)[n-1]).run(timeout=600)
    return time.time() - t

def open_all_tabs_and_expanders(at, tag):
    """Open every gated tab/expander once (on_change=rerun) so their bodies render."""
    # AppTest has no tab-open API for on_change tabs in all versions; try
    pass

def force_open_all():
    from streamlit.elements.lib import mutable_expander_container as mec, mutable_tab_container as mtc
    mec.ExpanderContainer.open = property(lambda self: True, lambda self, v: None) if hasattr(mec,'ExpanderContainer') else None
    for name in dir(mec):
        obj = getattr(mec, name)
        if isinstance(obj, type) and 'open' in obj.__dict__:
            obj.open = property(lambda self: True, lambda self, v: None)
    for name in dir(mtc):
        obj = getattr(mtc, name)
        if isinstance(obj, type) and 'open' in obj.__dict__:
            obj.open = property(lambda self: True, lambda self, v: None)

def walk(at, mod, start=2, tag=''):
    res = {}
    for n in range(start, len(steps(mod))+1):
        dt = go(at, mod, n)
        print(f"--- {mod} step {n} '{steps(mod)[n-1]}' ({dt:.1f}s)")
        res[n] = report(at, f"{tag}{mod}-{n}")
    return res

EXPORTS = []
def patch_export():
    import utils.ui_shell as ui
    orig = ui.render_export_section
    def wrapped(build_workbook, module_name, *, key=None):
        import traceback
        try:
            b = build_workbook()
            data = b.getvalue() if hasattr(b, 'getvalue') else b
            import pandas as pd, io
            sheets = pd.ExcelFile(io.BytesIO(data)).sheet_names
            EXPORTS.append((module_name, len(data), sheets, None))
            print(f"  EXPORT {module_name}: {len(data)} bytes, sheets={sheets}")
        except Exception as e:
            EXPORTS.append((module_name, 0, [], traceback.format_exc()))
            print(f"  EXPORT FAILED {module_name}: {traceback.format_exc()[-1500:]}")
        return orig(build_workbook, module_name, key=key)
    ui.render_export_section = wrapped
patch_export()
