import time; from scipy import stats
for k, df in [(12, 22), (12, 418), (12, 1000), (6, 58)]:
    for fn in ("cdf", "sf"):
        t = time.perf_counter(); v = getattr(stats.studentized_range, fn)(3.1, k, df); dt = time.perf_counter() - t
        print(k, df, fn, f"{dt*1000:.1f} ms", v)
    t = time.perf_counter(); stats.studentized_range.ppf(0.95, k, df); print("  ppf", f"{(time.perf_counter()-t)*1000:.0f} ms")
