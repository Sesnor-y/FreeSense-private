import ast, glob, re, sys, collections
from coverage import CoverageData
ROOT='/var/home/Lukas/Projects/RATA-Flow-App/'
S='/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B05/'
datas=[]
for f in ['tests.cov','val.cov','app.cov']:
    d=CoverageData(S+f); d.read(); datas.append(d)
targets=sorted(glob.glob(ROOT+'stats/*.py')+glob.glob(ROOT+'stats/shared/*.py'))+[ROOT+'core/data.py',ROOT+'utils/export.py']
# test source index: test name -> source text
tsrc={}
for tf in glob.glob(ROOT+'tests/test_*.py'):
    tree=ast.parse(open(tf).read()); src=open(tf).read()
    for n in ast.walk(tree):
        if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'):
            tsrc[(tf.split('/')[-1],n.name)]=ast.get_source_segment(src,n)
NUM=re.compile(r'approx|isclose|allclose|assert_frame_equal|assert_series_equal|assert_array|abs\(|< ?1e-|<= ?1e-|==\s*-?\d+\.\d|\b0\.\d+\b')
def strength(ctx):
    if ctx.startswith('validation_pins'): return 'REF'
    m=re.match(r'tests/(test_\w+\.py)::(\w+)',ctx)
    if not m: return '?'
    s=tsrc.get((m.group(1),m.group(2)),'')
    asserts=[l for l in s.splitlines() if 'assert' in l]
    if any(NUM.search(l) for l in asserts): return 'NUM'
    return 'STRUCT' if asserts else 'NOASSERT'
out=[]
for t in targets:
    src=open(t).read(); tree=ast.parse(src)
    funcs=[n for n in tree.body if isinstance(n,(ast.FunctionDef,))]
    for fn in funcs:
        lines=set(range(fn.body[0].lineno, fn.end_lineno+1))
        ctxs=set()
        for d in datas:
            cbl=d.contexts_by_lineno(t)
            for l in lines:
                for c in cbl.get(l,[]):
                    if c: ctxs.add(c.split('|')[0])
        # direct calls: name appears in test source
        direct=[k for k,v in tsrc.items() if re.search(r'\b'+fn.name+r'\b',v)]
        strengths=collections.Counter(strength(c) for c in ctxs)
        out.append((t.replace(ROOT,''),fn.name,fn.lineno,len(ctxs),dict(strengths),len(direct),sorted(ctxs)))
import json
json.dump(out,open(S+'matrix.json','w'),indent=1)
for r in out:
    if r[1].startswith('_') and '--all' not in sys.argv: continue
    print(f"{r[0]}::{r[1]} L{r[2]} tests={r[3]} {r[4]} direct={r[5]}")
