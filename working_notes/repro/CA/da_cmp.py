import sys, logging, warnings; sys.path.insert(0,'.'); logging.disable(logging.WARNING); warnings.simplefilter('ignore')
import pandas as pd, numpy as np
from core.data import clean_and_structure_data
from modules.descriptive.workflow import run_full_da_analysis
from stats.posthoc import generate_pairwise_table
F='/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/CA/files/'
CM={'assessor':'Panelist','product':'Product','replicate':'Session'}
def run(fn):
    raw=pd.read_csv(F+fn); dl,_,_=clean_and_structure_data(raw,CM,0,10,[],module='Descriptive')
    r=run_full_da_analysis(dl,CM,0.05,'FDR (Benjamini-Hochberg)',alpha_interaction=0.10)
    pw=generate_pairwise_table(dl,r['da_summary_df'],r['da_anova_df'],CM,0.05,'FDR (Benjamini-Hochberg)',anova_full_df=r['da_anova_full_df'])
    return r,pw
base,bpw=run('clean.csv')
print(base['da_anova_df'].columns.tolist())
cols=[c for c in ['attribute','F_product','p_product','df_error','tested_against','p_interaction','ss_type'] if c in base['da_anova_df'].columns]
for fn in ['dup.csv','nanprod.csv','trailing.csv']:
    r,pw=run(fn)
    a=base['da_anova_df'].set_index('attribute')[cols[1:]]; b=r['da_anova_df'].set_index('attribute')[cols[1:]]
    print('=====',fn); print(pd.concat({'clean':a.loc[['MilkF','Bitterness','Sweetness']],'test':b.loc[['MilkF','Bitterness','Sweetness']]},axis=1).T)
    m=bpw.merge(pw,on=['Attribute','Product 1','Product 2'],how='inner',suffixes=('_c','_t'))
    ch=m[m['Reject H0_c']!=m['Reject H0_t']]
    print(' pairwise verdict changes among real products:',len(ch),'of',len(m)); print(ch[['Attribute','Product 1','Product 2','p-value (adj)_c','p-value (adj)_t']].to_string()[:800])
    print(' sig attrs clean vs test:', (base['da_anova_df'].significant=='Yes').sum(), (r['da_anova_df'].significant=='Yes').sum())
