import sys, io, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")
import pandas as pd
from tests.test_apptest_smoke import _open_module
import core.data as core_data, utils.ui_shell as ui_shell
mode = sys.argv[1]
raw = pd.read_excel("example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx")
csv = raw.to_csv(index=False)
if mode == "trailing":
    csv += ","*(raw.shape[1]-1) + "\n" + ","*(raw.shape[1]-1) + "\n"
elif mode == "deccomma":
    # European export: 10% of CocoaA cells written with a decimal comma
    r = raw.copy().astype({"CocoaA": object})
    for i in range(0, len(r), 10): r.loc[i, "CocoaA"] = f"{r.loc[i,'CocoaA']},5" if r.loc[i,'CocoaA']<10 else r.loc[i,'CocoaA']
    csv = r.to_csv(index=False)
from streamlit.proto.Common_pb2 import FileURLs
from streamlit.runtime.uploaded_file_manager import UploadedFile, UploadedFileRec
def UF(b,n):
    return UploadedFile(UploadedFileRec(file_id=n,name=n,type="text/csv",data=b), FileURLs(file_id=n,upload_url="",delete_url=""))
real_load = core_data.load_data
df = real_load(UF(csv.encode(), "choc.csv"))
print("loaded", df.shape, df.tail(2).to_dict('records')[0] if mode=="trailing" else df.CocoaA.head(12).tolist())
class _U: name="choc.csv"
ui_shell.render_data_upload_section = lambda *a, **k: _U()
core_data.load_data = lambda f: df.copy()
module = sys.argv[2]
label = {"RATA":"Rate-All-That-Apply","DA":"Descriptive Analysis"}[module]
p = {"RATA":"rata","DA":"da"}[module]
at = _open_module(label)
at.selectbox(key=f"{p}_assessor").set_value("Panelist").run()
at.selectbox(key=f"{p}_product").set_value("Product").run()
at.selectbox(key=f"{p}_replicate").set_value("Session").run()
at.number_input(key=f"{p}_scale_max").set_value(10).run()
print("errors:", [e.value[:300] for e in at.error])
print("warnings:", [w.value[:300] for w in at.warning])
print("metrics:", [(m.label, m.value) for m in at.metric])
run = [b for b in at.button if b.key == f"{p}_run_analysis"]
if run:
    run[0].click().run(timeout=400)
    print("exc:", at.exception)
    dl = at.session_state[f"{p}_df_long"]
    print("products:", sorted(dl.Product.unique()))
    print("assessors n:", dl.Panelist.nunique(), "has 'nan':", 'nan' in set(dl.Panelist))
    if mode=="deccomma":
        sub = dl[dl.attribute=="CocoaA"]
        print("CocoaA intensity value counts head:", sub.intensity.value_counts(dropna=False).sort_index().to_dict())
    for k in (f"{p}_anova_df",):
        if k in at.session_state: 
            a = at.session_state[k]; print(a.head(3).to_string())
if run:
    d = at.session_state.to_dict()
    for k, v in d.items():
        if isinstance(v, pd.DataFrame):
            hit = ('nan' in set(map(str, v.index))) or any(('nan' in set(v[c].astype(str))) for c in v.columns if v[c].dtype==object) or ('nan' in set(map(str, v.columns)))
            if hit: print("NANPRODUCT in", k, v.shape)
    if mode=="trailing":
        for k in (f"{p}_summary_df", f"{p}_means_df", f"{p}_cld_df"):
            if k in d and isinstance(d[k], pd.DataFrame): print(k, "\n", d[k][d[k].astype(str).apply(lambda s: s.str.fullmatch('nan')).any(axis=1)].head(4).to_string()[:800])
