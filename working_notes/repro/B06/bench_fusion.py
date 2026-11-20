import sys, time, os, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import numpy as np, pandas as pd, streamlit as st, gen
from stats.pls import fit_pls, compute_cv_coefficient_stability
from stats.data_fusion import autoscale
from stats.multivariate import compute_pca_scores
from stats.prefmap import compute_prefmap, compute_preference_surface
n_prod, n_sens, n_cons = (int(x) for x in sys.argv[1].split("x")); nperm = int(sys.argv[2])
sens, ext, long, wide = gen.fusion(n_prod, n_sens, n_cons)
def T(label, f, *a, **k):
    t = time.perf_counter(); r = f(*a, **k); dt = time.perf_counter() - t
    print(f"    {label}: {dt:.2f}s", flush=True); return r
X, _, _ = autoscale(sens.iloc[:, 1:].to_numpy(float))
for yname, Yraw in [("Y=external(8)", ext.iloc[:, 1:].to_numpy(float)), (f"Y=consumers({n_cons})", wide.iloc[:, 1:].to_numpy(float))]:
    st.cache_data.clear()
    Y, ym, ys = autoscale(Yraw)
    Y = np.nan_to_num(Y)
    for cv in ("loo", "kfold_5"):
        r = T(f"fit_pls {yname} {cv} perm={nperm}", fit_pls, X, Y, 3, cv, run_permutation_test=True, n_permutations=nperm, y_mean=ym, y_std=ys)
        T(f"coef_stability {yname} {cv}", compute_cv_coefficient_stability, X, Y, r["n_components"], cv)
# PrefMap
st.cache_data.clear()
pca = compute_pca_scores(sens.iloc[:, 1:].to_numpy(float), standardise=True, n_components=2)
sc = pca["scores"] if isinstance(pca, dict) else pca[0]
coords = pd.DataFrame(np.asarray(sc)[:, :2], columns=["PC1", "PC2"], index=sens["product"])
lw = wide.set_index("product")
res = T(f"compute_prefmap ({n_cons} consumers)", compute_prefmap, coords, lw)
T("compute_preference_surface grid 50", compute_preference_surface, coords, lw, res)
print(f"FUSION prod={n_prod} sens={n_sens} cons={n_cons}")
