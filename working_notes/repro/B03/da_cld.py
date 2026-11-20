import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,".")
import pandas as pd, numpy as np, itertools
from core.data import clean_and_structure_data
from modules.descriptive.workflow import run_full_da_analysis
raw = pd.read_excel("example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx")
trail = pd.concat([raw, pd.DataFrame([[np.nan]*raw.shape[1]]*2, columns=raw.columns)], ignore_index=True)
CM={"assessor":"Panelist","product":"Product","replicate":"Session"}
res={}
for nm,d in (("clean",raw),("trail",trail)):
    dl,_,_=clean_and_structure_data(d, CM, 0, 10, [], module="Descriptive")
    res[nm]=run_full_da_analysis(dl, CM, 0.05, "Tukey-Kramer HSD")['da_cld_df']
a,b=res['clean'],res['trail']
nchg=0
for attr in a.attribute.unique():
    ca=a[a.attribute==attr].set_index('Product').cld; cb=b[b.attribute==attr].set_index('Product').cld
    for p,q in itertools.combinations(sorted(ca.index),2):
        sa=bool(set(ca[p])&set(ca[q])); sb=bool(set(cb[p])&set(cb[q]))
        if sa!=sb: nchg+=1; print(attr,p,q,"clean share:",sa,"trail share:",sb, dict(ca), dict(cb))
print("grouping changes:", nchg)
print(b[b.Product=='nan'])
