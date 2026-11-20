import sys, numpy as np, itertools, re
sys.path.insert(0,".")
from utils.colours import PRODUCT_PALETTES, CLUSTER_PALETTES, GROUP_PALETTES, DRIVER_COLOUR_MAP
def to_rgb(c):
    c=c.strip()
    if c.startswith('#'): return np.array([int(c[i:i+2],16) for i in (1,3,5)])/255
    m=re.findall(r"[\d.]+", c); return np.array([float(x) for x in m[:3]])/255
def lin(v): return np.where(v<=0.04045, v/12.92, ((v+0.055)/1.055)**2.4)
def delin(v): v=np.clip(v,0,1); return np.where(v<=0.0031308, 12.92*v, 1.055*v**(1/2.4)-0.055)
# Machado et al. 2009, severity 1.0
M={'deutan':np.array([[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]]),
   'protan':np.array([[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]]),
   'tritan':np.array([[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]])}
def sim(rgb,kind):
    if kind=='normal': return rgb
    if kind=='grey':
        l=lin(rgb); Y=0.2126*l[0]+0.7152*l[1]+0.0722*l[2]; return delin(np.array([Y,Y,Y]))
    return delin(M[kind]@lin(rgb))
def lab(rgb):
    l=lin(rgb); X,Y,Z=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])@l
    Xn,Yn,Zn=0.95047,1,1.08883
    f=lambda t: np.where(t>(6/29)**3, np.cbrt(t), t/(3*(6/29)**2)+4/29)
    fx,fy,fz=f(X/Xn),f(Y/Yn),f(Z/Zn); return np.array([116*fy-16,500*(fx-fy),200*(fy-fz)])
def de2000(l1,l2):
    L1,a1,b1=l1;L2,a2,b2=l2
    C1=np.hypot(a1,b1);C2=np.hypot(a2,b2);Cb=(C1+C2)/2
    G=0.5*(1-np.sqrt(Cb**7/(Cb**7+25**7)));a1p=(1+G)*a1;a2p=(1+G)*a2
    C1p=np.hypot(a1p,b1);C2p=np.hypot(a2p,b2)
    h1=np.degrees(np.arctan2(b1,a1p))%360;h2=np.degrees(np.arctan2(b2,a2p))%360
    dL=L2-L1;dC=C2p-C1p
    dh=h2-h1
    if C1p*C2p==0: dh=0
    elif dh>180: dh-=360
    elif dh<-180: dh+=360
    dH=2*np.sqrt(C1p*C2p)*np.sin(np.radians(dh/2))
    Lb=(L1+L2)/2;Cbp=(C1p+C2p)/2
    hb=(h1+h2)/2 if abs(h1-h2)<=180 else (h1+h2+360)/2
    if C1p*C2p==0: hb=h1+h2
    T=1-0.17*np.cos(np.radians(hb-30))+0.24*np.cos(np.radians(2*hb))+0.32*np.cos(np.radians(3*hb+6))-0.20*np.cos(np.radians(4*hb-63))
    SL=1+0.015*(Lb-50)**2/np.sqrt(20+(Lb-50)**2);SC=1+0.045*Cbp;SH=1+0.015*Cbp*T
    Rt=-2*np.sin(np.radians(2*30*np.exp(-((hb-275)/25)**2)))*np.sqrt(Cbp**7/(Cbp**7+25**7))
    return np.sqrt((dL/SL)**2+(dC/SC)**2+(dH/SH)**2+Rt*(dC/SC)*(dH/SH))
def report(name, pal, n=None):
    pal=pal[:n] if n else pal
    rgbs=[to_rgb(c) for c in pal]
    out=[]
    for kind in ('normal','deutan','protan','tritan','grey'):
        labs=[lab(sim(c,kind)) for c in rgbs]
        pairs=[(de2000(labs[i],labs[j]),pal[i],pal[j]) for i,j in itertools.combinations(range(len(pal)),2)]
        mn=min(pairs); nbad=sum(p[0]<10 for p in pairs)
        out.append(f"{kind}: min dE00={mn[0]:.1f} ({mn[1]} vs {mn[2]}), pairs<10: {nbad}/{len(pairs)}")
    wl=[ (c, lab(to_rgb(c))[0]) for c in pal]
    print(f"## {name} (n={len(pal)})"); print("   "+"\n   ".join(out))
for n in (6, None):
    for k,v in PRODUCT_PALETTES.items(): report(f"product/{k} first {n or len(v)}", v, n)
for k,v in CLUSTER_PALETTES.items(): report(f"cluster/{k} first 4", v, 4)
report("DRIVER_COLOUR_MAP", list(DRIVER_COLOUR_MAP.values()))
print("white-bg lightness of colourblind palette:", [(c, round(float(lab(to_rgb(c))[0]))) for c in PRODUCT_PALETTES['colourblind']])
