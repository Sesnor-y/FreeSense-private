"""Reference-contrast consistency audit (2026-10-06), cited in working_notes/contrast-fix.md.

Runs every product as the reference against all others, on every bundled
dataset, for every post-hoc / correction method of DA, RATA, Liking and CATA,
and counts rows where two views of the same comparison disagree:

  star w/o sig    the bar carries a * but is drawn faded (not significant)
  table p<α 'No'  the table's p-value column is below α but Significant = No
  CI clears 0 …   the drawn interval excludes zero but the bar is faded
  CI crosses 0 …  the interval includes zero but the bar is full colour

It also reports, for RATA, the gap between the plotted difference (raw_diff)
and "comparison mean − reference mean" as shown in the summary table, and
checks the FDR-adjusted interval rule of Benjamini & Yekutieli (2005) against
the BH decisions.

Run from the repository root:  env/bin/python working_notes/repro/contrast/contrast_audit.py
"""

import logging
import sys
import warnings

sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
logging.disable(logging.WARNING)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from core.data import clean_and_structure_data  # noqa: E402
from stats.cata import run_cata_contrast  # noqa: E402
from stats.contrast import compute_contrast  # noqa: E402
from stats.da_anova import run_da_anova  # noqa: E402
from stats.descriptive import calculate_da_descriptives, calculate_descriptives  # noqa: E402
from stats.liking import compute_liking_lmm  # noqa: E402
from stats.mixed_models import run_mixed_models  # noqa: E402
from stats.shared.frequency import build_citation_matrix  # noqa: E402
from tests.test_cld_contrast_agreement import (  # noqa: E402
    ALPHA, DA_METHODS, EXAMPLE_DATA, LIKING_CM, LIKING_FILES, LIKING_METHODS,
    RATA_METHODS, SENSOCHOC_CM, _liking_long, _synthetic_liking, _unwrap)
from utils.plotting import _sig_stars  # noqa: E402

FDR = 'FDR (Benjamini-Hochberg)'
CATA_CM = {'assessor': 'consumer', 'product': 'product'}
CATA_METHODS = [FDR, 'Bonferroni', 'Holm', 'Uncorrected']


def audit(label, c):
    sig = c['out_of_spec'].astype(bool)
    # Exactly what plot_butterfly_chart and the summary tables read today.
    star = c.apply(lambda r: _sig_stars(r.get('p_value_fdr', r.get('p_value')), ALPHA) != '', axis=1)
    tbl_p = c['p_value_fdr'] if 'p_value_fdr' in c else c['p_value']
    fin = c.dropna(subset=['ci_lower', 'ci_upper'])
    excl = (fin['ci_lower'] > 0) | (fin['ci_upper'] < 0)
    s = sig[fin.index]
    print(f"{label:44s} n={len(c):4d} | star w/o sig={int((star & ~sig).sum()):3d} "
          f"| table p<α 'No'={int(((tbl_p < ALPHA) & ~sig).sum()):3d} "
          f"| CI clears 0, faded={int((excl & ~s).sum()):3d} "
          f"CI crosses 0, sig={int((~excl & s).sum()):3d} | CI blank={len(c) - len(fin)}")


def fcr_check(label, c):
    """BH decision vs interval at level 1 − max(R,1)·α/m, per attribute (unique pairs)."""
    c = c.assign(pair=[frozenset(x) for x in zip(c['_ref'], c['comparison'])])
    u = c.drop_duplicates(['attribute', 'pair'])
    bad = 0
    for _, g in u.groupby('attribute'):
        m, r = len(g), int((g['p_value_fdr'] < ALPHA).sum())
        bad += int(((g['p_value'] < max(r, 1) * ALPHA / m) != (g['p_value_fdr'] < ALPHA)).sum())
    print(f"   FCR interval rule, {label}: {len(u)} unique pairs, {bad} disagreements")


def every_reference(dl, cm, summ, an, full, module, method):
    prods = sorted(dl[cm['product']].unique(), key=str)
    return pd.concat([
        compute_contrast(dl, cm, summ, an, full, r, [p for p in prods if p != r],
                         ALPHA, module, method).assign(_ref=r)
        for r in prods], ignore_index=True)


def profiling():
    raw = pd.read_excel(EXAMPLE_DATA / "02_Descriptive" / "DA_chocolates_sensochoc.xlsx")
    cells = raw[['Panelist', 'Product']].drop_duplicates().sample(6, random_state=3)
    inc = (raw.merge(cells, how='left', indicator=True)
              .query("_merge == 'left_only'").drop(columns='_merge'))
    for data, tag in [(raw, 'sensochoc'), (inc, 'sensochoc, 6 empty cells')]:
        dl, _, _ = clean_and_structure_data(data, SENSOCHOC_CM, 0, 10, module='RATA')
        an, _ = _unwrap(run_mixed_models)(dl, SENSOCHOC_CM, ALPHA)
        s = _unwrap(calculate_descriptives)(dl, SENSOCHOC_CM)
        mm = s.set_index(['attribute', 'Product'])['mean_intensity']
        for m in RATA_METHODS:
            c = every_reference(dl, SENSOCHOC_CM, s, an, None, 'RATA', m)
            audit(f"RATA {tag} | {m[:14]}", c)
            gap = (c['raw_diff'] - [mm[(a, p)] - mm[(a, r)] for a, p, r
                                    in zip(c['attribute'], c['comparison'], c['_ref'])]).abs()
            print(f"   plotted difference vs table means: max gap {gap.max():.3f}, "
                  f"rows > 0.005: {int((gap > 0.005).sum())}")
            if m == FDR:
                fcr_check(f"RATA {tag}", c)
        dl, _, _ = clean_and_structure_data(data, SENSOCHOC_CM, 0, 10, module='Descriptive')
        an, full = _unwrap(run_da_anova)(dl, SENSOCHOC_CM, ALPHA, 0.10)
        s = _unwrap(calculate_da_descriptives)(dl, SENSOCHOC_CM)
        for m in DA_METHODS:
            c = every_reference(dl, SENSOCHOC_CM, s, an, full, 'Descriptive', m)
            audit(f"DA {tag} | {m[:14]}", c)
            if m == FDR:
                fcr_check(f"DA {tag}", c)


def liking():
    sets = {k: _liking_long(p) for k, p in sorted(LIKING_FILES.items())}
    sets.update({f'synthetic 10x6 seed {sd}': _synthetic_liking(10, 6, sd) for sd in range(3)})
    for tag, df in sets.items():
        lmm = _unwrap(compute_liking_lmm)(df, LIKING_CM, 0, 10, ALPHA)
        prods = list(lmm['lmm_summary']['product'])
        for m in LIKING_METHODS:
            c = pd.concat([
                compute_contrast(df, LIKING_CM, lmm['lmm_summary'], None, None, r,
                                 [p for p in prods if p != r], ALPHA, 'Liking', m,
                                 lmm_cov_params=lmm['cov_lsmeans'], df_pairwise=lmm['df_pairwise'],
                                 liking_pooled_sd=float(np.sqrt(lmm['lmm_result'].scale))).assign(_ref=r)
                for r in prods], ignore_index=True)
            audit(f"Liking {tag} | {m[:14]}", c)
            if m == FDR:
                fcr_check(f"Liking {tag}", c)


def cata():
    for f in ['CATA_bread_Meyners2013.xlsx', 'CATA_squashes_emotions.xlsx']:
        w = pd.read_excel(EXAMPLE_DATA / '01_CATA' / f)
        w['consumer'] = w['consumer'].astype(str)
        w['product'] = w['product'].astype(str)
        attrs = [c for c in w.columns if c not in ('consumer', 'product', 'liking')]
        lg = w.melt(id_vars=['consumer', 'product'], value_vars=attrs,
                    var_name='attribute', value_name='intensity')
        lg['intensity'] = lg['intensity'].astype(float)
        lg['binary'] = lg['intensity']
        fr = _unwrap(build_citation_matrix)(lg, CATA_CM)
        prods = sorted(w['product'].unique())
        for m in CATA_METHODS:
            c = pd.concat([run_cata_contrast(lg, CATA_CM, fr, attrs, r, [p for p in prods if p != r], ALPHA, m)
                           for r in prods], ignore_index=True)
            audit(f"CATA {f[5:-5]} | {m[:14]}", c)
        nan_p = c[c['p_value'].isna()]
        print(f"   rows with a NaN p-value (b = c = 0): {len(nan_p)}; "
              f"_sig_stars(NaN) = {_sig_stars(float('nan'), ALPHA)!r}")


if __name__ == '__main__':
    profiling()
    liking()
    cata()
