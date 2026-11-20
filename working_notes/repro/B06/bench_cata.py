import sys, time, os, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import streamlit as st, gen
from core import data as core_data
from modules.cata.ui import _run_full_cata_pipeline
from stats.cata import cached_compute_ca, compute_ca_ellipses, cached_compute_penalty, cached_run_cata_contrast
size = tuple(int(x) for x in sys.argv[1].split("x"))
raw = gen.cata(*size)
attrs = [c for c in raw.columns if c.startswith("Attr")]
CM = {"assessor": "consumer", "product": "product", "replicate": None}
def T(label, f, *a, **k):
    t = time.perf_counter(); r = f(*a, **k); dt = time.perf_counter() - t
    print(f"    {label}: {dt:.2f}s", flush=True); return r
st.cache_data.clear(); t0 = time.perf_counter()
dl, _, _ = T("clean_and_structure", core_data.clean_and_structure_data, raw.drop(columns="liking"), CM, 0, 1, [], module="CATA")
res = T("_run_full_cata_pipeline", _run_full_cata_pipeline, dl, CM, 0.20, "any_product", 0.05, "FDR (Benjamini-Hochberg)")
lk, lcm = T("build_cata_liking_long", core_data.build_cata_liking_long, raw, "consumer", "product", "liking")
print(f"  TOTAL step1: {time.perf_counter()-t0:.2f}s", flush=True)
kept = tuple(res["cata_kept_attributes"]); prods = sorted(dl["product"].unique())
T("[S5] cata contrast", cached_run_cata_contrast, dl, CM, res["cata_freq_table"], kept, prods[0], tuple(prods[1:]))
T("[S6] compute_ca", cached_compute_ca, res["cata_count_table"], biplot_type="asymmetric")
T("[S6] compute_ca_ellipses", compute_ca_ellipses, df_long=dl, col_map=CM, kept_attributes=kept)
T("[S6] ellipses other dims (bootstrap cached)", compute_ca_ellipses, df_long=dl, col_map=CM, kept_attributes=kept, x_dim=0, y_dim=2)
T("[S7] penalty", cached_compute_penalty, dl, CM, lk, lcm, kept, res["cata_freq_table"])
print(f"CATA {size} rows={len(raw)} long={len(dl)} kept={len(kept)}")
