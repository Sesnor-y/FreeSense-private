import sys, openpyxl, re
wb = openpyxl.load_workbook(sys.argv[1])
from collections import Counter
for ws in wb.worksheets:
    hdr = [c.value for c in ws[1]]
    print(f"== {ws.title} ({ws.max_row}x{ws.max_column}) headers: {hdr[:14]}")
    fmts = Counter(); ptext=[]; pnum=0; rounded=Counter()
    for row in ws.iter_rows(min_row=1):
        for c in row:
            v=c.value
            if isinstance(v,float):
                fmts[c.number_format]+=1
                s=repr(v)
                if '.' in s and 'e' not in s: rounded[min(len(s.split('.')[1]),6)]+=1
            if isinstance(v,str) and re.fullmatch(r"[<>]?\s*0\.\d+|<\s*0\.0001", v.strip() or 'x'): ptext.append(v)
    print("   float formats:", dict(fmts), "decimals-in-stored-floats:", dict(sorted(rounded.items())), "numeric-looking text:", ptext[:5])
if 'Run_Parameters' in wb.sheetnames:
    for r in wb['Run_Parameters'].iter_rows(values_only=True): print("   RP:", r[:2])
