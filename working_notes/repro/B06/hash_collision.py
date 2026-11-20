"""Does st.cache_data return a stale result for a corrected upload of the same shape?"""
import sys, os, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import numpy as np, streamlit as st, gen
from core import data as core_data
from stats import descriptive as sd
CM = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
raw1 = gen.da(30, 10, 60, 3, seed=11)        # 900 rows wide, 54,000 rows long
dl1, _, _ = core_data.clean_and_structure_data(raw1, CM, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False)
print("long rows", len(dl1))
sample_idx = set(dl1.sample(n=10_000, random_state=0).index)
# pick a long-format row outside the hash sample; find the wide cell that produced it
row = next(i for i in dl1.index if i not in sample_idx)
r = dl1.loc[row]; print("cell outside sample:", r[["Panelist","Product","Session","attribute","intensity"]].to_dict())
raw2 = raw1.copy()
m = (raw2.Panelist == r.Panelist) & (raw2.Product == r.Product) & (raw2.Session.astype(str) == str(r.Session))
raw2.loc[m, r.attribute] = 0.0 if r.intensity > 5 else 10.0   # "corrected" value
dl2, _, _ = core_data.clean_and_structure_data(raw2, CM, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False)
print("clean_and_structure recomputed (raw hashed fully):", not dl1.equals(dl2))
s1 = sd.calculate_da_descriptives(dl1, CM)
s2 = sd.calculate_da_descriptives(dl2, CM)          # cache lookup
st.cache_data.clear()
s2_true = sd.calculate_da_descriptives(dl2, CM)
key = (s1.Product == r.Product) & (s1.attribute == r.attribute)
col = "mean_intensity" if "mean_intensity" in s1 else [c for c in s1.columns if "mean" in c][0]
print("mean after correction, served from cache :", float(s2.loc[key, col].iloc[0]))
print("mean after correction, true               :", float(s2_true.loc[key, col].iloc[0]))
print("stale result served:", s2.equals(s1) and not s2_true.equals(s1))
