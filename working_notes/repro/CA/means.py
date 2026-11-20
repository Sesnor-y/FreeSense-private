import sys, io, logging; sys.path.insert(0,'.'); logging.disable(logging.WARNING)
import pandas as pd, core.data as cd
d=pd.read_excel('example_data/05_Fusion_PrefMap/Cocktail_sensory_means.xlsx'); print(d.columns.tolist()[:5])
c1,c2=d.columns[1],d.columns[2]
d[c1]=d[c1].map(lambda v: f'{v:.2f}'.replace('.',','))          # all decimal comma
d[c2]=d[c2].astype(object); d.loc[:5,c2]=d.loc[:5,c2].map(lambda v: f'{v:.2f}'.replace('.',','))  # 6 of 16
b=io.BytesIO(); d.to_csv(b,index=False); b.seek(0); b.name='m.csv'
df,cm,na=getattr(cd.load_precomputed_means,'__wrapped__',cd.load_precomputed_means)(b,d.columns[0])
print(c1,df[c1].dtype, '| ',c2,df[c2].dtype,'NaN:',int(df[c2].isna().sum())); print('nan_affected',na.to_dict())
