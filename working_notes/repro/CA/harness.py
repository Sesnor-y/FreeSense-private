import sys, io, logging, warnings
sys.path.insert(0,'/var/home/Lukas/Projects/RATA-Flow-App'); logging.disable(logging.WARNING); warnings.simplefilter('ignore')
from unittest import mock
import pandas as pd
import core.data as cd, utils.ui_shell as ui
from tests.test_apptest_smoke import _open_module
F='/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/CA/files/'
REAL=getattr(cd.load_data,'__wrapped__',cd.load_data)
LABEL={'da':'Descriptive Analysis','rata':'Rate-All-That-Apply'}
def texts(at):
    out=[]
    for kind in ('error','warning','info','exception'):
        for e in getattr(at,kind):
            v=getattr(e,'value',None) or getattr(e,'message','')
            out.append(f'[{kind}] '+str(v)[:220].replace('\n',' '))
    return out
def drive(prefix, fn, run=True, cm=('Panelist','Product','Session')):
    class U(io.BytesIO): pass
    def mk():
        u=U(open(F+fn,'rb').read()); u.name=fn; return u
    with mock.patch.object(ui,'render_data_upload_section',lambda *a,**k: mk()), \
         mock.patch.object(cd,'load_data',lambda f: REAL(mk())):
        at=_open_module(LABEL[prefix])
        try:
            for k,v in zip(('assessor','product','replicate'),cm):
                at.selectbox(key=f'{prefix}_{k}').set_value(v).run()
            at.number_input(key=f'{prefix}_scale_max').set_value(10).run()
        except Exception as e:
            print('  mapping failed:',type(e).__name__,str(e)[:200])
            opts=[s.options for s in at.selectbox if s.key and s.key.startswith(prefix)]
            print('  selectbox options:',opts[:2]); print('  msgs:',texts(at)); return at
        print('  metrics:',[(m.label,m.value) for m in at.metric])
        print('  step1 msgs:',texts(at))
        if run:
            b=[x for x in at.button if x.key==f'{prefix}_run_analysis']
            if not b: print('  no run button'); return at
            b[0].click().run(timeout=600)
            print('  after run msgs:',texts(at))
        return at
