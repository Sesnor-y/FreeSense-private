import sys, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "/var/home/Lukas/Projects/RATA-Flow-App")
import numpy as np, pandas as pd, statsmodels.formula.api as smf, statsmodels.api as sm
from stats import da_anova
rng=np.random.default_rng(7); rows=[]
for a in range(8):
    for p in range(4):
        for r in range(1 if (a+p)%2 else 3):
            rows.append(dict(A=f"a{a}",P=f"p{p}",R=r+1,attribute="x",intensity=5+0.8*p+rng.normal(0,1)+0.3*a+rng.normal(0,.7)*(p==a%4)))
d=pd.DataFrame(rows); d["binary"]=(d.intensity>0).astype(float)
CM={"assessor":"A","product":"P","replicate":"R"}
f=da_anova.run_da_anova; f=getattr(f,"__wrapped__",f)
a,full=f(d,CM,0.05,alpha_interaction=0.99)
print(a.T.to_string())
m=smf.ols("intensity ~ C(P,Sum)*C(A,Sum)",d).fit(); t=sm.stats.anova_lm(m,typ=3)
print(t)
print("F_P/PxA", (t.loc["C(P, Sum)","sum_sq"]/t.loc["C(P, Sum)","df"])/(t.loc["C(P, Sum):C(A, Sum)","sum_sq"]/t.loc["C(P, Sum):C(A, Sum)","df"]))
print(repr(a.iloc[0]["p_product"]), repr(a.iloc[0]["F_product"]))
