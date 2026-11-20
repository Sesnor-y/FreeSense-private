import sys, os, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import streamlit as st, gen
from core import data as core_data
from stats.shared.frequency import run_cochrans_q, build_citation_matrix
CM = {"assessor": "consumer", "product": "product", "replicate": None}
raw1 = gen.cata(100, 10, 50, seed=7, liking=False)   # 1,000 rows wide -> 50,000 long
dl1, _, _ = core_data.clean_and_structure_data(raw1, CM, 0, 1, [], module="CATA")
print("long rows", len(dl1))
samp = set(dl1.sample(n=10_000, random_state=0).index)
# flip 20 ticks of one attribute for one product, all outside the hash sample
attr = "Attr003"; prod = "P02"
cand = dl1[(dl1.attribute == attr) & (dl1["product"] == prod) & (dl1.intensity == 0) & ~dl1.index.isin(samp)]
flip = cand.head(20)
raw2 = raw1.copy()
for _, r in flip.iterrows():
    raw2.loc[(raw2.consumer == r.consumer) & (raw2["product"] == r["product"]), attr] = 1
dl2, _, _ = core_data.clean_and_structure_data(raw2, CM, 0, 1, [], module="CATA")
print("df_long differs:", not dl1.equals(dl2), "same shape:", dl1.shape == dl2.shape)
m1 = build_citation_matrix(dl1, CM); q1 = run_cochrans_q(dl1, CM, 0.05)
m2 = build_citation_matrix(dl2, CM); q2 = run_cochrans_q(dl2, CM, 0.05)
st.cache_data.clear()
m2t = build_citation_matrix(dl2, CM); q2t = run_cochrans_q(dl2, CM, 0.05)
print(f"{prod}/{attr} citation rate  cached={m2.loc[prod, attr]:.2f} true={m2t.loc[prod, attr]:.2f}")
a = q2.set_index("attribute").loc[attr]; b = q2t.set_index("attribute").loc[attr]
print(f"Cochran Q {attr}: cached Q={a.q_statistic:.3f} p={a.p_value:.4g}  true Q={b.q_statistic:.3f} p={b.p_value:.4g}")
