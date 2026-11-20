import sys; sys.path.insert(0,'/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B01')
from h import *
from stats.da_anova import run_da_anova
import scipy.stats as ss
raw, dl, cm = choc()
def dummies(s):
    return pd.get_dummies(s.astype(str), drop_first=True, dtype=float).to_numpy()
def rss(y, *blocks):
    X = np.column_stack([np.ones(len(y))]+[b for b in blocks])
    b,_,rk,_ = np.linalg.lstsq(X,y,rcond=None); r=y-X@b
    return float(r@r), len(y)-np.linalg.matrix_rank(X)
def indep(sub, rep=True):
    y=sub.intensity.to_numpy(float); P=dummies(sub.Product); A=dummies(sub.Panelist)
    PA = pd.get_dummies(sub.Product.astype(str)+'|'+sub.Panelist.astype(str), dtype=float).to_numpy()
    r_full, df_full = rss(y, PA) if rep else rss(y,P,A)
    r_add, df_add = rss(y,P,A); r_A,dfA = rss(y,A); r_P,dfP=rss(y,P)
    ssP = r_A - r_add; dfp = dfA-df_add
    out={}
    mse=r_full/df_full
    if rep:
        ssI = r_add-r_full; dfi=df_add-df_full; msi=ssI/dfi
        pI = ss.f.sf(msi/mse, dfi, df_full)
        den,dden = (msi,dfi) if pI<0.10 else (mse,df_full)
    else:
        pI=np.nan; den,dden=mse,df_full
    F=(ssP/dfp)/den
    return dict(F=F,p=ss.f.sf(F,dfp,dden),pI=pI,dfe=dden)
s,f = run_da_anova(dl, cm, 0.05, 0.10)
rows=[]
for a in dl.attribute.unique():
    r=indep(dl[dl.attribute==a]); fs=s[s.attribute==a].iloc[0]
    rows.append((a, r['F'], fs.F_product, r['p'], fs.p_product, r['pI'], fs.p_interaction, r['dfe'], fs.df_error_term))
print(pd.DataFrame(rows, columns=['attr','F_ind','F_fs','p_ind','p_fs','pI_ind','pI_fs','dfe_ind','dfe_fs']).to_string())
# Empty cells: drop all obs for 3 random assessor x product cells
rng=np.random.default_rng(1)
d2=dl.copy()
cells=[('1','choc1'),('5','choc3'),('12','choc6'),('20','choc2')]
d2['Panelist']=d2.Panelist.astype(str)
for a_,p_ in cells: d2=d2[~((d2.Panelist==a_)&(d2.Product==p_))]
s2,f2=run_da_anova(d2, cm, 0.05, 0.10)
rows=[]
for a in d2.attribute.unique():
    r=indep(d2[d2.attribute==a]); fs=s2[s2.attribute==a].iloc[0]
    rows.append((a, r['F'], fs.F_product, r['p'], fs.p_product, r['pI'], fs.p_interaction, r['dfe'], fs.df_error_term, fs.ss_type))
print(pd.DataFrame(rows, columns=['attr','F_ind','F_fs','p_ind','p_fs','pI_ind','pI_fs','dfe_ind','dfe_fs','ss']).to_string())
# no replicate path with empty cells: use session 1 only
d3 = d2[d2.Session.astype(str)=='1']
cm3={'assessor':'Panelist','product':'Product','replicate':None}
s3,f3=run_da_anova(d3, cm3, 0.05, 0.10)
rows=[]
for a in d3.attribute.unique():
    r=indep(d3[d3.attribute==a], rep=False); fs=s3[s3.attribute==a].iloc[0]
    rows.append((a, r['F'], fs.F_product, r['p'], fs.p_product, r['dfe'], fs.df_error_term, fs.ss_type))
print(pd.DataFrame(rows, columns=['attr','F_ind','F_fs','p_ind','p_fs','dfe_ind','dfe_fs','ss']).to_string())
