"""Full-page screenshot of a report file, split into tiles (manual review).

    env/bin/python working_notes/repro/interactive_report/shoot_page.py <file.html> <out-prefix> [width]
"""
import asyncio
import base64
import io
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import shoot  # noqa: E402
import websockets  # noqa: E402
from PIL import Image  # noqa: E402

READY = """(() => { const vis = [...document.querySelectorAll('.fs-chart')].filter(e => !e.closest('[hidden]'));
 const c = vis.length, d = vis.filter(e => e.querySelector('.main-svg')).length;
 return (c > 0 && d >= c) ? document.documentElement.scrollHeight : null; })()"""


async def main(path, prefix, width):
    req = urllib.request.Request(f"http://127.0.0.1:{shoot.PORT}/json/new?about:blank", method="PUT")
    target = json.loads(urllib.request.urlopen(req, timeout=10).read())
    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=2**28) as ws:
        cdp = shoot.CDP(ws)
        await cdp.call("Emulation.setDeviceMetricsOverride", width=width, height=1000,
                       deviceScaleFactor=1, mobile=False)
        await cdp.call("Page.navigate", url=Path(path).resolve().as_uri())
        h = None
        for _ in range(200):
            r = await cdp.call("Runtime.evaluate", expression=READY, returnByValue=True)
            h = r.get("result", {}).get("value")
            if h:
                break
            await asyncio.sleep(0.25)
        await asyncio.sleep(1.5)
        r = await cdp.call("Runtime.evaluate", expression=READY, returnByValue=True)
        h = r["result"]["value"]
        await cdp.call("Emulation.setDeviceMetricsOverride", width=width, height=h,
                       deviceScaleFactor=1, mobile=False)
        await asyncio.sleep(1.5)
        shot = await cdp.call("Page.captureScreenshot", format="png", captureBeyondViewport=True)
    img = Image.open(io.BytesIO(base64.b64decode(shot["data"])))
    tile = 1600
    for i, top in enumerate(range(0, img.height, tile)):
        img.crop((0, top, img.width, min(img.height, top + tile))).save(f"{prefix}_{i:02d}.png")
    print(img.size, (img.height + tile - 1) // tile, "tiles")


if __name__ == "__main__":
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    proc = subprocess.Popen([shoot.EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                             f"--remote-debugging-port={shoot.PORT}", "--user-data-dir=/tmp/fs-edge-cdp",
                             "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{shoot.PORT}/json/version", timeout=1)
                break
            except Exception:
                time.sleep(0.25)
        asyncio.run(main(sys.argv[1], sys.argv[2], width))
    finally:
        proc.terminate()
