"""Accounting attribution of empirical ES, including fractional and tied tails.

This allocates the tail of a SUM using one common set of scenario weights.
It is not a sum of stand-alone ES values or a causal attribution of risk drivers.
"""
import numpy as np


def empirical_tail_weights(losses, alpha):
    x = np.asarray(losses, dtype=float)
    if x.ndim != 1 or not x.size or not np.isfinite(x).all():
        raise ValueError('Finite, nonempty one-dimensional losses required')
    if isinstance(alpha, bool) or not np.isfinite(alpha) or not 0 <= alpha < 1:
        raise ValueError('alpha must be in [0, 1)')
    mass = len(x) * (1 - alpha)
    threshold = np.sort(x)[min(len(x)-1, int(np.floor(len(x)*alpha)))]
    above, tied = x > threshold, x == threshold
    boundary_mass = mass - int(above.sum())
    if boundary_mass < -1e-10 or boundary_mass > tied.sum()+1e-10:
        raise ValueError('Numerically inconsistent tail boundary')
    weights = above.astype(float)
    weights[tied] = boundary_mass / tied.sum()
    return weights / mass


def tail_decomposition(components, alpha=.95):
    """components[path, cash component], preserving signed purchases/receipts.

    Tied total losses share boundary mass equally. Conditional tail component
    means add to ES. Subtracting each sample component mean allocates ES-mean.
    Negative contributions are allowed. These are accounting allocations under
    the supplied joint distribution, not separate component risk measures.
    """
    a = np.asarray(components, dtype=float)
    if a.ndim != 2 or min(a.shape) < 1 or not np.isfinite(a).all():
        raise ValueError('Finite nonempty [path, component] matrix required')
    losses = a.sum(axis=1)
    if not np.isfinite(losses).all():
        raise ValueError('Total losses overflowed')
    weights = empirical_tail_weights(losses, alpha)
    mean = a.mean(axis=0)
    allocated = weights @ a
    return dict(weights=weights, component_means=mean, es_contributions=allocated,
                excess_contributions=allocated-mean,
                mean=float(losses.mean()), es=float(weights @ losses))
