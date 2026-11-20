import sys, warnings, logging; warnings.filterwarnings('ignore'); logging.disable(logging.WARNING)
sys.path.insert(0,'.')
import pandas as pd
from core.data import clean_and_structure_data
from stats.da_anova import run_da_anova
D = sys.argv[1]
cm = {'assessor':'Panelist','product':'Product','replicate':'Session'}
na = pd.read_csv(D+'nan_product.csv')
dl,_,_ = clean_and_structure_data(na, cm, 0, 10, [], module='Descriptive')
print('nan_product products in df_long:', sorted(dl['Product'].unique()))
s = pd.read_csv(D+'small.csv'); d = pd.read_csv(D+'dup_rows.csv')
for name, df in [('small', s), ('dup', d)]:
    dl,_,_ = clean_and_structure_data(df, cm, 0, 10, [], module='Descriptive')
    a,_ = run_da_anova(dl, cm, 0.05)
    print(name, list(a.columns)); print(a.head(5).to_string())
e = pd.read_csv(D+'extra_cols.csv')
dl,_,_ = clean_and_structure_data(e, cm, 0, 10, [], module='Descriptive')
a,_ = run_da_anova(dl, cm, 0.05)
print(a.to_string()[:2500])
