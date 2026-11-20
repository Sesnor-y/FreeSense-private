import pandas as pd, numpy as np, csv
S='/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/CA/files/'
d=pd.read_excel('example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
print(d.dtypes.value_counts()); print(d.iloc[:,3:].stack().apply(lambda v: float(v).is_integer()).mean())
d.to_csv(S+'clean.csv',index=False)
# all decimal comma (values +0.5 so they all have decimals), comma-delimited, quoted
e=d.copy(); attrs=d.columns[3:]
for c in attrs: e[c]=(d[c].clip(upper=9.5)+0.5).map(lambda v: f'{v}'.replace('.',','))
e.to_csv(S+'eu_comma_all.csv',index=False,quoting=csv.QUOTE_NONNUMERIC)
# partial: 35 CocoaA cells as decimal comma
p=d.copy().astype({'CocoaA':object}); idx=p.index[:35]; p.loc[idx,'CocoaA']=[f'{v},5' for v in d.loc[idx,'CocoaA'].clip(upper=9)]
p.to_csv(S+'eu_comma_35.csv',index=False)
d.to_csv(S+'semicolon.csv',index=False,sep=';')
d.to_csv(S+'tab.csv',index=False,sep='\t')
l=d.copy(); l['Product']=l['Product'].str.replace('choc','Schokolade für ',regex=False); l.to_csv(S+'latin1.csv',index=False,encoding='latin-1')
pd.concat([d,d]).to_csv(S+'dup.csv',index=False)
n=d.copy(); n.loc[[5,50,100],'Product']=np.nan; n.to_csv(S+'nanprod.csv',index=False)
with open(S+'clean.csv') as f: t=f.read()
open(S+'trailing.csv','w').write(t+','*16+'\n'+','*16+'\n')
open(S+'UPPER.CSV','w').write(t)
