"""
PREFMAP — Preference Surface Mapping (Carroll, 1972).

Sits on top of the internal MDPREF step in stats/mdpref.py.
Takes product PCA coordinates from compute_preference_map() and the raw
liking matrix, fits per-consumer OLS models, and builds a 2D preference
surface grid.

Reference:
    Carroll, J.D. (1972). Individual differences and multidimensional
    scaling. In R.N. Shepard, A.K. Romney & S.B. Nerlove (Eds.),
    Multidimensional Scaling: Theory and Applications in the Behavioral
    Sciences (Vol. 1, pp. 105-155).
"""

import numpy as np
import pandas as pd
import streamlit as st
from scipy.spatial import Delaunay
from scipy.stats import shapiro

# Ideal points farther than this multiple of the product radius from the product
# centroid are considered numerically unstable and overridden to vector models.
IDEAL_POINT_STABILITY_FACTOR = 3.0


# ---------------------------------------------------------------------------
# Per-consumer model fitting
# ---------------------------------------------------------------------------

@st.cache_data(max_entries=8)
def compute_prefmap(
    product_coords: pd.DataFrame,
    liking_wide: pd.DataFrame,
) -> dict:
    """
    Fit a PREFMAP model per consumer and return classification + fit quality.

    Fits Phase 3 (vector/linear) and Phase 2 (ideal-point/quadratic) OLS
    models for each consumer via numpy least-squares and selects the winner
    by AICc (Burnham & Anderson, 2002) which applies a finite-sample
    correction that penalises complex models more heavily at small n.
    Phase 1 (full quadratic with cross-term) is excluded due to
    reliability concerns at typical sensory panel sizes.

    Parameters
    ----------
    product_coords : pd.DataFrame
        Shape (n_products, 2), columns PC1 and PC2.  Must be exactly 2
        columns — the product PCA scores from compute_preference_map().
    liking_wide : pd.DataFrame
        Shape (n_products, n_consumers).  Index must match product_coords.

    Returns
    -------
    dict with keys:
        consumer_results : pd.DataFrame
            One row per consumer with columns:
            consumer_id, model_type, r_squared, ideal_x, ideal_y,
            ideal_point_external, aic_vector, aic_ideal, coefficients.
            model_type ∈ {'vector', 'ideal_point', 'anti_ideal_point',
            'saddle', 'degenerate'}: quadratic AICc winners are classified
            by the signs of the quadratic coefficients — both negative →
            preference maximum ('ideal_point'), both positive → preference
            minimum ('anti_ideal_point', the least-preferred location),
            mixed/zero → 'saddle' (no point interpretation; ideal_x/y NaN).
            Anti-ideal and saddle consumers keep their quadratic fit for
            the preference surface but are never plotted as ideal points.
        n_vector : int
        n_ideal_point : int
        n_anti_ideal : int
        n_saddle : int
        n_ideal_internal : int
        n_ideal_external : int
        n_degenerate : int
        mean_r_squared : float
        n_stability_overrides : int
            Count of consumers whose AICc-winning ideal-point model was
            overridden to the vector model because the implied ideal sat
            farther than ``IDEAL_POINT_STABILITY_FACTOR * product_radius``
            from the product centroid (B.22 / F-25).
        stability_factor : float
            The hardcoded ``IDEAL_POINT_STABILITY_FACTOR`` used for the
            stability check (3.0 for v1.0); echoed so the UI caption can
            cite it without importing the module-level constant.

    Raises
    ------
    ValueError
        If product_coords does not have exactly 2 columns.
    """
    if product_coords.shape[1] != 2:
        raise ValueError(
            f"product_coords must have exactly 2 columns (PC1, PC2). "
            f"Got {product_coords.shape[1]} columns."
        )

    pc1 = product_coords.iloc[:, 0].values
    pc2 = product_coords.iloc[:, 1].values
    n = len(pc1)

    # Design matrices (add intercept column)
    ones = np.ones(n)
    X_linear = np.column_stack([ones, pc1, pc2])                       # k=3
    X_quad   = np.column_stack([ones, pc1, pc2, pc1 ** 2, pc2 ** 2])  # k=5

    # Precompute convex hull path for internal/external classification
    coords_2d = product_coords.iloc[:, :2].values
    try:
        hull_delaunay = Delaunay(coords_2d)
        hull_available = True
    except Exception:
        hull_delaunay = None
        hull_available = False

    # Precompute product centroid and radius for ideal-point stability check
    product_centroid = coords_2d.mean(axis=0)
    _dists = np.linalg.norm(coords_2d - product_centroid, axis=1)
    product_radius = float(_dists.max()) if len(_dists) > 0 else 1.0

    def _ols(X, y):
        """Fit OLS via numpy lstsq; return (coeffs, fitted, residuals)."""
        coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        fitted = X @ coeffs
        residuals = y - fitted
        return coeffs, fitted, residuals

    def _aicc(rss, n_obs, k):
        """AICc (Burnham & Anderson, 2002) — corrected AIC for small samples.

        AICc = n·ln(RSS/n) + 2k + 2k(k+1)/(n-k-1).
        When n-k-1 <= 0 the correction is undefined; return +inf so the
        model is never selected (insufficient residual df).
        """
        rss_safe = max(rss, 1e-300)
        aic = n_obs * np.log(rss_safe / n_obs) + 2 * k
        denom = n_obs - k - 1
        if denom <= 0:
            return float('inf')
        return aic + 2 * k * (k + 1) / denom

    def _r2(y, fitted):
        ss_res = float(np.sum((y - fitted) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        if ss_tot == 0.0:
            return 0.0
        return 1.0 - ss_res / ss_tot

    rows = []
    for consumer_id in liking_wide.columns:
        y = liking_wide[consumer_id].values.astype(float)

        # Degenerate: (near-)identical scores to all products
        if np.var(y) < 1e-10:
            rows.append({
                'consumer_id': consumer_id,
                'model_type': 'degenerate',
                'r_squared': 0.0,
                'ideal_x': np.nan,
                'ideal_y': np.nan,
                'ideal_point_external': np.nan,
                'aic_vector': np.nan,
                'aic_ideal': np.nan,
                'coefficients': [],
                'stability_override': False,
                'shapiro_p': np.nan,
            })
            continue

        # Guard: quadratic model has 5 parameters — underdetermined when n < 6.
        # np.linalg.lstsq finds a minimum-norm solution with RSS≈0, forcing
        # AIC_quad → −∞ and making every consumer appear ideal_point.
        # Skip quadratic fitting entirely and assign the vector model directly.
        if n < 6:
            coeffs_lin, fitted_lin, res_lin = _ols(X_linear, y)
            r2_lin = _r2(y, fitted_lin)
            _sp = float(shapiro(res_lin).pvalue) if n >= 3 else np.nan
            rows.append({
                'consumer_id': consumer_id,
                'model_type': 'vector',
                'r_squared': float(r2_lin),
                'ideal_x': np.nan,
                'ideal_y': np.nan,
                'ideal_point_external': np.nan,
                'aic_vector': float(_aicc(float(np.sum(res_lin ** 2)), n, 3)),
                'aic_ideal': np.nan,
                'coefficients': coeffs_lin.tolist(),
                'stability_override': False,
                'shapiro_p': _sp,
            })
            continue

        # --- Phase 3: vector model (linear) ---
        coeffs_lin, fitted_lin, res_lin = _ols(X_linear, y)
        rss_lin = float(np.sum(res_lin ** 2))
        aic_lin = _aicc(rss_lin, n, 3)
        r2_lin  = _r2(y, fitted_lin)

        # --- Phase 2: ideal-point model (quadratic, no cross-term) ---
        coeffs_quad, fitted_quad, res_quad = _ols(X_quad, y)
        rss_quad = float(np.sum(res_quad ** 2))
        aic_quad = _aicc(rss_quad, n, 5)
        r2_quad  = _r2(y, fitted_quad)

        # --- Select winner by AICc (lower = better) ---
        stability_override = False
        if aic_quad < aic_lin:
            r2 = r2_quad
            winning_coeffs = coeffs_quad.tolist()
            winning_residuals = res_quad

            b1, b2, b3, b4 = (
                coeffs_quad[1], coeffs_quad[2],
                coeffs_quad[3], coeffs_quad[4],
            )
            # Classify the stationary point (-b1/2b3, -b2/2b4) by the signs
            # of the quadratic coefficients (Carroll 1972 phases):
            #   b3 < 0 and b4 < 0 → preference MAXIMUM → ideal point;
            #   b3 > 0 and b4 > 0 → preference MINIMUM → anti-ideal point
            #     (the consumer's least-preferred location — liking
            #     increases away from it);
            #   mixed / zero signs → saddle or ridge, no point
            #     interpretation.
            # Plotting an anti-ideal or saddle stationary point as an
            # "ideal point" would invert the interpretation for that
            # consumer, so the three classes are kept distinct.
            if b3 < 0.0 and b4 < 0.0:
                model_type = 'ideal_point'
            elif b3 > 0.0 and b4 > 0.0:
                model_type = 'anti_ideal_point'
            else:
                model_type = 'saddle'

            if model_type == 'saddle':
                # No stationary-point interpretation; keep the quadratic fit
                # (it is the AICc winner and still contributes to the
                # preference surface) but expose no point coordinates.
                ideal_x = np.nan
                ideal_y = np.nan
                external = np.nan
            else:
                ideal_x = float(-b1 / (2.0 * b3))
                ideal_y = float(-b2 / (2.0 * b4))

                # Stability check: stationary points far outside the product
                # space are numerically unreliable — override to the vector
                # model. Applies to ideal and anti-ideal points alike.
                _dist = float(np.sqrt(
                    (ideal_x - product_centroid[0]) ** 2 +
                    (ideal_y - product_centroid[1]) ** 2
                ))
                if product_radius > 0 and _dist > IDEAL_POINT_STABILITY_FACTOR * product_radius:
                    # Override to vector model
                    model_type = 'vector'
                    r2 = r2_lin
                    winning_coeffs = coeffs_lin.tolist()
                    winning_residuals = res_lin
                    ideal_x = np.nan
                    ideal_y = np.nan
                    external = np.nan
                    stability_override = True
                else:
                    if hull_available:
                        external = not bool(
                            hull_delaunay.find_simplex(np.array([[ideal_x, ideal_y]])) >= 0
                        )
                    else:
                        # Hull unavailable (too few / collinear products) —
                        # treat ideal as internal (conservative fallback).
                        external = False
        else:
            model_type = 'vector'
            r2 = r2_lin
            winning_coeffs = coeffs_lin.tolist()
            winning_residuals = res_lin
            ideal_x = np.nan
            ideal_y = np.nan
            external = np.nan

        # Shapiro-Wilk normality test on winning model residuals
        _sp = float(shapiro(winning_residuals).pvalue) if n >= 3 else np.nan

        rows.append({
            'consumer_id': consumer_id,
            'model_type': model_type,
            'r_squared': float(r2),
            'ideal_x': ideal_x,
            'ideal_y': ideal_y,
            'ideal_point_external': external,
            'aic_vector': float(aic_lin),
            'aic_ideal': float(aic_quad),
            'coefficients': winning_coeffs,
            'stability_override': stability_override,
            'shapiro_p': _sp,
        })

    consumer_results = pd.DataFrame(rows)

    non_deg = consumer_results[consumer_results['model_type'] != 'degenerate']
    n_vector    = int((non_deg['model_type'] == 'vector').sum())
    n_ideal     = int((non_deg['model_type'] == 'ideal_point').sum())
    n_anti_ideal = int((non_deg['model_type'] == 'anti_ideal_point').sum())
    n_saddle    = int((non_deg['model_type'] == 'saddle').sum())
    ideal_rows  = non_deg[non_deg['model_type'] == 'ideal_point']
    n_internal  = int((ideal_rows['ideal_point_external'] == False).sum())
    n_external  = int((ideal_rows['ideal_point_external'] == True).sum())
    n_degen     = int((consumer_results['model_type'] == 'degenerate').sum())
    mean_r2     = float(non_deg['r_squared'].mean()) if not non_deg.empty else 0.0
    # B.22 / F-25: aggregate count of consumers whose ideal-point AICc winner
    # was overridden to the vector model because the implied ideal sat more
    # than IDEAL_POINT_STABILITY_FACTOR * product_radius from the product
    # centroid. Surfaced so Stage C can caption "X of N consumers had
    # unstable ideal points and were re-classified as vector" next to the
    # model-type pie. The factor itself stays hardcoded for v1.0.
    n_stability_overrides = int(consumer_results.get(
        'stability_override', pd.Series(dtype=bool)
    ).fillna(False).sum())

    return {
        'consumer_results': consumer_results,
        'n_vector': n_vector,
        'n_ideal_point': n_ideal,
        'n_anti_ideal': n_anti_ideal,
        'n_saddle': n_saddle,
        'n_ideal_internal': n_internal,
        'n_ideal_external': n_external,
        'n_degenerate': n_degen,
        'mean_r_squared': mean_r2,
        'vector_only_forced': n < 6,
        'n_stability_overrides': n_stability_overrides,
        'stability_factor': IDEAL_POINT_STABILITY_FACTOR,
    }


# ---------------------------------------------------------------------------
# Preference surface grid
# ---------------------------------------------------------------------------

@st.cache_data(max_entries=8)
def compute_preference_surface(
    product_coords: pd.DataFrame,
    liking_wide: pd.DataFrame,
    prefmap_results: dict,
    grid_resolution: int = 50,
    r_squared_weighted: bool = False,
    mask_to_hull: bool = True,
    r2_threshold: float = 0.0,
) -> dict:
    """
    Build a 2D predicted-liking grid over the PCA product space.

    Parameters
    ----------
    product_coords : pd.DataFrame
        Shape (n_products, 2) — PC1, PC2 from compute_preference_map().
    liking_wide : pd.DataFrame
        Shape (n_products, n_consumers).
    prefmap_results : dict
        Return value of compute_prefmap().
    grid_resolution : int
        Number of grid points per axis (default 50).
    r_squared_weighted : bool
        Weight each consumer's predictions by their R² when averaging.
    mask_to_hull : bool
        Set grid points outside the convex hull of product_coords to NaN.
    r2_threshold : float
        Exclude consumers with R² below this value (0.0 = include all).

    Returns
    -------
    dict with keys:
        grid_pc1 : np.ndarray  (1D, length grid_resolution)
        grid_pc2 : np.ndarray  (1D, length grid_resolution)
        surface_z : np.ndarray (2D, shape grid_resolution × grid_resolution)
        z_min : float
        z_max : float
        r_squared_weighted : bool
        mask_to_hull : bool
        grid_resolution : int
    """
    consumer_results = prefmap_results['consumer_results']

    # Filter to usable consumers
    usable = consumer_results[
        (consumer_results['model_type'] != 'degenerate') &
        (consumer_results['r_squared'] >= r2_threshold)
    ].copy()

    pc1_vals = product_coords.iloc[:, 0].values
    pc2_vals = product_coords.iloc[:, 1].values

    # Bounding box extended 25% to exceed the 20% axis margin used by _product_axis_range
    pc1_range = pc1_vals.max() - pc1_vals.min()
    pc2_range = pc2_vals.max() - pc2_vals.min()
    pad1 = pc1_range * 0.25 if pc1_range > 0 else 1.0
    pad2 = pc2_range * 0.25 if pc2_range > 0 else 1.0

    grid_pc1 = np.linspace(pc1_vals.min() - pad1, pc1_vals.max() + pad1, grid_resolution)
    grid_pc2 = np.linspace(pc2_vals.min() - pad2, pc2_vals.max() + pad2, grid_resolution)
    G1, G2 = np.meshgrid(grid_pc1, grid_pc2)  # shape (grid_res, grid_res)

    # R²-weighted mode: fall back to uniform weights when all usable R² are zero
    # (avoids 0/0 → NaN surface with no user feedback).
    r2_weight_fallback = False
    if r_squared_weighted and usable['r_squared'].sum() == 0.0:
        r_squared_weighted = False
        r2_weight_fallback = True

    # Accumulate weighted predictions
    sum_pred   = np.zeros((grid_resolution, grid_resolution))
    sum_weight = np.zeros((grid_resolution, grid_resolution))

    for _, row in usable.iterrows():
        coeffs = row['coefficients']
        model  = row['model_type']
        weight = float(row['r_squared']) if r_squared_weighted else 1.0

        if model == 'vector':
            # ŷ = b0 + b1*PC1 + b2*PC2
            b0, b1, b2 = coeffs[0], coeffs[1], coeffs[2]
            pred = b0 + b1 * G1 + b2 * G2
        else:  # quadratic winner (ideal_point / anti_ideal_point / saddle)
            # ŷ = b0 + b1*PC1 + b2*PC2 + b3*PC1² + b4*PC2²
            b0, b1, b2, b3, b4 = (
                coeffs[0], coeffs[1], coeffs[2], coeffs[3], coeffs[4]
            )
            pred = b0 + b1 * G1 + b2 * G2 + b3 * G1 ** 2 + b4 * G2 ** 2

        sum_pred   += weight * pred
        sum_weight += weight

    # Avoid division by zero
    with np.errstate(invalid='ignore', divide='ignore'):
        surface_z = np.where(sum_weight > 0, sum_pred / sum_weight, np.nan)

    # Clip predictions to the observed liking data range (not the full
    # theoretical scale).  This prevents extrapolation beyond values actually
    # given by consumers.  The colorbar in the UI uses the session-state
    # scale_min/scale_max for its endpoints, so the bar may extend beyond
    # the clipped surface — this is intentional (shows the full scale while
    # the surface only covers observed territory).
    scale_min = float(liking_wide.values.min())
    scale_max = float(liking_wide.values.max())
    surface_z = np.clip(surface_z, scale_min, scale_max)

    # Convex hull masking
    if mask_to_hull:
        coords_2d = product_coords.iloc[:, :2].values
        try:
            hull_tri = Delaunay(coords_2d)
            pts = np.column_stack([G1.ravel(), G2.ravel()])
            inside = (hull_tri.find_simplex(pts) >= 0).reshape(grid_resolution, grid_resolution)
            surface_z = np.where(inside, surface_z, np.nan)
        except Exception:
            pass  # too few points for hull — leave unmasked

    valid = surface_z[~np.isnan(surface_z)]
    z_min = float(valid.min()) if len(valid) > 0 else 0.0
    z_max = float(valid.max()) if len(valid) > 0 else 1.0

    return {
        'grid_pc1': grid_pc1,
        'grid_pc2': grid_pc2,
        'surface_z': surface_z,
        'z_min': z_min,
        'z_max': z_max,
        'scale_min': scale_min,
        'scale_max': scale_max,
        'r_squared_weighted': r_squared_weighted,
        'r2_weight_fallback': r2_weight_fallback,
        'mask_to_hull': mask_to_hull,
        'grid_resolution': grid_resolution,
    }


# ---------------------------------------------------------------------------
# Plain-language map summary
# ---------------------------------------------------------------------------

def summarise_preference_directions(
    product_coords: pd.DataFrame,
    consumer_results: pd.DataFrame,
) -> dict:
    """Summarise where the fitted consumer vectors point (ux-P2).

    Presentation-only: it re-reads the coefficients ``compute_prefmap`` already
    fitted and computes no new model.  Only vector-model consumers contribute —
    an ideal-point consumer has a preference *optimum*, not a direction, so a
    direction read off its linear terms would be meaningless.

    Each vector consumer's preference direction is the unit vector of its
    (PC1, PC2) slope coefficients.  A product's *vector-weighted preference* is
    the mean projection of its coordinates onto those unit directions: the
    higher it is, the more consumer arrows point at that product.

    Parameters
    ----------
    product_coords : pd.DataFrame
        The frame passed to ``compute_prefmap``: rows = products, first two
        numeric columns = PC1 / PC2.  A ``product`` column (or the index) names
        the rows.
    consumer_results : pd.DataFrame
        ``compute_prefmap(...)['consumer_results']``.

    Returns
    -------
    dict with keys:
        n_vectors : int
            Consumers contributing a direction.
        top_products : list[tuple[str, float]]
            Up to two (product, mean projection) pairs, highest first.
        pct_pc1_positive / pct_pc1_negative : float
            Share of those directions pointing into the positive / negative
            PC1 half-plane, in per cent.  A direction with an exactly-zero
            PC1 component is in neither half, so the two shares sum to 100
            only when no such direction exists (D-3).  Returns an empty
            summary (``n_vectors == 0``) when no consumer was fitted as a
            vector.

    Every vector consumer counts **once, unweighted** — the R²-weighting the
    map can be drawn with affects arrow length on screen, not this summary
    (D-3).  The caption that reports these numbers says so.
    """
    empty = {
        'n_vectors': 0,
        'top_products': [],
        'pct_pc1_positive': float('nan'),
        'pct_pc1_negative': float('nan'),
    }
    if consumer_results is None or consumer_results.empty:
        return empty
    if 'model_type' not in consumer_results.columns:
        return empty

    directions = []
    for coeffs in consumer_results.loc[
        consumer_results['model_type'] == 'vector', 'coefficients'
    ]:
        if coeffs is None or len(coeffs) < 3:
            continue
        d = np.asarray(coeffs[1:3], dtype=float)
        norm = float(np.linalg.norm(d))
        # A zero-slope fit has no direction (flat plane); skip rather than
        # divide by zero.
        if not np.isfinite(norm) or norm < 1e-12:
            continue
        directions.append(d / norm)

    if not directions:
        return empty

    directions = np.vstack(directions)

    if 'product' in product_coords.columns:
        labels = product_coords['product'].astype(str).tolist()
        coords = product_coords.drop(columns=['product'])
    else:
        labels = [str(i) for i in product_coords.index]
        coords = product_coords
    coords = coords.select_dtypes(include='number').iloc[:, :2].values.astype(float)

    # Centre the products so the projection measures position relative to the
    # map's centre of gravity, not to the arbitrary PCA origin offset.
    coords = coords - coords.mean(axis=0)
    projections = coords @ directions.T          # (n_products, n_vectors)
    mean_projection = projections.mean(axis=1)

    order = np.argsort(mean_projection)[::-1][:2]
    top_products = [(labels[i], float(mean_projection[i])) for i in order]

    n = len(directions)
    # D-3: a direction with an exactly-zero PC1 component points straight up
    # or down the map and belongs to neither half. Counting it as negative
    # (the old `n - n_positive`) overstated the left share. Measure-zero in
    # practice, but the two shares are reported to the user as a split, so
    # they must not silently absorb a third case: they may now sum to < 100.
    n_positive = int((directions[:, 0] > 0).sum())
    n_negative = int((directions[:, 0] < 0).sum())
    return {
        'n_vectors': n,
        'top_products': top_products,
        'pct_pc1_positive': 100.0 * n_positive / n,
        'pct_pc1_negative': 100.0 * n_negative / n,
    }
