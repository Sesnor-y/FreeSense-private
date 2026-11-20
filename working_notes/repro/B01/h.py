import sys, os, warnings
sys.path.insert(0, '/var/home/Lukas/Projects/RATA-Flow-App/validation')
sys.path.insert(0, '/var/home/Lukas/Projects/RATA-Flow-App')
os.chdir('/var/home/Lukas/Projects/RATA-Flow-App')
from _common import _stub_streamlit
_stub_streamlit()
warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
from core.data import clean_and_structure_data
ROOT='/var/home/Lukas/Projects/RATA-Flow-App'
def choc():
    raw = pd.read_excel(ROOT+'/example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
    cm = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
    dl,_,attrs = clean_and_structure_data(raw, cm, scale_min=0, scale_max=10, module="Descriptive")
    return raw, dl, cm
