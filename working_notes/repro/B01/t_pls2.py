import sys; sys.path.insert(0,'/tmp/claude-1000/-var-home-Lukas-Projects-RATA-Flow-App/9c9bcd14-2ca6-4847-a1b4-e4517d635af8/scratchpad/agents/B01')
from h import *
import stats.pls as P
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import LeaveOneOut
def q2_ref(X,Y,A):
    # independent LOO: autoscale raw data within fold, sklearn PLS, drop constant cols in fold
    press=np.zeros(A); n=len(X)
    for tr,te in LeaveOneOut().split(X):
        Xt,Yt=X[tr],Y[tr]; m=Xt.mean(0); s=Xt.std(0,ddof=1); keep=s>1e-12
        my=Yt.mean(0); sy=Yt.std(0,ddof=1)
        Xf=(Xt[:,keep]-m[keep])/s[keep]; Xe=(X[te][:,keep]-m[keep])/s[keep]
        for a in range(1,A+1):
            aa=min(a, np.linalg.matrix_rank(Xf))
            mdl=PLSRegression(n_components=aa,scale=False).fit(Xf,(Yt-my)/sy)
            press[a-1]+=float(((Y[te]-(mdl.predict(Xe)*sy+my))**2).sum())
    ss=((Y-Y.mean())**2).sum(); return 1-press/ss
rows=[]
for seed in range(20):
    rng=np.random.default_rng(seed); n=8
    X=rng.normal(size=(n,4)); X[:,3]=0; X[0,3]=3.0
    Y=(X[:,0]+0.5*X[:,1]+rng.normal(0,0.7,n)).reshape(-1,1)
    Xs=(X-X.mean(0))/X.std(0,ddof=1); Ys=(Y-Y.mean(0))/Y.std(0,ddof=1)
    r=P.fit_pls(Xs,Ys,3,'loo',run_permutation_test=False)
    rows.append((seed, r['q2'], q2_ref(X,Y,3)[-1]))
df=pd.DataFrame(rows,columns=['seed','q2_freesense','q2_independent'])
print(df.round(3).to_string()); print('median abs diff', (df.q2_freesense-df.q2_independent).abs().median())
import inspect, textwrap
src=inspect.getsource(P._compute_q2_cv).replace("(x_sd > 0)","(x_sd > 1e-10)").replace("(y_sd > 0)","(y_sd > 1e-10)")
ns=dict(P.__dict__); exec(src, ns)
rows=[]
for seed in range(20):
    rng=np.random.default_rng(seed); n=8
    X=rng.normal(size=(n,4)); X[:,3]=0; X[0,3]=3.0
    Y=(X[:,0]+0.5*X[:,1]+rng.normal(0,0.7,n)).reshape(-1,1)
    Xs=(X-X.mean(0))/X.std(0,ddof=1); Ys=(Y-Y.mean(0))/Y.std(0,ddof=1)
    a=P._compute_q2_cv(Xs,Ys,3,'loo')[0]; b=ns['_compute_q2_cv'](Xs,Ys,3,'loo')[0]
    rows.append((seed,a,b,q2_ref(X,Y,3)[-1]))
print(pd.DataFrame(rows,columns=['seed','prod','threshold_patched','indep']).round(3).head(10).to_string())
