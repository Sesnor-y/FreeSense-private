import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, statsmodels.formula.api as smf, statsmodels.api as sm
from stats import da_anova
f=getattr(da_anova.run_da_anova,'__wrapped__',da_anova.run_da_anova)
rng=np.random.default_rng(5); rows=[]
for a in range(8):
  for p,pe in zip('ABCD',[5,5.5,6,7]):
    nrep = 1 if (a+ord(p))%3==0 else 3   # unequal replication, no empty cells
    ie=rng.normal(0,0.8)
    for r in range(nrep):
      rows.append(dict(Assessor=f'J{a}',Product=p,Rep=r+1,attribute='X',intensity=pe+a*0.3+ie+rng.normal(0,0.5)))
d=pd.DataFrame(rows); d['binary']=1.0
CM={'assessor':'Assessor','product':'Product','replicate':'Rep'}
res,full=f(d,CM,0.05,alpha_interaction=0.10)
print(res[['F_product','p_product','tested_against','ss_type','df_error_term']].to_string())
m=smf.ols('intensity ~ C(Product,Sum)*C(Assessor,Sum)',data=d).fit()
t=sm.stats.anova_lm(m,typ=3); print(t)
ms=lambda k:t.loc[k,'sum_sq']/t.loc[k,'df']
print('F vs resid',ms('C(Product, Sum)')/ms('Residual'),'F vs int',ms('C(Product, Sum)')/ms('C(Product, Sum):C(Assessor, Sum)'))
