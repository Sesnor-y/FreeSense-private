import sys; sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from harness import *
import pandas as pd, io
force_open_all()
def cata(name, data, liking=True, walk_all=True):
    print(f"\n######## CATA :: {name}")
    at = open_module("Check-All-That-Apply")
    upload(at, 'cata_upload_main', name=name, data=data); report(at,'upload')
    at.selectbox(key="cata_assessor_col").set_value("consumer").run()
    at.selectbox(key="cata_product_col").set_value("product").run()
    report(at,'mapped')
    if liking:
        at.selectbox(key="cata_liking_col").set_value("liking").run(); report(at,'liking set')
    run = [b for b in at.button if b.key == 'cata_run_analysis']
    if not run or run[0].disabled: print('  no/disabled run'); return at
    t=time.time(); run[0].click().run(timeout=900); print(f'  run {time.time()-t:.1f}s'); report(at,'ran')
    if walk_all: walk(at,'CATA')
    return at
at = cata('bread.xlsx', open('example_data/01_CATA/CATA_bread_Meyners2013.xlsx','rb').read())
sq = open('example_data/01_CATA/CATA_squashes_emotions.xlsx','rb').read()
cata('squashes.xlsx', sq, liking=False, walk_all=False)
# bad: bread with a few '2' values and text 'yes'
b = pd.read_excel('example_data/01_CATA/CATA_bread_Meyners2013.xlsx')
attrs = [c for c in b.columns if c not in ('consumer','product','liking')]
b2 = b.copy().astype({attrs[0]: object}); b2.loc[[0,1], attrs[0]] = ['yes','x']
s = io.StringIO(); b2.to_csv(s, index=False); cata('bread_text.csv', s.getvalue().encode(), walk_all=False)
b3 = b.copy(); b3['product'] = b3['product'].map({'P1':'Käse','P2':'Crème brûlée','P3':'🍞 Rye','P4':'A+B:(x)','P5':'Variety','P6':'Cov'})
s = io.StringIO(); b3.to_csv(s, index=False); cata('bread_special.csv', s.getvalue().encode(), walk_all=True)
