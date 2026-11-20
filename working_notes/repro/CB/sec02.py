import sys, os, time, zipfile, resource, io, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "/var/home/Lukas/Projects/RATA-Flow-App")
import openpyxl
N=int(sys.argv[2]); p=sys.argv[1]
wb=openpyxl.Workbook(write_only=True); ws=wb.create_sheet("S")
ws.append(["a","b","c","d","e"])
for i in range(N): ws.append([1,1,1,1,1])
wb.save(p)
z=zipfile.ZipFile(p); u=sum(i.file_size for i in z.infolist())
print(f"rows {N} compressed {os.path.getsize(p)/1e6:.2f} MB uncompressed {u/1e6:.1f} MB ratio {u/os.path.getsize(p):.0f}:1")
from core.data import load_data
f=load_data.__wrapped__ if hasattr(load_data,'__wrapped__') else load_data
class U(io.BytesIO): name=os.path.basename(p)
t=time.time(); df=f(U(open(p,'rb').read())); dt=time.time()-t
print("shape", df.shape, f"{dt:.1f}s", "peak RSS MB", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
