import sys; sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from harness import *
import pandas as pd, io
force_open_all()
E='example_data/05_Fusion_PrefMap/'
at = open_module("Preference Mapping")
report(at,'open')
print('radios', [(r.key, r.options) for r in at.radio])
at.radio(key="prefmap_sensory_radio").set_value("Upload pre-computed sensory means (CSV/xlsx)").run()
upload(at, 'prefmap_upload_sensory', E+'Cocktail_sensory_means.xlsx')
report(at,'sensory uploaded')
print('prod col', at.selectbox(key='prefmap_upload_product_col').value)
at.radio(key="prefmap_consumer_radio").set_value("Upload raw consumer liking scores").run()
upload(at, 'prefmap_upload_liking', E+'Cocktail_consumer_liking.xlsx')
report(at,'long liking uploaded (shipped file)')
# wide version
ll = pd.read_excel(E+'Cocktail_consumer_liking.xlsx')
w = ll.pivot(index='product', columns='consumer', values='liking').reset_index()
w.columns = ['product'] + [f'C{c}' for c in w.columns[1:]]
b = io.BytesIO(); w.to_excel(b, index=False)
upload(at, 'prefmap_upload_liking', name='wide.xlsx', data=b.getvalue())
report(at,'wide liking uploaded')
walk(at, 'PrefMap')
fit = [x for x in at.button if 'Fit' in x.label]
print('fit buttons', [x.label for x in fit])
go(at,'PrefMap',2)
fit = [x for x in at.button if 'Fit' in x.label]
if fit:
    fit[0].click().run(timeout=600); report(at,'fitted')
walk(at, 'PrefMap', start=2, tag='post-fit ')
