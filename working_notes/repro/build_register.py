import re, glob
AREA={"STAT":"B01 Statistics","FUNC":"B02 Workflow","IO":"B03 Import/export","CODE":"B04 Code","TEST":"B05 Testing","PERF":"B06 Performance","SEC":"B07 Security/privacy","REL":"B08 Packaging/licensing","DOC":"B09 Documentation","UI":"B10 Interface"}
F={}
order=[]
for f in sorted(glob.glob("B*.md")):
    txt=open(f).read()
    body=txt.split("\n## Findings",1)[1] if "\n## Findings" in txt else txt
    body=re.split(r'\n## (?!#)',body)[0] if False else body
    for b in re.split(r'\n(?=### [A-Z]+-\d+)',body)[1:]:
        b=re.split(r'\n## ',b)[0].rstrip()
        m=re.match(r'### ([A-Z]+-\d+): (.*)',b)
        fid,title=m.group(1),m.group(2).strip()
        g=lambda k:(re.search(r'- '+k+r':\s*(.*)',b) or [None,""])[1].strip()
        F[fid]=dict(title=title,sev=g("Severity"),conf=g("Confidence"),eff=g("Effort"),body=b,src=f)
        order.append(fid)
# final severity and status
CH="Challenge: reproduced"
S={}
def s(i,sev,st): S[i]=(sev,st)
s("IO-01","BLOCKER",CH+" (pass A); absorbs FUNC-04")
s("FUNC-01","BLOCKER",CH+" (pass A)")
s("PERF-01","BLOCKER",CH+" (pass C); narrow trigger (>= 50,000 long rows), silent, cheap fix")
s("PERF-02","BLOCKER",CH+" (pass C)")
s("FUNC-04","BLOCKER","Merged into IO-01 (same root cause, core/data.py); challenger raised HIGH to BLOCKER")
s("STAT-01","HIGH",CH+" (pass A); challenger suggested MEDIUM; kept HIGH by lead: ★ significance on pure noise, no caveat")
s("STAT-02","HIGH",CH+" (pass A); challenger suggested MEDIUM (HIGH for panels under about 30); kept HIGH by lead: wrong df and Hedges' g of 0 at small n")
s("STAT-03","MEDIUM",CH+" (pass A); downgraded HIGH to MEDIUM: the CLD (primary output) is correct, the contrast view disagrees on 16/420 pairs")
s("STAT-04","HIGH",CH+" (pass A); beta module")
s("STAT-05","HIGH","Raised MEDIUM to HIGH by lead: independently reproduced by pass A; straight-lining consumers are common, the step crashes")
s("FUNC-02","HIGH",CH+" (pass A)")
s("FUNC-03","HIGH",CH+" (pass A)")
s("FUNC-05","HIGH",CH+" (pass A); absorbs IO-03, IO-04")
s("IO-02","HIGH","Challenge: partly reproduced (pass A): a mixed decimal-comma column in a means table does warn, but blames missing values; rest holds. Absorbs FUNC-06")
s("IO-06","MEDIUM",CH+" (pass A); downgraded HIGH to MEDIUM: audit gap, cannot corrupt a result")
s("TEST-01","MEDIUM",CH+" (pass B, facts); downgraded HIGH to MEDIUM: drift in pinned numbers could not be demonstrated")
s("TEST-02","HIGH",CH+" (pass B); challenger suggested MEDIUM; kept HIGH by lead: B01 found defects (STAT-01/02/03/04) precisely in untested paths")
s("SEC-01","MEDIUM",CH+" (pass B); downgraded HIGH to MEDIUM for local use; HIGH if hosted or fed third-party free text (D-02)")
s("SEC-04","HIGH",CH+" (pass B, facts); BLOCKER before the repository or its history is made public (D-03); absorbs REL-02")
s("REL-02","HIGH","Merged into SEC-04 (same files, same commits)")
s("REL-01","HIGH",CH+" (pass B)")
s("REL-03","MEDIUM",CH+" (pass B, facts); downgraded to MEDIUM: licensing decision D-04, not a defect")
s("DOC-01","HIGH",CH+" (pass B): 10 of 10 contradictions hold (item 6 weak)")
s("DOC-02","MEDIUM","Challenge: partly reproduced (pass B): Fusion does write an Analysis_Info sheet; downgraded HIGH to MEDIUM")
s("SEC-02","MEDIUM","Merged into PERF-04 (resource limits); pass B reproduced it (15.9 s, 526 MB); LOW local, HIGH hosted")
MERGE={"FUNC-06":"IO-02","IO-03":"FUNC-05","IO-04":"FUNC-05","STAT-12":"CODE-01","IO-07":"CODE-02","STAT-07":"CODE-03","STAT-10":"DOC-03","DOC-09":"REL-05","IO-10":"UI-06","DOC-08":"UI-09","REL-12":"SEC-08"}
for k,v in MERGE.items():
    base=F[k]["sev"].split()[0].strip("(,;")
    S.setdefault(k,(base,f"Merged into {v}"))
def norm(sev):
    for w in ["BLOCKER","HIGH","MEDIUM","LOW"]:
        if sev.startswith(w): return w
    return sev
for i in order:
    if i not in S:
        S[i]=(norm(F[i]["sev"]),"Not challenged (MEDIUM/LOW)")
cond={"PERF-04":"MEDIUM (HIGH if hosted)","SEC-01":"MEDIUM (HIGH if hosted)","SEC-05":"MEDIUM (HIGH if hosted)","SEC-04":"HIGH (BLOCKER if made public)"}
rank={"BLOCKER":0,"HIGH":1,"MEDIUM":2,"LOW":3}
live=[i for i in order if not S[i][1].startswith("Merged")]
merged=[i for i in order if S[i][1].startswith("Merged")]
live.sort(key=lambda i:(rank[S[i][0]],order.index(i)))
def eff(i): return (F[i]["eff"].split() or ["?"])[0]
def conf(i): return (F[i]["conf"].split() or ["?"])[0].strip(";,")
out=[]
out.append(open("/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/register_head.md").read())
out.append("\n## 1. Consolidated table\n\nSorted by final severity. \"Orig.\" is the severity the area reviewer gave; \"Final\" is after the challenge pass and consolidation. Effort: S under 2 h, M half a day to 2 days, L more than 2 days.\n")
out.append("| ID | Title | Area | Final | Orig. | Confidence | Effort | Status after challenge |\n|---|---|---|---|---|---|---|---|")
for i in live:
    out.append(f"| {i} | {F[i]['title'].replace('|','/')} | {AREA[i.split('-')[0]]} | **{cond.get(i,S[i][0])}** | {norm(F[i]['sev'])} | {conf(i)} | {eff(i)} | {S[i][1]} |")
out.append("\n### Merged findings (fixed together with the finding they merged into; original text kept at the end of section 2)\n\n| ID | Title | Merged into |\n|---|---|---|")
for i in merged:
    out.append(f"| {i} | {F[i]['title'].replace('|','/')} | {S[i][1].split('Merged into ')[1].split(' ')[0]} |")
out.append("\n## 2. Full findings, ordered by final severity\n\nText is as written by the area reviewer (reports `B01` to `B10`), with a `Register status` line added. Where the final severity differs from the reviewer's `Severity` line, the register status line is authoritative.\n")
cur=None
for i in live+merged:
    sec = S[i][0] if i in live else "MERGED"
    hdr={"BLOCKER":"### BLOCKER","HIGH":"### HIGH","MEDIUM":"### MEDIUM","LOW":"### LOW","MERGED":"### Merged into other findings"}[sec]
    if hdr!=cur:
        out.append("\n"+hdr.replace("###","##")+"\n"); cur=hdr
    body=F[i]["body"].replace("\n### ","\n#### ").replace("### "+i,"### "+i,1)
    lines=body.split("\n")
    lines.insert(1,f"- **Register status: final severity {cond.get(i,S[i][0])}. {S[i][1]}.** (source: `{F[i]['src']}`)")
    out.append("\n".join(lines)+"\n")
open("01-findings-register.md","w").write("\n".join(out))
from collections import Counter
print("orig",Counter(norm(F[i]['sev']) for i in order), len(order))
print("final live",Counter(S[i][0] for i in live), len(live), "merged",len(merged))
