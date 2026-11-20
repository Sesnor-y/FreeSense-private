import sys, time, os, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import streamlit as st, gen
from stats.liking import compute_liking_lmm, compute_liking_cld, compute_demographic_overview, compute_twoway_anova_demo
from stats.segmentation import compute_ahc_clusters, compute_kmeans_clusters, compute_demographic_association
from stats.jar_penalty import compute_jar_penalty, compute_jar_penalty_long, compute_jar_distribution
from stats.mdpref import compute_preference_map
from stats.contrast import cached_compute_contrast
n_cons, n_prod, n_jar = (int(x) for x in sys.argv[1].split("x"))
df, demo = gen.liking(n_cons, n_prod, n_jar)
CM = {"consumer": "consumer", "product": "product", "liking": "liking"}
jars = [c for c in df.columns if c.startswith("JAR")]
jcm = {c: {"too_low": 1, "jar": 3, "too_high": 5, "scale_points": 5} for c in jars}
def T(label, f, *a, **k):
    t = time.perf_counter(); r = f(*a, **k); dt = time.perf_counter() - t
    print(f"    {label}: {dt:.2f}s", flush=True); return r
st.cache_data.clear(); t0 = time.perf_counter()
dl = df.rename(columns={"liking": "intensity"}).astype({"consumer": str, "product": str})
lmm = T("compute_liking_lmm", compute_liking_lmm, dl, CM, 1, 9, 0.05)
cld = T("compute_liking_cld (Tukey)", compute_liking_cld, lmm["lmm_summary"], lmm["cov_lsmeans"], lmm["df_satterthwaite"], alpha=0.05, post_hoc_method="Tukey HSD (Studentized Range)")
print(f"  TOTAL step1: {time.perf_counter()-t0:.2f}s", flush=True)
T("[S3] demographic_overview", compute_demographic_overview, demo, CM, ["gender", "age_group", "usage"])
T("[S3] twoway_anova_demo (3 vars, LMM each)", compute_twoway_anova_demo, dl, demo, CM, ["gender", "age_group", "usage"], alpha=0.05, min_cell_n=5)
prods = sorted(dl["product"].unique())
try:
    T("[S4] contrast", cached_compute_contrast, df_long=dl, col_map=CM, summary_df=lmm["lmm_summary"], anova_df=None, anova_full_df=None,
      reference_product=prods[0], comparison_products=tuple(prods[1:]), alpha=0.05, module="Liking", post_hoc_method="Tukey HSD (Studentized Range)",
      lmm_cov_params=lmm["cov_lsmeans"])
except Exception as e: print("    contrast failed:", type(e).__name__, e)
mat = dl.pivot_table(index="consumer", columns="product", values="intensity")
ahc = T("[S5] AHC (k=3)", compute_ahc_clusters, mat, 3, False)
km = T("[S5] k-means (k=3, n_init=50)", compute_kmeans_clusters, mat, 3, False)
labels = km.get("labels", km.get("cluster_labels"))
if labels is not None:
    try: T("[S5] demographic_association", compute_demographic_association, labels, demo.set_index("consumer"), "usage")
    except Exception as e: print("    assoc failed", type(e).__name__, e)
t = time.perf_counter()
compute_jar_penalty(df_long=dl, jar_col_map=jcm, liking_col="intensity", alpha=0.05, penalty_threshold=0.5, min_pct_nojar=0.2, scale_min=1, scale_max=9)
compute_jar_distribution(dl, jcm)
for p in prods:
    dp = dl[dl["product"] == p]; compute_jar_distribution(dp, jcm)
    compute_jar_penalty_long(df_long=dp, jar_col_map=jcm, liking_col="intensity", alpha=0.05, scale_min=1, scale_max=9)
print(f"    [S6] JAR block (uncached, runs every Step 6 rerun): {time.perf_counter()-t:.2f}s")
T("[S7] MDPREF", compute_preference_map, liking_wide=mat.T, standardise_consumers=True, n_components=2)
print(f"LIKING cons={n_cons} prod={n_prod} jar={n_jar} rows={len(df)}")
