import sys, io, os, warnings, logging; warnings.filterwarnings('ignore'); logging.disable(logging.WARNING)
sys.path.insert(0,'.')
from core.data import load_data
S = os.path.dirname(os.path.abspath(__file__)) + '/data/'
for f in sorted(os.listdir(S)):
    from streamlit.runtime.uploaded_file_manager import UploadedFile, UploadedFileRec
    b = UploadedFile(UploadedFileRec(file_id=f, name=f, type='text/csv', data=open(S+f,'rb').read()), None)
    try:
        df = load_data(b)
        print(f"{f}: shape={df.shape} cols={list(df.columns)[:9]} dtypes={dict(df.dtypes.astype(str).value_counts())}")
    except Exception as e:
        print(f"{f}: ERR {str(e)[:300]}")
