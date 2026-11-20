import sys, math, logging; sys.path.insert(0,'.'); logging.disable(logging.WARNING)
import numpy as np, pandas as pd, scipy.stats as ss
from stats.liking import compute_liking_lmm, compute_liking_cld
from stats.contrast import compute_contrast
import statsmodels.formula.api as smf
cm={'product':'product','consumer':'consumer'}
methods=['FDR (Benjamini-Hochberg)','Tukey HSD (Studentized Range)','Pairwise t-test (Uncorrected)']
def sim(seed,nc=10,npd=6):
    r=np.random.default_rng(seed); eff=r.normal(0,0.6,npd); u=r.normal(0,1,nc)
    rows=[(f'c{i}',f'P{j+1}',6+eff[j]+u[i]+r.normal(0,1.2)) for i in range(nc) for j in range(npd)]
    return pd.DataFrame(rows,columns=['consumer','product','intensity'])
dis=tot=0; first=True
for seed in range(15):
    d=sim(seed,nc=int(sys.argv[1])); L=compute_liking_lmm(d,cm,1,9)
    # RCBD OLS
    o=smf.ols('intensity~C(product)+C(consumer)',d).fit()
    if first:
        print('contrast df',L['df_satterthwaite'],' RCBD resid df',o.df_resid)
        se_rc=math.sqrt(2*o.scale/int(sys.argv[1])); cov=L['cov_lsmeans']; se_l=math.sqrt(cov.loc['P2','P2']+cov.loc['P5','P5']-2*cov.loc['P2','P5'])
        print('SE diff LMM',se_l,'RCBD',se_rc)
    pooled=math.sqrt(L['lmm_result'].scale)
    for m in methods:
        cld=compute_liking_cld(L['lmm_summary'],L['cov_lsmeans'],L['df_satterthwaite'],0.05,m).set_index('product')['cld_letter']
        for ref in cld.index:
            comps=[p for p in cld.index if p!=ref]
            c=compute_contrast(d,cm,L['lmm_summary'],reference_product=ref,comparison_products=comps,alpha=0.05,module='Liking',post_hoc_method=m,lmm_cov_params=L['cov_lsmeans'],df_satterthwaite=L['df_satterthwaite'],liking_pooled_sd=pooled)
            if first: print(c.columns.tolist()); first=False
            for _,row in c.iterrows():
                cs=(row['significant']=='Yes'); cl= not (set(cld[ref])&set(cld[row['comparison']]))
                tot+=1; dis+= cs!=cl
import collections
print('disagree',dis,'of',tot)
print('done')
