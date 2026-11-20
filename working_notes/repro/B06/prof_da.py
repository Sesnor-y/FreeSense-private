import sys, os, warnings, logging, cProfile, pstats
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import streamlit as st, gen
from core import data as core_data
from stats import descriptive as sd, da_anova, panel_performance as pp, posthoc
raw = gen.da(20, 12, 30, 3)
CM = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
dl, _, _ = core_data.clean_and_structure_data(raw, CM, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False)
summ = sd.calculate_da_descriptives(dl, CM)
an, anf = da_anova.run_da_anova(dl, CM, 0.05, alpha_interaction=0.10)
print("sig attrs", (an.significant == "Yes").sum())
for name, call in [("cld", lambda: posthoc.generate_cld(dl, summ, an, CM, 0.05, "Tukey-Kramer HSD", anova_full_df=anf)),
                   ("rep", lambda: pp.compute_repeatability(dl, CM))]:
    pr = cProfile.Profile(); pr.enable(); call(); pr.disable()
    print("=====", name); pstats.Stats(pr).sort_stats("cumulative").print_stats(22)
