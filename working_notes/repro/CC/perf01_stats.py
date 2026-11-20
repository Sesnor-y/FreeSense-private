import sys, numpy as np, pandas as pd, logging
sys.path.insert(0, '.')
logging.disable(logging.WARNING)
from core.data import clean_and_structure_data
from stats.shared.frequency import build_citation_matrix, run_cochrans_q
from streamlit.runtime.caching.hashing import _PANDAS_SAMPLE_SIZE

def make_wide(nc, npd, na, seed=1):
    rng = np.random.default_rng(seed)
    rows = []
    for c in range(nc):
        for p in range(npd):
            rows.append({'Consumer': f'C{c:03d}', 'Product': f'P{p:02d}',
                         **{f'Attr{a:03d}': int(rng.random() < 0.3) for a in range(na)}})
    return pd.DataFrame(rows)

nc, npd, na = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
wide = make_wide(nc, npd, na)
cm = {'assessor': 'Consumer', 'product': 'Product', 'replicate': None}
cm_call = {'assessor': 'Consumer', 'product': 'Product'}
long1, *_ = clean_and_structure_data(wide, cm_call, 0, 1, module='CATA')
print('long rows', len(long1))
m1 = build_citation_matrix(long1, cm)
q1 = run_cochrans_q(long1, cm, 0.05)
# which long rows are sampled?
sampled = set(long1.sample(n=_PANDAS_SAMPLE_SIZE, random_state=0).index) if len(long1) >= 50000 else set(long1.index)
# long row index = attr_idx * (nc*npd) + wide_row ; flip Attr003 for P02 rows not sampled
wide2 = wide.copy()
a = 3; flipped = 0
for wr in wide2.index[wide2.Product == 'P02']:
    li = a * len(wide) + wr
    if li not in sampled and wide2.at[wr, 'Attr003'] == 0 and flipped < 20:
        wide2.at[wr, 'Attr003'] = 1; flipped += 1
print('flipped cells', flipped, 'raw differ', not wide.equals(wide2))
long2, *_ = clean_and_structure_data(wide2, cm_call, 0, 1, module='CATA')
print('long differ', not long1.equals(long2))
m2 = build_citation_matrix(long2, cm)
q2 = run_cochrans_q(long2, cm, 0.05)

import streamlit as st; st.cache_data.clear()
m2t = build_citation_matrix(long2, cm); q2t = run_cochrans_q(long2, cm, 0.05)
print('P02/Attr003 before', round(m1.loc['P02','Attr003'],3), 'cached after', round(m2.loc['P02','Attr003'],3), 'true after', round(m2t.loc['P02','Attr003'],3))
f = lambda q: q.set_index('attribute').loc['Attr003', ['q_statistic','p_value']].tolist()
print('Q Attr003 cached', f(q2), 'true', f(q2t))
