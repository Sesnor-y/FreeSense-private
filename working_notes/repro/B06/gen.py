"""Synthetic dataset generators for B06 performance review."""
import numpy as np, pandas as pd

def da(n_ass=20, n_prod=12, n_attr=30, n_rep=3, seed=1, scale=10):
    rng = np.random.default_rng(seed)
    prod_eff = rng.normal(5, 1.5, (n_prod, n_attr))
    ass_eff = rng.normal(0, 0.7, (n_ass, n_attr))
    inter = rng.normal(0, 0.5, (n_ass, n_prod, n_attr))
    rows = []
    for a in range(n_ass):
        for p in range(n_prod):
            for r in range(n_rep):
                v = prod_eff[p] + ass_eff[a] + inter[a, p] + rng.normal(0, 0.8, n_attr)
                rows.append([f"A{a+1:03d}", f"P{p+1:02d}", r + 1] + list(np.clip(np.round(v, 1), 0, scale)))
    cols = ["Panelist", "Product", "Session"] + [f"Attr{j+1:03d}" for j in range(n_attr)]
    return pd.DataFrame(rows, columns=cols)

def rata(n_ass=100, n_prod=8, n_attr=30, seed=2):
    rng = np.random.default_rng(seed)
    p_tick = rng.uniform(0.1, 0.7, (n_prod, n_attr))
    mean_int = rng.uniform(1.5, 4.5, (n_prod, n_attr))
    rows = []
    for a in range(n_ass):
        for p in range(n_prod):
            tick = rng.random(n_attr) < p_tick[p]
            v = np.clip(np.round(mean_int[p] + rng.normal(0, 0.8, n_attr)), 1, 5)
            vals = [float(x) if t else np.nan for x, t in zip(v, tick)]
            rows.append([f"C{a+1:04d}", f"P{p+1:02d}"] + vals)
    return pd.DataFrame(rows, columns=["Panelist", "Product"] + [f"Attr{j+1:03d}" for j in range(n_attr)])

def cata(n_cons=150, n_prod=8, n_attr=40, seed=3, liking=True):
    rng = np.random.default_rng(seed)
    p = rng.uniform(0.05, 0.6, (n_prod, n_attr))
    rows = []
    for c in range(n_cons):
        for j in range(n_prod):
            t = (rng.random(n_attr) < p[j]).astype(int)
            lk = float(np.clip(np.round(5 + t[:5].sum() * 0.6 - t[5:10].sum() * 0.5 + rng.normal(0, 1.5)), 1, 9))
            rows.append([f"C{c+1:04d}", f"P{j+1:02d}"] + list(t) + ([lk] if liking else []))
    cols = ["consumer", "product"] + [f"Attr{k+1:03d}" for k in range(n_attr)] + (["liking"] if liking else [])
    return pd.DataFrame(rows, columns=cols)

def liking(n_cons=300, n_prod=10, n_jar=5, seed=4):
    rng = np.random.default_rng(seed)
    pm = rng.uniform(4.5, 7.5, n_prod)
    seg = rng.integers(0, 3, n_cons)
    segshift = rng.normal(0, 1.2, (3, n_prod))
    jar_bias = rng.normal(0, 0.6, (n_prod, n_jar))
    rows = []
    for c in range(n_cons):
        off = rng.normal(0, 0.8)
        for p in range(n_prod):
            lk = int(np.clip(np.round(pm[p] + segshift[seg[c], p] + off + rng.normal(0, 1.2)), 1, 9))
            jars = np.clip(np.round(3 + jar_bias[p] + rng.normal(0, 0.9, n_jar)), 1, 5).astype(int)
            rows.append([f"C{c+1:05d}", f"P{p+1:02d}", lk] + list(jars))
    df = pd.DataFrame(rows, columns=["consumer", "product", "liking"] + [f"JAR_{k+1}" for k in range(n_jar)])
    demo = pd.DataFrame({
        "consumer": [f"C{c+1:05d}" for c in range(n_cons)],
        "gender": rng.choice(["F", "M"], n_cons),
        "age_group": rng.choice(["18-34", "35-54", "55+"], n_cons),
        "usage": rng.choice(["low", "medium", "high"], n_cons),
        "age": rng.integers(18, 75, n_cons),
    })
    return df, demo

def fusion(n_prod=12, n_sens=30, n_cons=300, n_ext=8, seed=5):
    rng = np.random.default_rng(seed)
    latent = rng.normal(0, 1, (n_prod, 3))
    sens = latent @ rng.normal(0, 1, (3, n_sens)) + rng.normal(0, 0.3, (n_prod, n_sens)) + 5
    names = [f"S{p+1:02d}" for p in range(n_prod)]
    sensory = pd.DataFrame(sens.round(3), columns=[f"Sens{j+1:02d}" for j in range(n_sens)])
    sensory.insert(0, "product", names)
    ext = latent @ rng.normal(0, 1, (3, n_ext)) + rng.normal(0, 0.3, (n_prod, n_ext)) + 10
    external = pd.DataFrame(ext.round(3), columns=[f"Ext{j+1:02d}" for j in range(n_ext)])
    external.insert(0, "product", names)
    w = rng.normal(0, 1, (3, n_cons))
    lik = np.clip(np.round(5 + latent @ w * 0.8 + rng.normal(0, 1, (n_prod, n_cons))), 1, 9)
    # long raw liking and consumer x product wide means
    long = pd.DataFrame([(f"C{c+1:04d}", names[p], lik[p, c]) for c in range(n_cons) for p in range(n_prod)],
                        columns=["consumer", "product", "liking"])
    wide = pd.DataFrame(lik, columns=[f"C{c+1:04d}" for c in range(n_cons)])
    wide.insert(0, "product", names)
    return sensory, external, long, wide
