import sys, os, time, zipfile, resource, io, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "/var/home/Lukas/Projects/RATA-Flow-App")
N=int(sys.argv[2]); p=sys.argv[1]
src=io.BytesIO()
openpyxl=__import__("openpyxl"); wb=openpyxl.Workbook(); wb.active.append(["a","b","c","d","e"]); wb.save(src)
zin=zipfile.ZipFile(src)
row="<row>"+"<c><v>1</v></c>"*5+"</row>"
hdr='<row><c t="inlineStr"><is><t>a</t></is></c><c t="inlineStr"><is><t>b</t></is></c><c t="inlineStr"><is><t>c</t></is></c><c t="inlineStr"><is><t>d</t></is></c><c t="inlineStr"><is><t>e</t></is></c></row>'
sheet='<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+hdr+row*N+'</sheetData></worksheet>'
with zipfile.ZipFile(p,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for i in zin.infolist():
        z.writestr(i.filename, sheet if i.filename=="xl/worksheets/sheet1.xml" else zin.read(i.filename))
z=zipfile.ZipFile(p); u=sum(i.file_size for i in z.infolist())
print(f"rows {N} compressed {os.path.getsize(p)/1e6:.2f} MB uncompressed {u/1e6:.1f} MB ratio {u/os.path.getsize(p):.0f}:1")
from core.data import load_data
f=load_data.__wrapped__
class U(io.BytesIO): name=os.path.basename(p)
t=time.time(); df=f(U(open(p,'rb').read())); dt=time.time()-t
print("shape", df.shape, f"{dt:.1f}s", "peak RSS MB", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
