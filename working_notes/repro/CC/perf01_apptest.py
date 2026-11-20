import sys, logging; sys.path.insert(0, '.')
logging.disable(logging.WARNING)
import numpy as np, pandas as pd
import streamlit as st
from streamlit.runtime.caching.hashing import _PANDAS_SAMPLE_SIZE
import core.data as core_data, utils.ui_shell as ui_shell, modules.cata.ui as cata_ui
from tests.test_apptest_smoke import _open_module

nc, npd, na = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rng = np.random.default_rng(1)
rows = [{'consumer': f'C{c:03d}', 'product': f'P{p:02d}', **{f'Attr{a:03d}': int(rng.random() < 0.3) for a in range(na)}}
        for c in range(nc) for p in range(npd)]
wide = pd.DataFrame(rows)
nlong = len(wide) * na
sampled = set(pd.RangeIndex(nlong).to_series().sample(n=_PANDAS_SAMPLE_SIZE, random_state=0)) if nlong >= 50000 else set(range(nlong))
wide2 = wide.copy(); flipped = 0
for wr in wide2.index[wide2['product'] == 'P02']:
    if 3 * len(wide) + wr not in sampled and wide2.at[wr, 'Attr003'] == 0 and flipped < 25:
        wide2.at[wr, 'Attr003'] = 1; flipped += 1
CUR = {'df': wide}
class _Upload: name = 'study.xlsx'
def _fake_section(*a, **k):
    st.button("Re-upload", key="fake_reupload", on_click=k.get("on_change"))
    return _Upload()
ui_shell.render_data_upload_section = _fake_section
cata_ui.render_data_upload_section = _fake_section
core_data.load_data = lambda _f: CUR['df'].copy()

def run(at):
    at.selectbox(key="cata_assessor_col").set_value("consumer").run()
    at.selectbox(key="cata_product_col").set_value("product").run()
    b = [b for b in at.button if b.key == "cata_run_analysis"][0]
    b.click().run(timeout=600)
    assert not at.exception, at.exception
    ft = at.session_state['cata_freq_table_full'] if 'cata_freq_table_full' in at.session_state else at.session_state['cata_freq_table']
    q = at.session_state['cata_cochrans_df'].set_index('attribute')
    return ft.loc['P02', 'Attr003'], q.loc['Attr003', ['q_statistic', 'p_value']].tolist()

at = _open_module("Check-All-That-Apply")
print('long rows', nlong, 'flipped', flipped)
print('first upload        ', run(at))
CUR["df"] = wide2
at.session_state["current_step"] = 1; at.run()
at.button(key="fake_reupload").click().run()        # real _reset_cata_upload on_change
print('analysis_complete after re-upload reset:', at.session_state['analysis_complete'])
print('corrected upload (same session, app shows)', run(at))
st.cache_data.clear()
at2 = _open_module("Check-All-That-Apply")
print('corrected upload after cache clear (truth)', run(at2))
