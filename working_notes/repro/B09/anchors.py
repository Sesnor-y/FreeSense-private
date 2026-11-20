import re,sys,unicodedata
def gh(t):
    t=t.strip().lower()
    t=re.sub(r'[^\w\- ]','',t,flags=re.U)
    return t.replace(' ','-')
def st_slug(t):
    t=re.sub(r"([A-Za-z\d])['’]([ts])(?![A-Za-z\d])",r"\1\2",t)
    t=re.sub(r'([a-z\d])([A-Z])',r'\1 \2',t)  # decamelize approx
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode()
    t=t.lower()
    t=re.sub(r'[^a-z\d]+','-',t).strip('-')
    return t
for fn in sys.argv[1:]:
    txt=open(fn,encoding='utf-8').read()
    # strip code fences
    txt_nc=re.sub(r'```.*?```','',txt,flags=re.S)
    heads=[m.group(2) for m in re.finditer(r'^(#{1,6})\s+(.*)$',txt_nc,flags=re.M)]
    ghs={}; sts=set()
    for h in heads:
        h2=re.sub(r'`','',h)
        s=gh(h2); 
        if s in ghs: ghs[s]+=1; s=f"{s}-{ghs[s]}"
        else: ghs[s]=0
        ghs.setdefault(s,0); sts.add(st_slug(h2))
    links=re.findall(r'\]\(#([^)]+)\)',txt)
    bad_gh=[l for l in links if l not in ghs]
    bad_st=[l for l in links if l not in sts]
    print(fn,'links',len(links),'dead(GitHub)',len(bad_gh),'dead(Streamlit approx)',len(bad_st))
    print(' GH dead:',bad_gh)
    print(' ST dead sample:',bad_st[:60])
    # relative file links
    for l in re.findall(r'\]\(([^)#h][^)]*)\)',txt): print(' filelink',l)
