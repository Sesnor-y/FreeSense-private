import numpy as np
# Machado et al. 2009 severity 1.0 matrices (linear RGB)
M={'deutan':np.array([[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]]),
   'protan':np.array([[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]])}
def lin(c):
    c=np.array([int(c[i:i+2],16) for i in (1,3,5)])/255; return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def srgb(l):
    l=np.clip(l,0,1); return np.where(l<=0.0031308,12.92*l,1.055*l**(1/2.4)-0.055)
def lab(c):
    l=c if isinstance(c,np.ndarray) else lin(c)
    X,Y,Z=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])@l
    Xn,Yn,Zn=0.95047,1,1.08883
    f=lambda t: np.where(t>0.008856,np.cbrt(t),7.787*t+16/116)
    fx,fy,fz=f(X/Xn),f(Y/Yn),f(Z/Zn); return np.array([116*fy-16,500*(fx-fy),200*(fy-fz)])
def dE(a,b,mode=None):
    la,lb=lin(a),lin(b)
    if mode: la,lb=np.clip(M[mode]@la,0,1),np.clip(M[mode]@lb,0,1)
    return float(np.linalg.norm(lab(la)-lab(lb)))
pairs=[('robust green vs no-discrimination red','#2ca02c','#d62728'),('RdYlGn ends','#d73027','#1a9850'),('JAR ok green vs too-high red','#2ca02c','#d62728'),('DA heat low red vs mid green','#d73027','#a6d96a'),('DA heat orange vs light green','#fc8d59','#a6d96a'),('fusion red vs green','#d62728','#2ca02c')]
for n,a,b in pairs:
    print(f"{n}: normal dE={dE(a,b):.1f} deutan dE={dE(a,b,'deutan'):.1f} protan dE={dE(a,b,'protan'):.1f}")
