import sys; sys.path.insert(0,'/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B01')
from h import *
from stats.liking import compute_liking_lmm, compute_liking_cld
from stats.contrast import compute_contrast
import scipy.stats as ss
cm={'product':'product','consumer':'consumer'}
def make(nc, npr, seed, eff):
    rng=np.random.default_rng(seed); rows=[]
    ce=rng.normal(0,1.2,nc)
    for c in range(nc):
        for p in range(npr):
            rows.append(dict(consumer=f'c{c}',product=f'P{p}',intensity=float(np.clip(np.round(5+eff[p]+ce[c]+rng.normal(0,1.3)),1,9))))
    return pd.DataFrame(rows)
tot_mis=0; tot=0
for seed in range(30):
    nc,npr=10,6
    d=make(nc,npr,seed,[0,0.4,0.8,1.2,1.6,2.0])
    L=compute_liking_lmm(d,cm,1,9,0.05)
    for meth in ['FDR (Benjamini-Hochberg)','Pairwise t-test (Uncorrected)','Tukey HSD (Studentized Range)']:
        cld=compute_liking_cld(L['lmm_summary'],L['cov_lsmeans'],L['df_satterthwaite'],0.05,meth)
        let=dict(zip(cld['product'],cld['cld_letter']))
        for ref in [f'P{p}' for p in range(npr)]:
            comps=[f'P{p}' for p in range(npr) if f'P{p}'!=ref]
            c=compute_contrast(d,cm,L['lmm_summary'],None,None,ref,comps,0.05,'Liking',meth,lmm_cov_params=L['cov_lsmeans'],df_satterthwaite=L['df_satterthwaite'])
            for _,r in c.iterrows():
                cld_sig = not (set(let[ref]) & set(let[r.comparison]))
                tot+=1
                if cld_sig != (r.significant=='Yes'): tot_mis+=1
print('df_satterthwaite used by contrast:', L['df_satterthwaite'])
print('contrast-vs-CLD disagreements', tot_mis, 'of', tot)
# independent reference: RCBD two-way ANOVA pairwise t with df=(nc-1)(np-1) on one dataset
d=make(10,6,3,[0,0.4,0.8,1.2,1.6,2.0])
L=compute_liking_lmm(d,cm,1,9,0.05)
import statsmodels.formula.api as smf
m=smf.ols('intensity ~ C(product)+C(consumer)',d).fit()
mse=m.mse_resid; dfr=m.df_resid
means=d.groupby('product').intensity.mean()
se=np.sqrt(2*mse/10)
cov=L['cov_lsmeans']
for a,b in [('P0','P1'),('P0','P3'),('P2','P5')]:
    sed=np.sqrt(cov.loc[a,a]+cov.loc[b,b]-2*cov.loc[a,b])
    t=(means[a]-means[b])/se
    print(a,b,'SE rcbd',round(se,4),'SE lmm',round(sed,4),'p rcbd(df=%d)'%dfr, ss.t.sf(abs(t),dfr)*2, 'p contrast(df=%g)'%L['df_satterthwaite'], ss.t.sf(abs(t),L['df_satterthwaite'])*2)
print('converged flag:', L['lmm_result'].converged, 'convergence_warning', L['convergence_warning'])
