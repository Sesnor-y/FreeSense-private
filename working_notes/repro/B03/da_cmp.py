import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,".")
import pandas as pd, numpy as np
from core.data import clean_and_structure_data
from modules.descriptive.workflow import run_full_da_analysis
raw = pd.read_excel("example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx")
trail = pd.concat([raw, pd.DataFrame([[np.nan]*raw.shape[1]]*2, columns=raw.columns)], ignore_index=True)
CM={"assessor":"Panelist","product":"Product","replicate":"Session"}
out={}
for nm,d in (("clean",raw),("trail",trail)):
    dl,_,_=clean_and_structure_data(d, CM, 0, 10, [], module="Descriptive")
    out[nm]=run_full_da_analysis(dl, CM, 0.05, "Tukey-Kramer HSD")
print(type(out['clean']), list(out['clean'].keys()) if isinstance(out['clean'],dict) else '')
for k in out['clean']:
    a,b=out['clean'][k],out['trail'][k]
    if isinstance(a,pd.DataFrame):
        bb=b
        for c in ('Product',):
            if c in b.columns: bb=b[b[c]!='nan']
        try:
            pd.testing.assert_frame_equal(a.reset_index(drop=True), bb.reset_index(drop=True), check_dtype=False, atol=1e-9)
            print(k,"equal after dropping nan product rows")
        except AssertionError as e: print(k,"DIFFERS:", str(e)[:300])
