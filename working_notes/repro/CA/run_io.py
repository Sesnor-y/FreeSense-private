import sys; sys.path.insert(0,'/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/CA')
from harness import *
which=sys.argv[1:]
for spec in which:
    pre,fn=spec.split(':')
    print('=====',pre,fn)
    at=drive(pre,fn)
    ss=at.session_state
    try:
        dl=ss[f'{pre}_df_long']; print('  products in df_long:',sorted(dl[ 'Product'].unique()), 'assessors',dl['Panelist'].nunique())
        print('  zeros CocoaA:', int(((dl.attribute=='CocoaA')&(dl.intensity==0)).sum()), 'NaN CocoaA:', int(((dl.attribute=='CocoaA')&(dl.intensity.isna())).sum()))
    except Exception as e: print('  no df_long',e)
    import pickle; pickle.dump({k:ss[k] for k in ss.to_dict() if k.startswith(pre+'_') and not callable(ss[k])} if False else None, open('/dev/null','wb'))
