"""Drive DA or RATA Step 1 with an arbitrary file; optionally run + walk."""
import sys; sys.path.insert(0, sys.argv[0].rsplit('/',1)[0])
from harness import *
import pandas as pd

LABEL = {'Descriptive': 'Descriptive Analysis', 'RATA': 'Rate-All-That-Apply'}
PFX = {'Descriptive': 'da', 'RATA': 'rata'}

def drive(mod, name, data, assessor, product, replicate=None, scale=(0,10), exclude=(), walk_steps=True, extra=None):
    p = PFX[mod]
    print(f"\n########## {mod} :: {name}")
    at = open_module(LABEL[mod])
    upload(at, f'{p}_upload_main', name=name, data=data)
    report(at, 'upload')
    if at.exception or not [s for s in at.selectbox if s.key == f'{p}_assessor']:
        print('  -> no mapping widgets'); return at
    opts = at.selectbox(key=f'{p}_assessor').options
    print('  options:', opts[:12])
    at.selectbox(key=f'{p}_assessor').set_value(assessor).run()
    at.selectbox(key=f'{p}_product').set_value(product).run()
    if replicate: at.selectbox(key=f'{p}_replicate').set_value(replicate).run()
    at.number_input(key=f'{p}_scale_min').set_value(scale[0]).run()
    at.number_input(key=f'{p}_scale_max').set_value(scale[1]).run()
    if exclude: at.multiselect(key=f'{p}_exclude_cols').set_value(list(exclude)).run()
    if extra: extra(at)
    report(at, 'mapped')
    for m in at.metric: print(f"  metric {m.label}={m.value}")
    btn = [b for b in at.button if b.key == f'{p}_run_analysis']
    if not btn:
        print('  -> no run button'); return at
    t=time.time(); btn[0].click().run(timeout=900); print(f'  run {time.time()-t:.1f}s')
    report(at, 'ran')
    if walk_steps and at.session_state[f'{p}_analysis_complete'] if f'{p}_analysis_complete' in at.session_state else False:
        walk(at, mod)
    return at
