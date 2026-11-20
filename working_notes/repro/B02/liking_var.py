import warnings; warnings.filterwarnings('ignore')
import logging; logging.disable(logging.WARNING)
import pandas as pd
from stats.liking import compute_liking_lmm
df = pd.read_excel('example_data/03_Liking/Liking_chocolates_hedochoc.xlsx')
df = df.rename(columns={'liking':'intensity'})
cm = {'product':'product','consumer':'consumer'}
a = compute_liking_lmm(df, cm, 0, 10)['lmm_summary']
ren = {f'choc{i}': n for i,n in enumerate(['Variety A','Variety B','Covent','Plain','Dark','Milk'],1)}
df2 = df.copy(); df2['product'] = df2['product'].map(ren)
b = compute_liking_lmm(df2, cm, 0, 10)['lmm_summary']
print(a); print(b)
print(df2.groupby('product')['intensity'].mean())
