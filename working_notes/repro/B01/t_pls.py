import sys; sys.path.insert(0,'/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B01')
from h import *
from stats.pls import _compute_q2_cv, fit_pls
res=[]
for seed in range(200):
    rng=np.random.default_rng(seed)
    n=8
    X=rng.normal(size=(n,4)); X[:,3]=0; X[0,3]=3.0
    Y=(X[:,0]+rng.normal(0,1.0,n)).reshape(-1,1)
    Xs=(X-X.mean(0))/X.std(0,ddof=1); Ys=(Y-Y.mean(0))/Y.std(0,ddof=1)
    q2,rm,q2pc,pred,_,_=_compute_q2_cv(Xs,Ys,4,'loo')
    P=pred[3]; valid=~np.isnan(P).any(1)
    if valid.all(): continue
    # alternative: fill missing rows with their nc=3 prediction
    P2=P.copy(); P2[~valid]=pred[2][~valid]
    ss=((Ys-Ys.mean())**2).sum()
    q2_fill=1-((Ys-P2)**2).sum()/ss
    q2_both=1-((Ys[valid]-P[valid])**2).sum()/((Ys[valid]-Ys.mean())**2).sum()
    res.append((q2pc[3], q2_fill, q2_both, int((~valid).sum())))
r=np.array(res)
print('datasets with dropped rows:',len(r),'rows dropped per dataset:',set(r[:,3]))
print('mean Q2@4 as reported:',r[:,0].mean().round(3),' if dropped row predicted at nc=3:',r[:,1].mean().round(3),' both restricted:',r[:,2].mean().round(3))
print('fraction reported > fill-in:', (r[:,0]>r[:,1]).mean())
print(r[:5].round(3))
