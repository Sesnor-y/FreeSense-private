import sys, os, time, warnings, logging, traceback
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import gen, streamlit as st
from core import data as core_data
from modules.descriptive.workflow import run_full_da_analysis
from stats import mixed_models, descriptive as sd, posthoc
CM = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
def da_case(label, raw, cm=CM):
    st.cache_data.clear(); t = time.perf_counter()
    try:
        dl, _, _ = core_data.clean_and_structure_data(raw, cm, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False)
        r = run_full_da_analysis(dl, cm, 0.05, "FDR (Benjamini-Hochberg)", alpha_interaction=0.10)
        a = r["da_anova_df"]
        print(f"DA {label}: OK {time.perf_counter()-t:.1f}s; anova status={a['status'].value_counts().to_dict() if 'status' in a else '?'}")
    except Exception as e:
        print(f"DA {label}: EXCEPTION {type(e).__name__}: {e} ({time.perf_counter()-t:.1f}s) at {traceback.extract_tb(e.__traceback__)[-1][:3]}")
da_case("1 product", gen.da(10, 1, 5, 2))
da_case("2 products", gen.da(10, 2, 5, 2))
da_case("1 attribute", gen.da(10, 5, 1, 2))
da_case("1 assessor", gen.da(1, 5, 5, 2))
da_case("no replicates (col_map replicate None)", gen.da(10, 5, 5, 1).drop(columns="Session"), {"assessor": "Panelist", "product": "Product", "replicate": None})
raw = gen.da(5, 3, 1000, 2)
da_case("1000 attributes (5x3x2)", raw)
def rata_case(label, raw):
    cm = {"assessor": "Panelist", "product": "Product", "replicate": None}
    st.cache_data.clear(); t = time.perf_counter()
    try:
        dl, _, _ = core_data.clean_and_structure_data(raw, cm, 1, 5, [], module="RATA")
        s = sd.calculate_descriptives(dl, cm); sd.run_cochrans_q(dl, cm, 0.05)
        a, _ = mixed_models.run_mixed_models(dl, cm, 0.05); posthoc.generate_cld(dl, s, a, cm, 0.05, "FDR (Benjamini-Hochberg)")
        print(f"RATA {label}: OK {time.perf_counter()-t:.1f}s status={a['status'].value_counts().to_dict()}")
    except Exception as e:
        print(f"RATA {label}: EXCEPTION {type(e).__name__}: {e} at {traceback.extract_tb(e.__traceback__)[-1][:3]}")
rata_case("1 product", gen.rata(20, 1, 5))
rata_case("1 attribute", gen.rata(20, 4, 1))
