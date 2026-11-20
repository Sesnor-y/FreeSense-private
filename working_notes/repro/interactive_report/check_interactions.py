"""Exercise the report's selectors and table sorting in headless Edge (manual check).

    env/bin/python working_notes/repro/interactive_report/check_interactions.py <file.html>
"""
import asyncio
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import shoot  # noqa: E402
import websockets  # noqa: E402

JS = r"""
(async () => {
  const out = {};
  const sel = document.querySelector('select[data-group]');
  const group = document.getElementById(sel.dataset.group);
  out.options = sel.options.length;
  out.drawnBefore = group.querySelectorAll('.fs-chart[data-drawn]').length;
  sel.value = '3'; sel.dispatchEvent(new Event('change'));
  await new Promise(r => setTimeout(r, 800));
  const shown = [...group.querySelectorAll('.fs-member')].filter(m => !m.hidden);
  out.shownAfterPick = shown.map(m => m.dataset.index);
  const svg = shown[0].querySelector('.main-svg');
  out.pickedWidth = svg ? svg.getBoundingClientRect().width : 0;
  out.pickedTitle = shown[0].querySelector('.gtitle') ? shown[0].querySelector('.gtitle').textContent : null;
  sel.value = 'all'; sel.dispatchEvent(new Event('change'));
  await new Promise(r => setTimeout(r, 2500));
  out.shownAll = [...group.querySelectorAll('.fs-member')].filter(m => !m.hidden).length;
  out.drawnAll = group.querySelectorAll('.fs-chart[data-drawn]').length;
  // sorting: first stats table, column 2 (F-ratio)
  const det = document.querySelector('details.fs-stats'); det.open = true;
  const table = det.querySelector('table.fs-table');
  const th = table.tHead.rows[0].cells[1];
  const col = i => [...table.tBodies[0].rows].map(r => r.cells[i].textContent.trim());
  out.header = th.textContent;
  th.click(); out.asc = col(1).slice(0, 4); out.ascSort = th.getAttribute('aria-sort');
  th.click(); out.desc = col(1).slice(0, 4); out.descSort = th.getAttribute('aria-sort');
  const t0 = table.tHead.rows[0].cells[0]; t0.click(); out.textAsc = col(0).slice(0, 4);
  return JSON.stringify(out);
})()
"""


async def main(path):
    req = urllib.request.Request(f"http://127.0.0.1:{shoot.PORT}/json/new?about:blank", method="PUT")
    target = json.loads(urllib.request.urlopen(req, timeout=10).read())
    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=2**28) as ws:
        cdp = shoot.CDP(ws)
        await cdp.call("Emulation.setDeviceMetricsOverride", width=1280, height=1000,
                       deviceScaleFactor=1, mobile=False)
        await cdp.call("Page.navigate", url=Path(path).resolve().as_uri())
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
    asyncio.run(main(sys.argv[1]))
finally:
    proc.terminate()
