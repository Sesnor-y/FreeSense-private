import sys; sys.path.insert(0,'/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B01')
from h import *
from stats.da_anova import run_da_anova
from stats.posthoc import generate_cld, generate_pairwise_table
from stats.descriptive import calculate_da_descriptives
import scipy.stats as ss
raw, dl, cm = choc()
# Unbalanced replicates, complete cells: drop session-2 rows for a few cells
d=dl.copy(); d['Panelist']=d.Panelist.astype(str); d['Session']=d.Session.astype(str)
drop=[('1','choc1'),('5','choc3'),('12','choc6'),('20','choc2'),('3','choc2'),('7','choc5')]
for a_,p_ in drop: d=d[~((d.Panelist==a_)&(d.Product==p_)&(d.Session=='2'))]
def sumcode(s):
    lv=sorted(s.astype(str).unique()); M=np.zeros((len(s),len(lv)-1))
    v=s.astype(str).to_numpy()
    for j,l in enumerate(lv[:-1]): M[:,j]=(v==l)
    M[v==lv[-1],:]=-1; return M
def rssX(y,X):
    b=np.linalg.lstsq(X,y,rcond=None)[0]; r=y-X@b; return r@r, len(y)-np.linalg.matrix_rank(X)
s,f=run_da_anova(d,cm,0.05,0.10)
out=[]
for a in d.attribute.unique():
    sub=d[d.attribute==a]; y=sub.intensity.to_numpy(float)
    P=sumcode(sub.Product); A=sumcode(sub.Panelist)
    PA=np.column_stack([P[:,i]*A[:,j] for i in range(P.shape[1]) for j in range(A.shape[1])])
    one=np.ones((len(y),1))
    rf,dff=rssX(y,np.hstack([one,P,A,PA])); rnoP,_=rssX(y,np.hstack([one,A,PA]))
    rnoI,_=rssX(y,np.hstack([one,P,A]))
    ssP=rnoP-rf; ssI=rnoI-rf; dfp=P.shape[1]; dfi=PA.shape[1]
    mse=rf/dff; msi=ssI/dfi; pI=ss.f.sf(msi/mse,dfi,dff)
    den,dd=(msi,dfi) if pI<0.1 else (mse,dff)
    F=ssP/dfp/den
    r=s[s.attribute==a].iloc[0]
    out.append((a,F,r.F_product,ss.f.sf(F,dfp,dd),r.p_product,pI,r.p_interaction,r.ss_type))
print(pd.DataFrame(out,columns=['a','F_ind','F_fs','p_ind','p_fs','pI_ind','pI_fs','ss']).to_string())
# single replicate but replicate col mapped
d1=dl[dl.Session.astype(str)=='1']
s1,f1=run_da_anova(d1,cm,0.05,0.10)
print(s1[['attribute','F_product','p_product','significant','tested_against','status','df_error_term']].head(4))
