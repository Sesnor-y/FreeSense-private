import sys; sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from raw_driver import *
force_open_all()
mod = sys.argv[1]
files = sys.argv[2:]
D = sys.argv[0].rsplit('/',1)[0] + '/data/'
for f in files:
    data = open(D+f,'rb').read()
    kw = dict(assessor='Panelist', product='Product', replicate='Session')
    if f == 'no_product.csv': kw['product'] = 'Session'; kw['replicate']=None
    if f in ('eu_semicolon.csv','tab.csv','title_row.csv'):
        at = open_module(LABEL[mod]); upload(at, f"{PFX[mod]}_upload_main", name=f, data=data); report(at, f+' upload')
        print('  options:', at.selectbox(key=f"{PFX[mod]}_assessor").options if [s for s in at.selectbox if s.key==f"{PFX[mod]}_assessor"] else None)
        continue
    try:
        drive(mod, f, data, walk_steps=(f in sys.argv[2:3] or 'WALK' in os.environ), **kw)
    except Exception as e:
        import traceback; print('  HARNESS EXC', traceback.format_exc()[-800:])
