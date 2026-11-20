import sys, os, warnings, logging, traceback
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import gen
from core import data as core_data
from modules.descriptive.workflow import run_full_da_analysis
CM = {"assessor": "Panelist", "product": "Product", "replicate": "Session"}
for label, raw in [("2 prod x 2 reps x 30 assessors", gen.da(30, 2, 5, 2)), ("3 prod x 2 reps", gen.da(10, 3, 5, 2)), ("1 attribute", gen.da(10, 5, 1, 2))]:
    try:
        dl, _, _ = core_data.clean_and_structure_data(raw, CM, 0, 10, [], module="Descriptive", fill_blanks_with_zero=False)
        run_full_da_analysis(dl, CM); print(label, "OK")
    except Exception as e:
        print(label, "FAIL", type(e).__name__, e)
        for fr in traceback.extract_tb(e.__traceback__):
            if "RATA-Flow-App/stats" in fr.filename or "modules" in fr.filename: print("   ", fr.filename.split("RATA-Flow-App/")[1], fr.lineno, fr.name, "|", fr.line)
