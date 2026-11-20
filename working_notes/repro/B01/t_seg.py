import sys; sys.path.insert(0,'/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B01')
from h import *
from stats.segmentation import compute_ahc_clusters, compute_kmeans_clusters
import inspect
print(inspect.signature(compute_ahc_clusters))
# Pure noise: 100 consumers x 6 products, iid N(6,1.5) rounded clipped 1-9, no segments
sig_counts=[]
for seed in range(20):
    rng=np.random.default_rng(seed)
    M=pd.DataFrame(np.clip(np.round(rng.normal(6,1.5,(100,6))),1,9), index=[f'c{i}' for i in range(100)], columns=[f'P{j}' for j in range(6)])
    r=compute_ahc_clusters(M, n_clusters=2, standardise=False, alpha=0.05)
    sig_counts.append(int(r['cluster_anova']['significant'].sum()))
print('AHC k=2 on pure noise: #products (of 6) flagged significant per dataset:', sig_counts)
sig_counts=[]
for seed in range(10):
    rng=np.random.default_rng(seed)
    M=pd.DataFrame(np.clip(np.round(rng.normal(6,1.5,(100,6))),1,9), index=[f'c{i}' for i in range(100)], columns=[f'P{j}' for j in range(6)])
    r=compute_kmeans_clusters(M, n_clusters=3, standardise=True, alpha=0.05)
    sig_counts.append(int(r['cluster_anova']['significant'].sum()))
print('kmeans k=3 std on pure noise:', sig_counts)
# constant rater with standardise
M.iloc[0,:]=7
for fn in (compute_ahc_clusters, compute_kmeans_clusters):
    try:
        r=fn(M, n_clusters=2, standardise=True, alpha=0.05); print(fn.__name__,'ok', r['cluster_labels'].value_counts().to_dict())
    except Exception as e: print(fn.__name__,'ERROR', type(e).__name__, e)
