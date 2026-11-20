import sys, time, os, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import streamlit as st
import gen
from core import data as core_data
from stats import descriptive as sd, mixed_models as mm, posthoc, multivariate as mv
from stats.shared.frequency import compute_citation_disagreement
size = tuple(int(x) for x in sys.argv[1].split("x"))
raw = gen.rata(*size)
CM = {"assessor": "Panelist", "product": "Product", "replicate": None}
times = {}
def T(label, f, *a, **k):
    t = time.perf_counter(); r = f(*a, **k); dt = time.perf_counter() - t
    print(f"    {label}: {dt:.2f}s", flush=True); return r
st.cache_data.clear()
t0 = time.perf_counter()
dl, _, attrs = T("clean_and_structure", core_data.clean_and_structure_data, raw, CM, 1, 5, [], module="RATA")
summ = T("descriptives", sd.calculate_descriptives, dl, CM)
T("cochrans_q", sd.run_cochrans_q, dl, CM, 0.05)
T("citation_disagreement", compute_citation_disagreement, dl, CM)
an, diag = T("run_mixed_models", mm.run_mixed_models, dl, CM, 0.05)
T("generate_cld", posthoc.generate_cld, dl, summ, an, CM, 0.05, "Tukey-Kramer HSD")
print(f"  TOTAL step1: {time.perf_counter()-t0:.2f}s", flush=True)
sel = tuple(attrs)
T("[S6] calculate_pca", mv.calculate_pca, summ, sel, "Product", "Covariance")
T("[S6] run_cva", mv.run_cva, dl, sel, CM)
T("[S7] panel_stability", mv.calculate_panel_stability, dl, CM, reference_method="fixed")
print(f"RATA {size} rows={len(raw)} long={len(dl)} converged={an['converged'].mean():.2f}")
