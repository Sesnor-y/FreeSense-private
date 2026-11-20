import sys, time, os, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import streamlit as st
import gen
from core import data as core_data
from stats import descriptive as sd, da_anova, panel_performance as pp, posthoc, multivariate as mv, contrast
size = tuple(int(x) for x in sys.argv[1].split("x")); reps = int(sys.argv[2])
raw = gen.da(*size)
CM = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
def T(label, f, *a, **k):
    t = time.perf_counter(); r = f(*a, **k); dt = time.perf_counter() - t
    times.setdefault(label, []).append(dt); return r
times = {}
for i in range(reps):
    st.cache_data.clear()
    t0 = time.perf_counter()
    dl, _, attrs = T("clean_and_structure", core_data.clean_and_structure_data, raw, CM, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False)
    summ = T("descriptives", sd.calculate_da_descriptives, dl, CM)
    T("attr_correlations", sd.calculate_attribute_correlations, summ, "Product")
    an, anf = T("run_da_anova", da_anova.run_da_anova, dl, CM, 0.05, alpha_interaction=0.10)
    T("discrimination", pp.compute_discrimination, dl, CM)
    rep = T("repeatability", pp.compute_repeatability, dl, CM)
    ag, rv = T("agreement", pp.compute_agreement, dl, CM)
    sc = T("scale_usage", pp.compute_scale_usage, dl, CM)
    T("generate_cld", posthoc.generate_cld, dl, summ, an, CM, 0.05, "Tukey-Kramer HSD", anova_full_df=anf)
    times.setdefault("TOTAL run_full_da_analysis (+clean)", []).append(time.perf_counter() - t0)
    # later-step computations
    sel = tuple(attrs)
    T("[S5] calculate_pca", mv.calculate_pca, summ, sel, "Product", "Correlation (standardised)")
    T("[S5] run_cva", mv.run_cva, dl, sel, CM)
    T("[S5] panel_stability fixed", mv.calculate_panel_stability, dl, CM, reference_method="fixed")
    T("[S7] compute_da_diagnostics", da_anova.compute_da_diagnostics, dl, CM)
    T("[S6] summarise_assessor_performance", pp.summarise_assessor_performance, dl, CM, rep, ag, rv, sc, an, 0.05)
t = time.perf_counter(); dl2, _, _ = core_data.clean_and_structure_data(raw, CM, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False); da_anova.run_da_anova(dl2, CM, 0.05, alpha_interaction=0.10)
times["cache-hit clean+anova"] = [time.perf_counter() - t]
print(f"DA {size} rows={len(raw)} long={len(dl)}")
for k, v in times.items():
    print(f"  {k:42s} " + " / ".join(f"{x:7.2f}" for x in v))
