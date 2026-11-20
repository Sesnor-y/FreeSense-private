import sys; sys.path.insert(0,'.')
import pandas as pd, numpy as np
from core.data import clean_and_structure_data
import inspect
raw=pd.read_excel('example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
raw=raw[raw['Session']==1].drop(columns=['Session','Rank'],errors='ignore')
print(raw.columns.tolist()[:6])
print(inspect.signature(clean_and_structure_data))
cm={'assessor':'Panelist','product':'Product'}
out=clean_and_structure_data(raw,cm,0,10,module='DA')
dl=out[0] if isinstance(out,tuple) else out
from stats.panel_performance import compute_discrimination
d=compute_discrimination(dl,cm)
print(d[['neg_log_p','range_score','score']].describe().T[['count','mean']])
from modules.descriptive.ui import plot_discrimination_heatmap
fig=plot_discrimination_heatmap(d,cm)
z=np.array(fig.data[0].z,dtype=float); print('heatmap z finite cells:',np.isfinite(z).sum(),'of',z.size)
