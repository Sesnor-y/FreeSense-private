import ast, pathlib, re
for p in sorted(pathlib.Path('.').glob('**/*.py')):
    if p.parts[0] in ('env','tests','validation','.git','scripts'): continue
    t=ast.parse(p.read_text())
    for n in ast.walk(t):
        if not isinstance(n,ast.With): continue
        for it in n.items:
            c=it.context_expr
            if isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and c.func.attr=='expander':
                if any(k.arg=='on_change' for k in c.keywords): continue
                heavy=set()
                for m in ast.walk(ast.Module(body=n.body,type_ignores=[])):
                    if isinstance(m,ast.Call):
                        f=m.func; name=f.attr if isinstance(f,ast.Attribute) else getattr(f,'id','')
                        if re.match(r'(render_chart|plot_|compute_|build_|make_|_build|_plot|run_|fit_|_compute|go\.Figure|make_subplots)',name) or name in('Figure','make_subplots'):
                            heavy.add(name)
                print("E",p,n.lineno) if False else None
                if heavy: print(f"{p}:{n.lineno} {sorted(heavy)[:5]}")
