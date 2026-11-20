import sys; sys.path.insert(0,'/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B01')
from h import *
from stats.mixed_models import run_mixed_models
from stats.descriptive import calculate_descriptives, calculate_da_descriptives
from stats.posthoc import generate_pairwise_table, generate_cld
from stats.contrast import compute_contrast
from stats.da_anova import run_da_anova
raw = pd.read_excel(ROOT+'/example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
cm = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
def check(dl, mod, method, an, full, summ):
    pw = generate_pairwise_table(dl, summ, an, cm, 0.05, method, anova_full_df=full)
    tot=0; mism=[]
    prods=sorted(dl.Product.unique())
    for ref in prods:
        comps=[p for p in prods if p!=ref]
        c = compute_contrast(dl, cm, summ, an, full, ref, comps, 0.05, mod, method)
        sig_attrs=set(an[an.significant=='Yes'].attribute)
        for _,r in c.iterrows():
            if r.attribute not in sig_attrs: continue
            row=pw[(pw.Attribute==r.attribute)&(((pw['Product 1']==ref)&(pw['Product 2']==r.comparison))|((pw['Product 2']==ref)&(pw['Product 1']==r.comparison)))]
            if row.empty: continue
            tot+=1
            a=row['Reject H0'].iloc[0]=='True'; b=r.significant=='Yes'
            if a!=b: mism.append((r.attribute, ref, r.comparison, row['p-value (adj)'].iloc[0], r.p_value, a, b))
    print(mod, method, 'pairs', tot, 'mismatches', len(mism)); 
    for m in mism[:8]: print('  ',m)
# RATA
dl,_,_ = clean_and_structure_data(raw, cm, 0, 10, module='RATA')
an,_ = run_mixed_models(dl, cm, 0.05); summ = calculate_descriptives(dl, cm)
for m in ['Tukey HSD','FDR (Benjamini-Hochberg)','Fisher LSD (Uncorrected)']:
    check(dl,'RATA',m,an,None,summ)
# DA
dl2,_,_ = clean_and_structure_data(raw, cm, 0, 10, module='Descriptive')
s,f = run_da_anova(dl2, cm, 0.05, 0.10); summ2=calculate_da_descriptives(dl2, cm)
for m in ['Tukey-Kramer HSD','FDR (Benjamini-Hochberg)','Fisher LSD']:
    check(dl2,'Descriptive',m,s,f,summ2)
