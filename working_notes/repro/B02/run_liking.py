import sys; sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from harness import *
import pandas as pd, io
force_open_all()
def liking(name, data, walk_all=True):
    print(f"\n######## Liking :: {name}")
    at = open_module("Consumer Liking")
    upload(at, 'liking_upload_main', name=name, data=data); report(at,'upload')
    for k,v in [('liking_consumer','consumer'),('liking_product','product'),('liking_liking','liking')]:
        at.selectbox(key=k).set_value(v).run()
    report(at,'mapped')
    print('  scale choice', at.segmented_control(key='liking_scale_choice').value if [s for s in at.get('button_group') if getattr(s,'key',None)=='liking_scale_choice'] else '?')
    run = [b for b in at.button if b.key == 'liking_run_analysis']
    if not run or run[0].disabled: print('  no/disabled run'); return at
    t=time.time(); run[0].click().run(timeout=900); print(f'  run {time.time()-t:.1f}s'); report(at,'ran')
    if walk_all: walk(at,'Liking')
    return at
h = pd.read_excel('example_data/03_Liking/Liking_chocolates_hedochoc.xlsx')
at = liking('hedochoc.xlsx', open('example_data/03_Liking/Liking_chocolates_hedochoc.xlsx','rb').read())
print('LS means (choc):'); print(at.session_state['liking_lmm_results']['lmm_summary'] if 'liking_lmm_results' in at.session_state else [k for k in at.session_state.to_dict() if k.startswith('liking_')])
h2 = h.copy(); h2['product'] = h2['product'].map({f'choc{i}': n for i,n in enumerate(['Variety A','Variety B','Covent','Plain','Dark','Milk'],1)})
b = io.StringIO(); h2.to_csv(b, index=False)
at = liking('variety.csv', b.getvalue().encode(), walk_all=False)
for k in at.session_state.to_dict():
    if k.startswith('liking_') and 'lmm' in k: print(k)
j = open('example_data/04_JAR/JAR_sensominer.xlsx','rb').read()
liking('JAR_sensominer.xlsx', j, walk_all=False)
