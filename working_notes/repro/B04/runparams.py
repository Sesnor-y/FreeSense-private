import io, sys, types
sys.path.insert(0,'.')
import pandas as pd
from utils import export as ex
class F: name='panel_DA_2025.csv'
for mod in ('Fusion','PrefMap'):
    buf=io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as w:
        ex.build_run_parameters_sheet(w, mod, {'uploaded_file':F()}, '1.0.0')
    buf.seek(0); df=pd.read_excel(buf, sheet_name='Run_Parameters')
    print(mod, df[df.iloc[:,0]=='data_source_file'].values.tolist())
