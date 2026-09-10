"""Explicit empirical loss summaries and attainable finite-candidate gaps.

Losses are equally weighted draws conditional on ONE scenario and parameter set.
P50 and quantiles use NumPy's linear interpolation (the legacy CAP convention).
ES integrates the empirical inverse CDF, including fractional boundary mass.
No scenario probabilities, portfolio convexity, or capital adequacy are implied.
"""

from __future__ import annotations

import numpy as np


def _loss_vector(losses) -> np.ndarray:
    x = np.asarray(losses, dtype=float)
    if x.ndim != 1 or x.size == 0 or not np.isfinite(x).all():
        raise ValueError("losses must be a nonempty, finite, one-dimensional vector")
    return x


def expected_shortfall(losses, alpha: float = 0.9) -> float:
    """Mean of the worst (1-alpha) empirical probability mass.

    Rockafellar–Uryasev objective at an empirical alpha-quantile. Using just
    mean(x[x >= quantile]) is wrong with atoms/ties or fractional tail counts.
    """
    x = _loss_vector(losses)
    if not np.isfinite(alpha) or not 0 <= alpha < 1:
        raise ValueError("alpha must be finite and in [0, 1)")
    eta = float(np.quantile(x, alpha, method="inverted_cdf"))
    return eta + float(np.maximum(x - eta, 0).mean()) / (1 - alpha)


def loss_summary(losses, alpha: float = 0.9) -> dict[str, float | int]:
    """Report location, tail level, and upper quantile spread separately."""
    x = _loss_vector(losses)
    if not np.isfinite(alpha) or not 0.5 < alpha < 1:
        raise ValueError("summary alpha must be finite and in (0.5, 1)")
    p50 = float(np.quantile(x, 0.5, method="linear"))
    qa = float(np.quantile(x, alpha, method="linear"))
    return dict(n_draws=x.size, mean=float(x.mean()), p50=p50, q_alpha=qa,
                tcar=qa - p50, es_alpha=expected_shortfall(x, alpha),
                alpha=float(alpha))


def finite_candidate_gap(costs, risks, point_cost: float, point_risk: float,
                         atol: float = 1e-9) -> tuple[float, float]:
    """Attainable cost/risk savings within a discrete candidate set.

    Minimise cost subject to risk <= disclosed risk, and vice versa. These are
    two separate comparisons and generally select different witness plans.
    NaN means no candidate reaches the corresponding threshold. Zero means
    the threshold is reachable but no strict improvement has been found.
    """
    c, r = np.asarray(costs, dtype=float), np.asarray(risks, dtype=float)
    if c.ndim != 1 or r.shape != c.shape or not np.isfinite(c).all() or not np.isfinite(r).all():
        raise ValueError("costs and risks must be aligned finite vectors")
    if not np.isfinite([point_cost, point_risk, atol]).all() or atol < 0:
        raise ValueError("point coordinates and nonnegative tolerance must be finite")
    admissible_c = c[r <= point_risk + atol]
    admissible_r = r[c <= point_cost + atol]
    dcost = max(0.0, float(point_cost - admissible_c.min())) if admissible_c.size else float("nan")
    drisk = max(0.0, float(point_risk - admissible_r.min())) if admissible_r.size else float("nan")
    return dcost, drisk


def sampled_dominance_witnesses(losses: dict[str, np.ndarray], atol=1e-9) -> dict[str, str]:
    """A cheaper-or-equal loss on every sampled path, strict on at least one.

    This establishes dominance on the evaluated sample only, not on all future
    states. An unfavorable TCaR score must not hide such a cost improvement.
    """
    if not np.isfinite(atol) or atol < 0:
        raise ValueError('dominance tolerance must be finite and nonnegative')
    arrays = {key:_loss_vector(value) for key,value in losses.items()}
    if len({a.shape for a in arrays.values()}) > 1:
        raise ValueError('dominance requires the same sampled states')
    means = {key:float(a.mean()) for key,a in arrays.items()}
    order = sorted(arrays,key=lambda key:(means[key],key))
    witnesses = {}
    for target in order:
        for alternative in order:
            if alternative == target or means[alternative] > means[target] + atol:
                continue
            d = arrays[alternative] - arrays[target]
            if np.all(d <= atol) and np.any(d < -atol):
                witnesses[target] = alternative
                break
    return witnesses


def pareto_mask(costs, risks):
    """Non-dominated observed coordinates; coincident points all remain valid."""
    c,r = _loss_vector(costs),_loss_vector(risks)
    if c.shape != r.shape:
        raise ValueError('Pareto axes must be aligned')
    return np.array([not np.any((c <= x) & (r <= y) & ((c < x) | (r < y)))
                     for x,y in zip(c,r)])
