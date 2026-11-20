import sys, traceback, logging; sys.path.insert(0, '.')
logging.disable(logging.WARNING)
import numpy as np, pandas as pd
import stats.panel_performance as pp
from core.data import clean_and_structure_data
from modules.descriptive.workflow import run_full_da_analysis
if len(sys.argv) > 1 and sys.argv[1] == 'nopg':
    pp.PINGOUIN_AVAILABLE = False
def design(na, np_, nr, nattr, drop=None, seed=0):
    rng = np.random.default_rng(seed); rows = []
    for a in range(na):
        for p in range(np_):
            for r in range(nr):
                if drop and (a, p) in drop: continue
                rows.append({'Assessor': f'A{a}', 'Product': f'P{p}', 'Session': r + 1,
                             **{f'T{t}': float(rng.integers(0, 11)) for t in range(nattr)}})
    return pd.DataFrame(rows)
cm = {'assessor': 'Assessor', 'product': 'Product', 'replicate': 'Session'}
cases = {'10x2prod x2rep': design(10, 2, 2, 5), '10x2prod x3rep': design(10, 2, 3, 5),
         '30x2prod x2rep': design(30, 2, 2, 5), '12x3prod x2rep, A0 missed P1': design(12, 3, 2, 5, drop={(0, 1)}),
         '12x3prod x2rep balanced': design(12, 3, 2, 5),
         '12x4prod x2rep, A0 missed P1': design(12, 4, 2, 5, drop={(0, 1)})}
for name, wide in cases.items():
    long, *_ = clean_and_structure_data(wide, cm, 0, 10, module='Descriptive')
    try:
        run_full_da_analysis(long, cm); print(f'{name}: OK')
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        own = [f for f in tb if 'RATA-Flow-App' in f.filename and '/env/' not in f.filename][-1]
        print(f'{name}: {type(e).__name__}: {e}  @ {own.filename.split("RATA-Flow-App/")[1]}:{own.lineno}  (raised in {tb[-1].filename.split("site-packages/")[-1]}:{tb[-1].lineno})')
