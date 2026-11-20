"""Does a user string in a chart become live markup in the report? (plan §8, SEC-07)

plotly.js renders a small subset of HTML in titles, annotations, tick labels,
legend entries and hover labels. This builds a report whose chart carries an
injection payload in every one of those places, opens it in headless Edge,
hovers the points, and reports whether any payload ran or left an element
behind (manual check; the HTML-level escaping is unit-tested).

    env/bin/python working_notes/repro/interactive_report/check_hover_injection.py
"""
import asyncio
import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))
import plotly.graph_objects as go  # noqa: E402
import shoot  # noqa: E402
import websockets  # noqa: E402

from utils.html_report import Chart, Report, Section, render_report  # noqa: E402

P = ('<img src=x onerror="window.__pwn=(window.__pwn||0)+1">'
     '<a href="javascript:window.__pwn=99">link</a>'
     '<svg onload="window.__pwn=7"></svg><b onmouseover="window.__pwn=5">b</b>')

fig = go.Figure(go.Bar(x=[P, "b"], y=[1, 2], name=P, text=[P, P], hovertext=[P, P],
                       customdata=[P, P],
                       hovertemplate="%{x}<br>%{customdata}<br>%{hovertext}<extra>" + P + "</extra>"))
fig.add_trace(go.Scatter(x=[P, "b"], y=[2, 1], name=P, mode="markers+text", text=[P, P]))
fig.update_layout(title={"text": P}, xaxis_title=P, legend_title_text=P,
                  annotations=[{"text": P, "x": 0.5, "y": 0.5, "xref": "paper", "yref": "paper"}])
html = render_report(Report("Descriptive Analysis", None, "0",
                            [Section("s", "s", charts=[Chart(fig)])]))
path = Path(tempfile.mkdtemp()) / "inject.html"
path.write_text(html, encoding="utf-8")

JS = r"""
(async () => {
  const el = document.querySelector('.js-plotly-plot');
  for (const pt of [0, 1]) {
    Plotly.Fx.hover(el, [{curveNumber: 0, pointNumber: pt}, {curveNumber: 1, pointNumber: pt}]);
    await new Promise(r => setTimeout(r, 400));
  }
  const svg = [...document.querySelectorAll('.js-plotly-plot svg, .js-plotly-plot .hoverlayer')];
  const bad = [];
  document.querySelectorAll('.js-plotly-plot *').forEach(n => {
    const tag = n.tagName.toLowerCase();
    if (['img', 'script', 'iframe', 'foreignobject'].includes(tag)) bad.push(tag);
    for (const a of n.attributes) {
      if (/^on/i.test(a.name)) bad.push(tag + '@' + a.name);
      if (/href$/i.test(a.name) && /javascript:/i.test(a.value)) bad.push(tag + '@' + a.name);
    }
  });
  const hover = document.querySelector('.hoverlayer');
  return JSON.stringify({pwn: window.__pwn || 0, bad,
                         hoverText: hover ? hover.textContent.slice(0, 200) : null,
                         title: (document.querySelector('.gtitle') || {}).textContent});
})()
"""


async def main():
    req = urllib.request.Request(f"http://127.0.0.1:{shoot.PORT}/json/new?about:blank", method="PUT")
    target = json.loads(urllib.request.urlopen(req, timeout=10).read())
    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=2**28) as ws:
        cdp = shoot.CDP(ws)
        await cdp.call("Emulation.setDeviceMetricsOverride", width=1280, height=1000,
                       deviceScaleFactor=1, mobile=False)
        await cdp.call("Page.navigate", url=path.as_uri())
        await asyncio.sleep(4)
        r = await cdp.call("Runtime.evaluate", expression=JS, awaitPromise=True, returnByValue=True)
        print(json.dumps(json.loads(r["result"]["value"]), indent=1, ensure_ascii=False))


proc = subprocess.Popen([shoot.EDGE, "--headless=new", "--disable-gpu", f"--remote-debugging-port={shoot.PORT}",
                         "--user-data-dir=/tmp/fs-edge-cdp", "about:blank"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(40):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{shoot.PORT}/json/version", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
    asyncio.run(main())
finally:
    proc.terminate()
