import re,os,subprocess,sys
files=sys.argv[1:]
src=subprocess.run("git ls-files '*.py' '*.R' '*.sh' '*.toml'",shell=True,capture_output=True,text=True).stdout.split()
corpus={f:open(f,encoding='utf-8',errors='ignore').read() for f in src}
allsrc="\n".join(corpus.values())
for fn in files:
    txt=open(fn,encoding='utf-8').read()
    toks=set(re.findall(r'`([^`\n]{2,80})`',txt))
    missing_paths=[];missing_ids=[]
    for t in sorted(toks):
        t0=t.strip()
        m=re.match(r'^([\w./-]+\.(py|md|R|csv|sh|toml|txt|xlsx|svg))(::\w+)?',t0)
        if m and '/' in m.group(1) or (m and m.group(2) in('py','md','R','sh')):
            p=m.group(1)
            cands=[p,os.path.join(os.path.dirname(fn),p)]
            if not any(os.path.exists(c) for c in cands) and not any(f.endswith('/'+p) or f==p for f in src):
                missing_paths.append(t0)
            if m.group(3):
                name=m.group(3)[2:]
                if not re.search(r'\b'+re.escape(name)+r'\b',allsrc): missing_ids.append(t0)
            continue
        m=re.match(r'^(?:[\w.]+\.)?(\w+)\(\)?.*$',t0)
        idm=re.match(r'^([A-Za-z_][\w.]*)(\(.*\))?$',t0)
        if idm and ('_' in t0 or '(' in t0 or '.' in t0):
            name=idm.group(1).split('.')[-1]
            if len(name)<3: continue
            if not re.search(r'\b'+re.escape(name)+r'\b',allsrc):
                missing_ids.append(t0)
    print('==',fn); print(' missing paths:',missing_paths); print(' missing ids:',missing_ids)
