import sys, os, time, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import gen, streamlit as st
from core import data as core_data
from stats import descriptive as sd, mixed_models as mm, posthoc
CM = {"assessor": "Panelist", "product": "Product", "replicate": None}
dl, _, _ = core_data.clean_and_structure_data(gen.rata(100, 8, 30), CM, 1, 5, [], module="RATA")
s = sd.calculate_descriptives(dl, CM)
t = time.perf_counter(); a, _ = mm.run_mixed_models(dl, CM, 0.05); print(f"LMM {time.perf_counter()-t:.1f}s")
for m in ("FDR (Benjamini-Hochberg)", "Tukey HSD", "Fisher LSD (Uncorrected)"):
    st.cache_data.clear(); t = time.perf_counter(); posthoc.generate_cld(dl, s, a, CM, 0.05, m); print(f"CLD {m}: {time.perf_counter()-t:.1f}s")
