import sys, logging, warnings; sys.path.insert(0,'.'); logging.disable(logging.WARNING); warnings.simplefilter('ignore')
import numpy as np
from sklearn.cross_decomposition import PLSRegression
from stats.data_fusion import autoscale
from stats.pls import fit_pls, _compute_q2_cv
def indep_q2(X,Y,nc):
    n=len(X); pred=np.zeros_like(Y)
    for i in range(n):
        tr=np.arange(n)!=i; xs=X[tr].std(0,ddof=1); ys=Y[tr].std(0,ddof=1)
        xs=np.where(xs>1e-10,xs,1.0); ys=np.where(ys>1e-10,ys,1.0)
        m=PLSRegression(n_components=nc,scale=False).fit(X[tr]/xs,Y[tr]/ys)
        pred[i]=m.predict(X[i:i+1]/xs)[0]*ys
    return 1-((Y-pred)**2).sum()/((Y-Y.mean(0))**2).sum()
res=[]
for seed in range(20):
    r=np.random.default_rng(seed); n=8
    X=r.normal(size=(n,4)); X[:,3]=0; X[r.integers(n),3]=r.uniform(1,5)
    Y=(X[:,:2]@np.array([[1.0,0.5],[0.7,-0.4]]))+r.normal(0,0.4,(n,2))
    Xs,_,_=autoscale(X); Ys,_,_=autoscale(Y)
    q=fit_pls(Xs,Ys,2,'loo',run_permutation_test=False)['q2']
    res.append((seed,round(q,3),round(indep_q2(Xs,Ys,2),3)))
for t in res: print(t)
d=[abs(a-b) for _,a,b in res]; print('median abs diff',np.median(d))
# show in-fold sd
r=np.random.default_rng(4); X=r.normal(size=(8,4)); X[:,3]=0; X[2,3]=3; Xs,_,_=autoscale(X); print('in-fold sd',Xs[np.arange(8)!=2,3].std(ddof=1))
