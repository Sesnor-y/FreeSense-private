import sys, os, io, time, resource, warnings, logging
sys.path.insert(0, os.getcwd()); warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import numpy as np, pandas as pd
from core import data as core_data
target_mb = float(sys.argv[1]); frac_clean = float(sys.argv[2])
n_attr = 100; rng = np.random.default_rng(0)
row_bytes = 16 + n_attr * 4
n = int(target_mb * 1e6 / row_bytes)
n_ass = 200; n_prod = max(1, n // (n_ass * 3))
df = pd.DataFrame(np.round(rng.uniform(0, 10, (n, n_attr)), 1), columns=[f"A{j:03d}" for j in range(n_attr)])
df.insert(0, "Session", np.arange(n) % 3 + 1); df.insert(0, "Product", [f"P{i//(n_ass*3):05d}" for i in range(n)]); df.insert(0, "Panelist", [f"J{i % n_ass:03d}" for i in range(n)])
buf = io.BytesIO(); df.to_csv(buf, index=False); raw = buf.getvalue(); del df, buf
print(f"CSV size {len(raw)/1e6:.0f} MB, rows {n}, cols {n_attr+3}")
from streamlit.runtime.uploaded_file_manager import UploadedFile, UploadedFileRec, UploadFileUrlInfo
def Up(b): return UploadedFile(UploadedFileRec("id1", "big.csv", "text/csv", b), UploadFileUrlInfo("id1", "", ""))
r0 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
t = time.perf_counter(); d = core_data.load_data(Up(raw)); print(f"load_data: {time.perf_counter()-t:.1f}s  maxRSS {r0:.0f}->{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f} MB  df mem {d.memory_usage(deep=True).sum()/1e6:.0f} MB")
t = time.perf_counter(); d2 = core_data.load_data(Up(raw)); print(f"load_data cache hit (hash of {len(raw)/1e6:.0f} MB bytes): {time.perf_counter()-t:.2f}s")
sub = d.iloc[: int(len(d) * frac_clean)]
CM = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
t = time.perf_counter(); dl, _, _ = core_data.clean_and_structure_data(sub, CM, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False)
print(f"clean_and_structure on {len(sub)} wide rows -> {len(dl)} long rows: {time.perf_counter()-t:.1f}s long mem {dl.memory_usage(deep=True).sum()/1e6:.0f} MB maxRSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f} MB")
