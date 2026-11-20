"""Write one standalone HTML page per captured spec, themed by utils.report_theme.

    env/bin/python working_notes/repro/interactive_report/spike_html.py

The page skeleton is spike_page.html (a 704 px column, Streamlit's centred
layout); shoot.py then compares each page with Streamlit's own rendering.
Re-run capture_figures.py, this script and shoot.py after a Streamlit upgrade.
"""
import base64
import json
import string
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from utils import report_theme as rt  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "out"
WIDTH = 704  # Streamlit's centred main column
PAGE = string.Template((HERE / "spike_page.html").read_text(encoding="utf-8"))


def page(rec) -> str:
    spec = rt.theme_spec(rec["spec"])
    spec["layout"].pop("width", None)
    spec["layout"].setdefault("height", rt.DEFAULT_HEIGHT)
    return PAGE.substitute(
        font=base64.b64encode(rt.source_sans_woff2()).decode(), width=WIDTH,
        plotly=rt.plotly_js(), payload=json.dumps(spec).replace("</", "<\\/"),
        config=json.dumps(rt.chart_config(rec["config"])))


for i, path in enumerate(sorted((OUT / "specs").glob("*.json"))):
    (OUT / f"spike_{i}.html").write_text(page(json.loads(path.read_text())), encoding="utf-8")
    print(i, path.name)
