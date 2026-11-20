import sys; sys.path.insert(0,'.')
import pandas as pd
from stats.liking import compute_liking_lmm
d=pd.read_excel('example_data/03_Liking/Liking_chocolates_hedochoc.xlsx')
d=d.rename(columns={'liking':'intensity'})
cm={'product':'product','consumer':'consumer'}
for ren in [None,{'choc1':'Variety A','choc2':'Variety B','choc3':'Covent','choc4':'Plain','choc5':'Dark','choc6':'Milk'}]:
    dd=d.copy()
    if ren: dd['product']=dd['product'].map(ren)
    r=compute_liking_lmm(dd,cm,0,10)
    s=r['lmm_summary'].copy(); s['raw']=s['product'].map(dd.groupby('product')['intensity'].mean())
    print(s)
