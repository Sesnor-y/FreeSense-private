import ast, re, pathlib, collections
terms={'assessor':r'assessors?\b','panellist':r'panell?ists?\b','judge':r'judges?\b','consumer':r'consumers?\b','subject':r'subjects?\b','respondent':r'respondents?\b','participant':r'participants?\b',
'attribute':r'attributes?\b','descriptor':r'descriptors?\b','session':r'sessions?\b','replicate':r'replicates?\b','repetition':r'repetitions?\b',
'product':r'products?\b','sample':r'samples?\b','stimul':r'stimul(?:us|i)\b','colour':r'colou?r','colorUS':r'\bcolor\b','analyse':r'analy[sz]e','analyzeUS':r'analyze'}
groups={'cata':['modules/cata'],'rata':['modules/rata'],'descriptive':['modules/descriptive'],'liking':['modules/liking'],'fusion':['modules/fusion'],'prefmap':['modules/prefmap'],'shell':['utils/ui_shell.py','core/upload_ui.py','core/upload_validation.py','app.py'],'plotting':['utils/plotting.py']}
def strings(path):
    tree=ast.parse(pathlib.Path(path).read_text())
    docs=set()
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.Module)) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(getattr(n.body[0],'value',None),ast.Constant):
            docs.add(id(n.body[0].value))
    for n in ast.walk(tree):
        if isinstance(n,ast.Constant) and isinstance(n.value,str) and id(n) not in docs and ' ' in n.value:
            yield n.value
rows=[]
print('group'.ljust(12)+''.join(t[:9].rjust(10) for t in terms))
for g,paths in groups.items():
    files=[]
    for p in paths:
        pp=pathlib.Path(p); files+= list(pp.glob('*.py')) if pp.is_dir() else [pp]
    c=collections.Counter()
    for f in files:
        for s in strings(f):
            for t,rx in terms.items():
                c[t]+=len(re.findall(rx,s,re.I))
    print(g.ljust(12)+''.join(str(c[t]).rjust(10) for t in terms))
