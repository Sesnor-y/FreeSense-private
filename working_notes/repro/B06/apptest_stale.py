"""End-to-end: corrected re-upload of a CATA file (150 consumers x 8 products x 50 attributes)."""
import sys, os, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import gen, core.data as core_data, utils.ui_shell as ui_shell, modules.cata.ui as cata_ui
from tests.test_apptest_smoke import _open_module
from stats.shared.frequency import build_citation_matrix, run_cochrans_q
raw1 = gen.cata(150, 8, 50, seed=21, liking=False)
CM = {"assessor": "consumer", "product": "product", "replicate": None}
dl1, _, _ = core_data.clean_and_structure_data.__wrapped__(raw1, CM, 0, 1, [], module="CATA") if hasattr(core_data.clean_and_structure_data, "__wrapped__") else core_data.clean_and_structure_data(raw1, CM, 0, 1, [], module="CATA")
samp = set(dl1.sample(n=10_000, random_state=0).index)
attr, prod = "Attr003", "P02"
flip = dl1[(dl1.attribute == attr) & (dl1["product"] == prod) & (dl1.intensity == 0) & ~dl1.index.isin(samp)].head(25)
raw2 = raw1.copy()
for _, r in flip.iterrows():
    raw2.loc[(raw2.consumer == r.consumer) & (raw2["product"] == r["product"]), attr] = 1
print("long rows:", len(dl1), "| cells corrected:", len(flip))
class _Upload: name = "study.xlsx"
def _fake_section(*a, **k): return _Upload()
ui_shell.render_data_upload_section = _fake_section; cata_ui.render_data_upload_section = _fake_section
def session(raw):
    core_data.load_data = lambda _f: raw.copy()
    at = _open_module("Check-All-That-Apply")
    at.selectbox(key="cata_assessor_col").set_value("consumer").run()
    at.selectbox(key="cata_product_col").set_value("product").run()
    at.button(key="cata_run_analysis").click().run(timeout=600)
    assert not at.exception, at.exception
    return at
a1 = session(raw1)
a2 = session(raw2)   # user fixes the file and uploads it again (new browser session, same server)
ft = a2.session_state["cata_freq_table"]; q = a2.session_state["cata_cochrans_df"].set_index("attribute")
st_true = build_citation_matrix.__wrapped__ if hasattr(build_citation_matrix, "__wrapped__") else None
import streamlit as st; st.cache_data.clear()
dl2, _, _ = core_data.clean_and_structure_data(raw2, CM, 0, 1, [], module="CATA")
true_ft = build_citation_matrix(dl2, CM); true_q = run_cochrans_q(dl2, CM, 0.05).set_index("attribute")
print(f"raw data differ: {not raw1.equals(raw2)}")
print(f"{prod}/{attr} citation rate shown after corrected upload: {ft.loc[prod, attr]:.3f}; correct: {true_ft.loc[prod, attr]:.3f}")
print(f"Cochran's Q {attr} shown: {q.loc[attr, 'q_statistic']:.2f}; correct: {true_q.loc[attr, 'q_statistic']:.2f}")
