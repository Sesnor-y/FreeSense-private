import sys; sys.path.insert(0,'.'); sys.path.insert(0,sys.argv[1])
from cvd import dE
from contrast import cr
import itertools
from utils.colours import PRODUCT_PALETTES, CLUSTER_PALETTES
def tohex(c):
    if c.startswith('rgb'):
        v=[int(float(x)) for x in c[c.index('(')+1:-1].split(',')[:3]]; return '#%02x%02x%02x'%tuple(v)
    return c
for fam,P in (('product',PRODUCT_PALETTES),('cluster',CLUSTER_PALETTES)):
  for name,pal in P.items():
    pal=[tohex(c) for c in pal]
    for n in (6,8):
        sub=pal[:n]
        res={}
        for m in (None,'deutan','protan'):
            res[m]=min((dE(a,b,m),a,b) for a,b in itertools.combinations(sub,2))
        print(f"{fam:8}{name:12} first{n}: min dE normal {res[None][0]:5.1f}  deutan {res['deutan'][0]:5.1f} {res['deutan'][1:]}  protan {res['protan'][0]:5.1f}")
print('Bold',[ (c,round(cr(tohex(c),'#FFFFFF'),2)) for c in PRODUCT_PALETTES['default']])
