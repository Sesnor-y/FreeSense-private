"""Draw one captured spec with st.plotly_chart, as the app does (spike reference).

    env/bin/streamlit run working_notes/repro/interactive_report/reference_app.py --server.port 8599
    open http://localhost:8599/?i=<n>
"""
import json
from pathlib import Path

import streamlit as st

st.set_page_config(layout="centered")
specs = sorted((Path(__file__).parent / "out" / "specs").glob("*.json"))
i = int(st.query_params.get("i", 0))
rec = json.loads(specs[i].read_text())
st.plotly_chart(rec["spec"], config=rec["config"], key="chart")
