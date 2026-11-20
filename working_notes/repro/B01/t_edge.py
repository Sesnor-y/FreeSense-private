import sys; sys.path.insert(0,'/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B01')
from h import *
from stats.mixed_models import run_mixed_models
from stats.da_anova import run_da_anova
from stats.descriptive import calculate_descriptives, calculate_da_descriptives
from stats.posthoc import generate_cld, generate_pairwise_table
rng=np.random.default_rng(5)
rows=[]
A=[f'a{i}' for i in range(3)]; Pp=['X','Y']
for a in A:
    for p in Pp:
        for r in (1,2):
            rows.append(dict(assessor=a,product=p,rep=r,
                allzero=0.0,
                oneuser=(float(rng.integers(1,10)) if a=='a0' else 0.0),
                const_per_assessor={'a0':2.0,'a1':5.0,'a2':7.0}[a],
                perfect={'X':3.0,'Y':6.0}[p],
                normal=float(rng.integers(0,10))))
w=pd.DataFrame(rows)
attrs=['allzero','oneuser','const_per_assessor','perfect','normal']
dl=w.melt(id_vars=['assessor','product','rep'],value_vars=attrs,var_name='attribute',value_name='intensity')
dl['binary']=(dl.intensity>0).astype(float)
cm={'assessor':'assessor','product':'product','replicate':'rep'}
an,_=run_mixed_models(dl,cm,0.05)
print(an[['attribute','lr_stat','p_value','significant','converged','status','optimiser_used']])
s,f=run_da_anova(dl,cm,0.05,0.10)
print(s[['attribute','F_product','p_product','significant','tested_against','status']])
summ=calculate_da_descriptives(dl,cm)
for m in ['Tukey-Kramer HSD','FDR (Benjamini-Hochberg)']:
    try:
        c=generate_cld(dl,summ,s,cm,0.05,m,anova_full_df=f); print(m); print(c)
        print(generate_pairwise_table(dl,summ,s,cm,0.05,m,anova_full_df=f)[['Attribute','p-value (adj)','Reject H0','Method']])
    except Exception as e: print('CLD error',m,type(e).__name__,e)
