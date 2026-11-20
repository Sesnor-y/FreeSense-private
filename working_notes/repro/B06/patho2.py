import sys, os, warnings, logging
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import gen
from core import data as core_data
from modules.descriptive.workflow import run_full_da_analysis
CM = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
raw = gen.da(12, 3, 6, 2)
raw = raw[~((raw.Panelist == "A001") & (raw.Product == "P03"))]   # one assessor missed one product
for label, r in [("3 products x 2 reps, one assessor missed one product", raw),
                 ("4 products x 2 reps, one assessor missed one session of one product", gen.da(12, 4, 6, 2).drop(index=[0]))]:
    try:
        dl, _, _ = core_data.clean_and_structure_data(r, CM, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False)
        run_full_da_analysis(dl, CM); print(label, "-> OK")
    except Exception as e: print(label, "-> FAIL", type(e).__name__, e)
