"""Screenshot the chart element of the reference page and of the spike page.

Drives a headless Microsoft Edge through the DevTools protocol, waits until
plotly has drawn (``.main-svg`` present and fonts loaded), and captures the
chart's own bounding box, so the two images can be compared pixel by pixel.

    env/bin/python working_notes/repro/interactive_report/shoot.py [indices…]

Needs the reference app on :8599 (see reference_app.py).
"""
from __future__ import annotations

import asyncio
import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websockets

EDGE = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
PORT = 9333
HERE = Path(__file__).parent
OUT = HERE / "out" / "shots"

_JS_READY = """(() => {
  const el = document.querySelector('.js-plotly-plot');
  if (!el || !el.querySelector('.main-svg')) return null;
  if (document.fonts.status !== 'loaded') return null;
  const r = el.getBoundingClientRect();
  return JSON.stringify({x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height});
})()"""


class CDP:
    def __init__(self, ws):
        self.ws, self.n = ws, 0

    async def call(self, method, **params):
        self.n += 1
        await self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get("id") == self.n:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result", {})


async def shoot(url: str, dest: Path, settle: float = 1.5) -> dict:
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/json/new?about:blank", method="PUT")
    with urllib.request.urlopen(req, timeout=10) as r:
        target = json.loads(r.read())
    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=2**27) as ws:
        cdp = CDP(ws)
        await cdp.call("Emulation.setDeviceMetricsOverride", width=1000, height=2400,
                       deviceScaleFactor=1, mobile=False)
        await cdp.call("Page.navigate", url=url)
        box = None
        for _ in range(120):
            res = await cdp.call("Runtime.evaluate", expression=_JS_READY, returnByValue=True)
            val = res.get("result", {}).get("value")
            if val:
                box = json.loads(val)
                break
            await asyncio.sleep(0.25)
        if box is None:
            raise RuntimeError(f"chart never rendered: {url}")
        await asyncio.sleep(settle)       # let plotly finish transitions/automargin
        res = await cdp.call("Runtime.evaluate", expression=_JS_READY, returnByValue=True)
        box = json.loads(res["result"]["value"])
        shot = await cdp.call("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                              clip={"x": box["x"], "y": box["y"], "width": box["w"],
                                    "height": box["h"], "scale": 1})
        dest.write_bytes(base64.b64decode(shot["data"]))
        return box


async def main(indices):
    OUT.mkdir(parents=True, exist_ok=True)
    for i in indices:
        ref = await shoot(f"http://localhost:8599/?i={i}", OUT / f"ref_{i}.png")
        spk = await shoot((HERE / "out" / f"spike_{i}.html").resolve().as_uri(), OUT / f"spike_{i}.png")
        print(i, "ref", ref, "spike", spk)


if __name__ == "__main__":
    idx = [int(a) for a in sys.argv[1:]] or list(range(8))
    proc = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                             f"--remote-debugging-port={PORT}", "--user-data-dir=/tmp/fs-edge-cdp",
                             "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1)
                break
            except Exception:
                time.sleep(0.25)
        asyncio.run(main(idx))
    finally:
        proc.terminate()
