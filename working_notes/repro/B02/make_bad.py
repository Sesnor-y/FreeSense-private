import pandas as pd, numpy as np, os
S = os.path.dirname(os.path.abspath(__file__)) + '/data/'
base = pd.read_excel('example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
attrs = [c for c in base.columns if c not in ('Panelist','Session','Product')]
print(base.head(3)); print(base.dtypes.value_counts())
# small subset for speed: 12 panelists, 4 products, 5 attributes
small = base[base.Panelist.isin(sorted(base.Panelist.unique())[:12]) & base.Product.isin(sorted(base.Product.unique())[:4])][['Panelist','Session','Product']+attrs[:5]].reset_index(drop=True)
small.to_csv(S+'small.csv', index=False)
# 1 European CSV: ; separator, decimal comma
eu = small.copy(); eu[attrs[:5]] = eu[attrs[:5]] + 0.5
eu.to_csv(S+'eu_semicolon.csv', sep=';', decimal=',', index=False)
# 2 comma sep but decimal comma (quoted)
eu.to_csv(S+'eu_comma_quoted.csv', sep=',', decimal=',', index=False)
# 3 text cells in an intensity column
t = small.copy().astype({attrs[0]: object}); t.loc[[0,5,9], attrs[0]] = ['n/a','high','5,5']; t.to_csv(S+'text_cells.csv', index=False)
# 4 extra text column not excluded
e = small.copy(); e['Comment'] = ['nice']*len(e); e['Date'] = '2026-01-01'; e.to_csv(S+'extra_cols.csv', index=False)
# 5 duplicated rows
pd.concat([small, small]).to_csv(S+'dup_rows.csv', index=False)
# 6 special product names
names = ['Käse', 'Crème brûlée', '🍫 Dark', 'A+B ~ x:y (new)']
m = dict(zip(sorted(small.Product.unique()), names))
sp = small.copy(); sp['Product'] = sp['Product'].map(m); sp['Panelist'] = 'Prüfer ' + sp['Panelist'].astype(str); sp.to_csv(S+'special_levels.csv', index=False)
sp.to_excel(S+'special_levels.xlsx', index=False)
# 7 weird attribute names
wa = small.copy()
newattr = ['Sweet+Sour', 'a ~ b', 'Bitter:after', '1st taste (x)', 'L'*220]
wa = wa.rename(columns=dict(zip(attrs[:5], newattr)))
wa.to_csv(S+'weird_attrs.csv', index=False)
# 8 colliding attribute names: 'Sweet' and 'Sweet ' and 'sweet'
co = small.copy(); co = co.rename(columns={attrs[0]:'Sweet', attrs[1]:'Sweet ', attrs[2]:'sweet'}); co.to_csv(S+'collide.csv', index=False)
# 9 numeric product codes and numeric assessors
nu = small.copy(); nu['Product'] = nu['Product'].map(dict(zip(sorted(small.Product.unique()), [101, 102, 205, 999]))); nu.to_csv(S+'numeric_codes.csv', index=False)
# 10 missing product column
small.drop(columns=['Product']).to_csv(S+'no_product.csv', index=False)
# 11 uppercase extension
import shutil; shutil.copy(S+'small.csv', S+'SMALL.CSV')
# 12 NaN in product column
na = small.copy(); na.loc[[0,1,2], 'Product'] = np.nan; na.to_csv(S+'nan_product.csv', index=False)
# 13 products "Variety A" etc (for DA/RATA too)
va = small.copy(); va['Product'] = va['Product'].map(dict(zip(sorted(small.Product.unique()), ['Variety A','Variety B','Covent','Plain']))); va.to_csv(S+'var_products.csv', index=False)
# 14 title row above header
with open(S+'title_row.csv','w') as f:
    f.write('Study XYZ export 2026\n'); small.to_csv(f, index=False)
# 15 latin-1 encoding with umlauts
sp.drop(columns=[]).assign(Product=sp['Product'].str.replace('🍫 ','')).to_csv(S+'latin1.csv', index=False, encoding='latin-1')
# 16 TSV named .csv
small.to_csv(S+'tab.csv', sep='\t', index=False)
print(attrs[:5])
