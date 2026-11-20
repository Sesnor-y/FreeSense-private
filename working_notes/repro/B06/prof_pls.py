import sys, os, warnings, logging, cProfile, pstats
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings("ignore"); logging.disable(logging.WARNING)
import gen
from stats.pls import fit_pls
from stats.data_fusion import autoscale
sens, ext, long, wide = gen.fusion()
X, _, _ = autoscale(sens.iloc[:, 1:].to_numpy(float)); Y, ym, ys = autoscale(ext.iloc[:, 1:].to_numpy(float))
pr = cProfile.Profile(); pr.enable(); fit_pls.__wrapped__(X, Y, 3, "loo", run_permutation_test=True, n_permutations=1000) if hasattr(fit_pls, "__wrapped__") else fit_pls(X, Y, 3, "loo", run_permutation_test=True, n_permutations=1000); pr.disable()
pstats.Stats(pr).sort_stats("cumulative").print_stats("pls.py", 12)
