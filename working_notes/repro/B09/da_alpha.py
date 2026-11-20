import os,sys
sys.path.insert(0,'validation')
from _common import _stub_streamlit; _stub_streamlit()
sys.path.insert(0,'.')
import warnings; warnings.filterwarnings('ignore')
import pandas as pd
from core.data import clean_and_structure_data
from stats.da_anova import run_da_anova
raw=pd.read_excel('example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
cm={"assessor":"Panelist","product":"Product","replicate":"Session"}
df,_,_=clean_and_structure_data(raw,cm,scale_min=0,scale_max=10,module="Descriptive")
a,_=run_da_anova(df,cm,alpha=0.05,alpha_interaction=0.10)
b,_=run_da_anova(df,cm,alpha=0.05,alpha_interaction=0.0001)
m=a[['attribute','p_product','tested_against','p_interaction']].merge(b[['attribute','p_product','tested_against']],on='attribute',suffixes=('_a0.10','_a0.0001'))
print(m.to_string())
