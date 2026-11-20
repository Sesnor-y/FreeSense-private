import sys, logging; sys.path.insert(0, '.'); logging.disable(logging.WARNING)
import numpy as np, pandas as pd
import core.data as core_data, utils.ui_shell as ui_shell
from tests.test_apptest_smoke import _open_module
nr = int(sys.argv[1])
rng = np.random.default_rng(0)
raw = pd.DataFrame([{'Panelist': f'A{a}', 'Product': f'P{p}', 'Session': r+1,
                     **{f'T{t}': float(rng.integers(0, 11)) for t in range(5)}}
                    for a in range(10) for p in range(2) for r in range(nr)])
class _Upload: name = 'x.xlsx'
ui_shell.render_data_upload_section = lambda *a, **k: _Upload()
core_data.load_data = lambda _f: raw.copy()
from core.config import MODULES
at = _open_module(MODULES['Descriptive']['name'])
at.selectbox(key="da_assessor").set_value("Panelist").run()
at.selectbox(key="da_product").set_value("Product").run()
at.selectbox(key="da_replicate").set_value("Session").run()
at.button(key="da_run_analysis").click().run(timeout=300)
print(f'10x2x{nr}: exception:', [e.message for e in at.exception], '| da_analysis_complete:', at.session_state['da_analysis_complete'] if 'da_analysis_complete' in at.session_state else None)
