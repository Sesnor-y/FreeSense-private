import sys, logging, warnings; sys.path.insert(0,'.'); logging.disable(logging.WARNING); warnings.simplefilter('ignore')
import pandas as pd, numpy as np
from core.data import clean_and_structure_data
from modules.descriptive.workflow import run_full_da_analysis
F='/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/CA/files/'
CM={'assessor':'Panelist','product':'Product','replicate':'Session'}
def run(fn,m):
    raw=pd.read_csv(F+fn); dl,_,_=clean_and_structure_data(raw,CM,0,10,[],module='Descriptive')
    return run_full_da_analysis(dl,CM,0.05,m,alpha_interaction=0.10)
for m in ['FDR (Benjamini-Hochberg)','Tukey-Kramer HSD','Fisher LSD (Uncorrected)']:
    a=run('clean.csv',m); b=run('trailing.csv',m)
    ca=a['da_cld_df']; cb=b['da_cld_df']
    if m.startswith('FDR'): print(ca.columns.tolist()); print(cb[cb.Product=='nan'].head(3))
    pc=[c for c in ca.columns if c.lower().startswith('cld')][0]
    def verdicts(c):
        out={}
        for at,g in c[c.Product!='nan'].groupby('attribute'):
            L=g.set_index('Product')[pc]
            ps=sorted(L.index)
            for i in range(len(ps)):
                for j in range(i+1,len(ps)): out[(at,ps[i],ps[j])]=not(set(str(L[ps[i]]))&set(str(L[ps[j]])))
        return out
    va,vb=verdicts(ca),verdicts(cb)
    diff=[k for k in va if va[k]!=vb.get(k)]
    print(m,'CLD verdict changes:',len(diff),diff[:5])
    for key in ['da_agree_df','da_scale_df','da_rv_df']:
        if key in a: 
            try: same=a[key].equals(b[key])
            except Exception: same='?'
            print('  ',key,'identical' if same is True else 'DIFFERENT', getattr(b[key],'shape',None), getattr(a[key],'shape',None))
