import ast, pathlib, collections
tot=collections.Counter()
for f in sorted(pathlib.Path('modules').rglob('*.py')):
    tree=ast.parse(f.read_text())
    for fn in [n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)]:
        calls=[n for n in ast.walk(fn) if isinstance(n,ast.Call)]
        names=[]
        for c in calls:
            fnc=c.func
            nm=fnc.attr if isinstance(fnc,ast.Attribute) else (fnc.id if isinstance(fnc,ast.Name) else '')
            names.append(nm)
        nch=names.count('render_chart')
        if not nch: continue
        ntab=sum(names.count(x) for x in ('render_result_table','dataframe','table','data_editor'))
        tot[f.parts[1]+'_charts']+=nch
        if ntab==0: 
            tot[f.parts[1]+'_fn_no_table']+=1
            print(f"{f}:{fn.lineno} {fn.name} charts={nch} tables=0")
print(tot)
