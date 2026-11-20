import sys, io, logging; sys.path.insert(0,'.'); logging.disable(logging.WARNING)
import pandas as pd
import core.data as cd
F='/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/CA/files/'
class U(io.BytesIO): pass
def up(fn,name=None):
    u=U(open(F+fn,'rb').read()); u.name=name or fn; return u
for fn in ['semicolon.csv','tab.csv','latin1.csv','UPPER.CSV','eu_comma_all.csv','trailing.csv']:
    try:
        df=getattr(cd.load_data,"__wrapped__",cd.load_data)(up(fn)); print(fn,'->',df.shape,list(df.columns)[:3], df.dtypes.value_counts().to_dict())
    except Exception as e: print(fn,'-> ERR',e)
# fake xls: write a real xls? not possible without xlwt; test the engine message with the xlsx bytes renamed
try:
    import xlrd; print('xlrd present', xlrd.__version__)
except ImportError: print('xlrd not installed')
