import sys, logging; sys.path.insert(0,'.'); logging.disable(logging.WARNING)
import numpy as np, pandas as pd
from stats.segmentation import compute_ahc_clusters
r=np.random.default_rng(1); m=pd.DataFrame(np.round(r.normal(6,1.5,(50,6))).clip(1,9)); m.iloc[0]=7
try: compute_ahc_clusters(m,2,standardise=True)
except Exception as e: print('straight-liner + standardise ->',type(e).__name__,e)
