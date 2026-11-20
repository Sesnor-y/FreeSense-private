import sys, io, warnings, types
warnings.filterwarnings("ignore")
sys.path.insert(0, "validation"); sys.path.insert(0, ".")
from _common import _stub_streamlit
_stub_streamlit()
import pandas as pd, numpy as np
from core import data as cd

class UF(io.BytesIO):
    def __init__(self, b, name): super().__init__(b); self.name = name

def show(label, b, name, mod=None):
    try:
        df = cd.load_data(UF(b, name))
        print(f"--- {label}: OK shape={df.shape} cols={list(df.columns)}")
        print(df.head(3).to_string()); print(df.dtypes.to_dict())
        return df
    except Exception as e:
        print(f"--- {label}: ERROR {str(e)[:200]}")

base = "Panelist,Sample,Süße,Crème,Bitterness\nP1,Brötchen,5.5,3,2\nP2,Brötchen,4,,1\nP3,Café,6,2.5,3\n"
show("utf8", base.encode("utf-8"), "a.csv")
show("utf8-bom", base.encode("utf-8-sig"), "a.csv")
show("latin1", base.encode("latin-1"), "a.csv")
show("cp1252", (base.replace("Crème","Crème–€")).encode("cp1252"), "a.csv")
show("utf16", base.encode("utf-16"), "a.csv")
eu = "Panelist;Sample;Sweet;Bitter\nP1;A;5,5;3\nP2;A;4;2,5\nP3;B;6,5;1\n"
show("semicolon+comma", eu.encode(), "a.csv")
eu2 = "Panelist,Sample,Sweet,Bitter\nP1,A,\"5,5\",3\nP2,A,4,\"2,5\"\nP3,B,\"6,5\",1\n"
df = show("comma-delim with quoted decimal comma", eu2.encode(), "a.csv")
show("tsv", base.replace(",","\t").encode(), "a.tsv")
show("tsv named .csv", base.replace(",","\t").encode(), "a.csv")
show("uppercase .CSV", base.encode(), "DATA.CSV")
show("trailing empties", (base.replace("\n",",,\n")+",,,,,,\n,,,,,,\n").encode(), "a.csv")
off = "FreeSense export 2026\nPanel study X\nPanelist,Sample,Sweet\nP1,A,5\nP2,B,6\n"
show("header offset", off.encode(), "a.csv")
show("dup headers + ws", "Panelist, Sample ,Sweet,Sweet\nP1,A,5,6\nP2,B,6,7\n".encode(), "a.csv")
