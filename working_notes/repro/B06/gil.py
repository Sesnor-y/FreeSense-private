import sys, os, time, warnings, logging, threading
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import gen
from core import data as core_data
from stats import da_anova, mixed_models
print("GIL enabled:", getattr(sys, "_is_gil_enabled", lambda: True)())
CM = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
dls = []
for seed in range(4):
    raw = gen.da(20, 12, 30, 3, seed=100 + seed)
    dl, _, _ = core_data.clean_and_structure_data(raw, CM, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False); dls.append(dl)
f = lambda dl: da_anova.run_da_anova.__wrapped__(dl, CM, 0.05, alpha_interaction=0.10) if hasattr(da_anova.run_da_anova, "__wrapped__") else da_anova.run_da_anova(dl, CM, 0.05, alpha_interaction=0.10)
import streamlit as st
t = time.perf_counter(); [f(d) for d in dls]; seq = time.perf_counter() - t
st.cache_data.clear()
t = time.perf_counter(); th = [threading.Thread(target=f, args=(d,)) for d in dls]; [x.start() for x in th]; [x.join() for x in th]; par = time.perf_counter() - t
print(f"4 x run_da_anova sequential {seq:.2f}s ; 4 threads concurrently {par:.2f}s (speed-up {seq/par:.2f}x)")
