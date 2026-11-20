import ast, sys, re, pathlib
sys.path.insert(0,'.')
from core import state as cs
root=pathlib.Path('.')
files=[p for d in ('modules','core','utils','app.py') for p in (root.glob(d+'/**/*.py') if d!='app.py' else [root/d])]
listed=set(k for v in cs.MODULE_STATE_KEYS.values() for k in v)
written={}; widget=set(); aliases=set(); dyn=[]
for f in files:
    t=ast.parse(f.read_text())
    # aliases: name = st.session_state
    al={'ss','state','_ss','session'}
    for n in ast.walk(t):
        if isinstance(n,ast.Assign) and isinstance(n.value,ast.Attribute) and n.value.attr=='session_state':
            for tg in n.targets:
                if isinstance(tg,ast.Name): al.add(tg.id)
    def is_ss(v):
        return (isinstance(v,ast.Attribute) and v.attr=='session_state') or (isinstance(v,ast.Name) and v.id in al)
    for n in ast.walk(t):
        tgts=[]
        if isinstance(n,(ast.Assign,)): tgts=n.targets
        if isinstance(n,(ast.AugAssign,ast.AnnAssign)): tgts=[n.target]
        for tg in tgts:
            if isinstance(tg,ast.Subscript) and is_ss(tg.value):
                if isinstance(tg.slice,ast.Constant): written.setdefault(tg.slice.value,set()).add(f"{f}:{n.lineno}")
                else: dyn.append(f"{f}:{n.lineno}: {ast.unparse(tg)}")
            if isinstance(tg,ast.Attribute) and isinstance(tg.value,ast.Attribute) and tg.value.attr=='session_state':
                written.setdefault(tg.attr,set()).add(f"{f}:{n.lineno} (attr)")
        if isinstance(n,ast.Call):
            for kw in n.keywords:
                if kw.arg in('key','widget_key') and isinstance(kw.value,ast.Constant): widget.add(kw.value.value)
            if isinstance(n.func,ast.Attribute) and n.func.attr in('setdefault','update') and is_ss(n.func.value):
                if n.func.attr=='setdefault' and n.args and isinstance(n.args[0],ast.Constant):
                    written.setdefault(n.args[0].value,set()).add(f"{f}:{n.lineno} (setdefault)")
                elif n.func.attr=='update':
                    for a in n.args:
                        if isinstance(a,ast.Dict):
                            for k in a.keys:
                                if isinstance(k,ast.Constant): written.setdefault(k.value,set()).add(f"{f}:{n.lineno} (update)")
                        else: dyn.append(f"{f}:{n.lineno}: update({ast.unparse(a)[:60]})")
glob={'selected_module','current_step','analysis_complete','show_about_readme','show_methods_readme','export_format','global_colour_palette','sidebar_nav_step'}
print("UNLISTED written non-widget keys:")
for k in sorted(written):
    if k not in listed and k not in widget and k not in glob:
        print(' ',k, sorted(written[k])[:3])
print("\nDYNAMIC writes:"); print("\n".join(dyn))
