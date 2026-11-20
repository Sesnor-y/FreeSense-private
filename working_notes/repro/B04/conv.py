import sys, warnings; sys.path.insert(0,'.')
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from stats.liking import compute_liking_lmm
found=0
for seed in range(60):
    rng=np.random.default_rng(seed)
    n=12
    df=pd.DataFrame([(f"c{c}",f"P{p}",float(5+0.2*p+rng.normal(0,0.3))) for c in range(n) for p in range(4)],columns=['consumer','product','intensity'])
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            r=smf.mixedlm("intensity ~ C(product)",df,groups=df['consumer']).fit(reml=True,method='lbfgs')
    except Exception as e:
        continue
    names=[type(x.message).__name__ for x in w]
    if (not r.converged) or 'ConvergenceWarning' in names:
        res=compute_liking_lmm(df,{'consumer':'consumer','product':'product'},1,9)
        print(seed,'statsmodels converged=',r.converged,sorted(set(names)),'-> FreeSense convergence_warning=',res['convergence_warning'], res['anova_table'][['test','p_value']].values.tolist())
        found+=1
        if found>=3: break
print('found',found)
