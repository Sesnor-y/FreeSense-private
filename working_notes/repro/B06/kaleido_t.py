import sys, os, time, threading, subprocess
sys.path.insert(0, os.getcwd())
import warnings; warnings.filterwarnings("ignore")
import plotly.graph_objects as go, numpy as np
from utils.plot_theme import export_figure, apply_base_layout
fig = apply_base_layout(go.Figure(go.Scatter(x=np.arange(500), y=np.random.randn(500), mode="markers")))
def kids(): return subprocess.run(["pgrep", "-P", str(os.getpid()), "-c"], capture_output=True, text=True).stdout.strip()
for i in range(4):
    for fmt in ("png", "svg"):
        t = time.perf_counter(); b = export_figure(fig, "word", fmt=fmt); print(f"call {i} {fmt}: {time.perf_counter()-t:.2f}s  bytes={len(b)} child_procs={kids()}")
res = []
def w(): t=time.perf_counter(); export_figure(fig, "powerpoint", fmt="png"); res.append(time.perf_counter()-t)
th = [threading.Thread(target=w) for _ in range(4)]; t=time.perf_counter(); [x.start() for x in th]; [x.join() for x in th]
print(f"4 concurrent png exports: wall {time.perf_counter()-t:.2f}s, each " + ", ".join(f"{r:.2f}" for r in res))
