import sys, io, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "validation"); sys.path.insert(0, ".")
from _common import _stub_streamlit
_stub_streamlit()
import pandas as pd, numpy as np, openpyxl
from core import data as cd
S=sys.argv[1]
class UF(io.BytesIO):
    def __init__(self, b, name): super().__init__(b); self.name = name
def tryit(label, f):
    try: r=f(); print("---",label,": OK", r)
    except Exception as e: print("---",label,": ERROR", str(e)[:250])
means = "Sample,Sweet,Bitter\nA,5.5,3.1\nB,4.2,2.2\nC,6.1,1.0\n"
b = means.encode("utf-8-sig")
tryit("means BOM via load_data cols", lambda: list(cd.load_data(UF(b,"m.csv")).columns))
tryit("means BOM load_precomputed_means(Sample)", lambda: cd.load_precomputed_means(UF(b,"m.csv"),"Sample")[0].shape)
tryit("means latin1 load_precomputed_means", lambda: cd.load_precomputed_means(UF("Sample,Süß\nA,1\nB,2\n".encode("latin-1"),"m.csv"),"Sample")[0].columns.tolist())
eu = "Sample,Sweet,Bitter,Sour\nA,\"5,5\",3,\"2,1\"\nB,4,\"2,2\",\"1,2\"\nC,6,1,\"3,3\"\n"
tryit("means decimal comma", lambda: (lambda r:(r[0].to_dict(), r[2].to_dict()))(cd.load_precomputed_means(UF(eu.encode(),"m.csv"),"Sample")))
tryit("means .CSV uppercase", lambda: cd.load_precomputed_means(UF(means.encode(),"M.CSV"),"Sample")[0].shape)
# multi-sheet xlsx
p=f"{S}/multi.xlsx"
with pd.ExcelWriter(p) as w:
    pd.DataFrame({"Info":["read me"]}).to_excel(w, sheet_name="Instructions", index=False)
    pd.DataFrame({"Panelist":["P1","P2"],"Sample":["A","B"],"Sweet":[1,2]}).to_excel(w, sheet_name="Data", index=False)
tryit("multi-sheet xlsx", lambda: list(cd.load_data(UF(open(p,'rb').read(),"multi.xlsx")).columns))
# xlsm
wb=openpyxl.Workbook(); ws=wb.active
for r in [["Panelist","Sample","Sweet"],["P1","A",1],["P2","B",2]]: ws.append(r)
wb.save(f"{S}/m.xlsx")
tryit("xlsm (xlsx bytes renamed)", lambda: list(cd.load_data(UF(open(f"{S}/m.xlsx",'rb').read(),"m.xlsm")).columns))
tryit("xls name, xlsx bytes", lambda: list(cd.load_data(UF(open(f"{S}/m.xlsx",'rb').read(),"m.xls")).columns))
# real BIFF xls header bytes
biff = bytes.fromhex("D0CF11E0A1B11AE1")+b"\0"*504
tryit("real xls (OLE2 header)", lambda: cd.load_data(UF(biff,"old.xls")))
# xlsx with trailing formatted empty rows and a title row
wb=openpyxl.Workbook(); ws=wb.active
ws.append(["Study X results"]); ws.append([])
for r in [["Panelist","Sample","Sweet"],["P1","A",1],["P2","B",2]]: ws.append(r)
wb.save(f"{S}/off.xlsx")
tryit("xlsx title row offset", lambda: cd.load_data(UF(open(f"{S}/off.xlsx",'rb').read(),"off.xlsx")).to_dict('list'))
wb=openpyxl.Workbook(); ws=wb.active
for r in [["Panelist","Sample","Sweet"],["P1","A",1],["P2","B",2]]: ws.append(r)
ws.cell(row=10,column=1).number_format="0.00"; ws.cell(row=10,column=1).value=None
ws.cell(row=8,column=5).value=" "
wb.save(f"{S}/trail.xlsx")
tryit("xlsx trailing whitespace cell", lambda: cd.load_data(UF(open(f"{S}/trail.xlsx",'rb').read(),"trail.xlsx")).to_dict('list'))
