import sys, logging; sys.path.insert(0,'.'); logging.disable(logging.WARNING)
import pandas as pd, numpy as np
import core.data as cd, stats.descriptive as sd, stats.mixed_models as mm, stats.posthoc as ph
from stats.contrast import compute_contrast
raw=pd.read_excel('example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
cm={'assessor':'Panelist','product':'Product','replicate':'Session'}
dl,_,attrs=cd.clean_and_structure_data(raw,cm,0,10,[],module='RATA')
summ=sd.calculate_descriptives(dl,cm); an,_=mm.run_mixed_models(dl,cm,0.05)
for meth in ['Tukey HSD','FDR (Benjamini-Hochberg)','Fisher LSD (Uncorrected)']:
    pw=ph.generate_pairwise_table(dl,summ,an,cm,0.05,meth)
    lut={}
    for _,r in pw.iterrows(): lut[(r.Attribute,frozenset((r['Product 1'],r['Product 2'])))]=(r['Reject H0']=='True',r['p-value (adj)'])
    prods=sorted(dl['Product'].unique()); mism=[]; tot=0
    for ref in prods:
        c=compute_contrast(dl,cm,summ,anova_df=an,reference_product=ref,comparison_products=[p for p in prods if p!=ref],alpha=0.05,module='RATA',post_hoc_method=meth)
        for _,r in c.iterrows():
            k=(r.attribute,frozenset((ref,r.comparison)))
            if k not in lut: continue
            tot+=1
            if (r.significant=='Yes')!=lut[k][0]: mism.append((r.attribute,ref,r.comparison,r.significant,lut[k]))
    print(meth,'pairs',tot,'mismatches',len(mism)); [print('  ',m) for m in mism[:6]]
