import ast, re, sys, pathlib
sys.path.insert(0,'.')
from core.config import MODULES
modmap={'cata':'CATA','rata':'RATA','descriptive':'Descriptive','liking':'Liking','fusion':'Fusion','prefmap':'PrefMap'}
for d,k in modmap.items():
    steps={i+1:s.split('. ',1)[1].lower() for i,s in enumerate(MODULES[k]['steps'])}
    for f in pathlib.Path('modules',d).glob('*.py'):
        tree=ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Constant) and isinstance(node.value,str):
                if isinstance(getattr(node,'parent',None),ast.Expr): pass
                for m in re.finditer(r'Step (\d)\s*(?:—|-|:|\(|,)?\s*([A-Za-z][A-Za-z &/()]{3,40})?',node.value):
                    n=int(m.group(1)); name=(m.group(2) or '').strip()
                    real=steps.get(n,'<none>')
                    first=name.lower().split(' ')[0] if name else ''
                    ok = first and first in real
                    print(('OK  ' if ok else '??  ')+f"{f}:{node.lineno} Step {n} '{name[:40]}' -> actual '{real}'")
