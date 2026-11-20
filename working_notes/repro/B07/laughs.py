import zipfile, io, openpyxl, sys, time, resource, pandas as pd
wb = openpyxl.Workbook(); ws = wb.active; ws.append(['a','b']); ws.append([1,2])
b = io.BytesIO(); wb.save(b); b.seek(0); zin = zipfile.ZipFile(b)
ents = '<!ENTITY l0 "lol">' + ''.join(f'<!ENTITY l{i} "{("&l%d;" % (i-1))*10}">' for i in range(1,10))
xml = ('<?xml version="1.0"?><!DOCTYPE worksheet [' + ents + ']><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
       '<row r="1"><c r="A1" t="inlineStr"><is><t>a</t></is></c></row><row r="2"><c r="A2" t="inlineStr"><is><t>&l9;</t></is></c></row></sheetData></worksheet>')
out = io.BytesIO()
with zipfile.ZipFile(out, 'w') as z:
    for it in zin.infolist():
        z.writestr(it, xml if it.filename=='xl/worksheets/sheet1.xml' else zin.read(it.filename))
out.seek(0)
t=time.time()
try:
    df = pd.read_excel(out); print('parsed', df.shape, len(str(df.iloc[0,0])))
except Exception as e:
    print('rejected:', type(e).__name__, str(e)[:150])
print(f'{time.time()-t:.2f}s RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f} MB')
