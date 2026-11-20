import sys, logging; sys.path.insert(0,'.'); logging.disable(logging.WARNING)
import numpy as np, pandas as pd
from stats.segmentation import compute_ahc_clusters, compute_kmeans_clusters
for fn,std in [(compute_kmeans_clusters,False),(compute_ahc_clusters,True)]:
    counts=[]
    for s in range(20):
        r=np.random.default_rng(100+s)
        m=pd.DataFrame(np.clip(r.normal(6,1.5,(100,6)),1,9),index=[f'c{i}' for i in range(100)],columns=[f'P{j}' for j in range(6)])
        res=fn(m,2,standardise=std,alpha=0.05)
        a=[v for k,v in res.items() if isinstance(v,pd.DataFrame) and 'significant' in v.columns][0]
        counts.append(int(a['significant'].sum()))
    print(fn.__name__,'std' if std else 'raw',counts,'mean',np.mean(counts),'(expected 0.3)')
