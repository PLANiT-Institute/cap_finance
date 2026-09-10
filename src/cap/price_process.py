"""Positive lognormal paths with explicit analytic variance and normalization."""
import numpy as np


def log_variance_path(sigma, periods, process="gbm", half_life=10.):
    if not np.isfinite(sigma) or sigma<0 or periods<1 or int(periods)!=periods:
        raise ValueError("Finite nonnegative volatility and positive integer periods required")
    if process not in ("gbm","ou"):
        raise ValueError("Unknown price process")
    if process=="gbm": return sigma*sigma*np.arange(periods)
    if not np.isfinite(half_life) or half_life<=0:
        raise ValueError("OU half-life must be finite and positive")
    phi=np.exp(-np.log(2.)/half_life)
    variance=np.zeros(periods)
    for t in range(1,periods):variance[t]=phi*phi*variance[t-1]+sigma*sigma
    return variance


def positive_exp(log_values):
    with np.errstate(over="ignore",under="ignore",invalid="ignore"):
        value=np.exp(log_values)
    if not np.isfinite(value).all() or np.any(value<=0):
        raise ValueError("Price multiplier overflow/underflow; review model scale")
    return value


def scale_lognormal_multiplier(shock, amplitude, log_variance, normalisation="mean"):
    """Change log-price dispersion using the same standard-normal path.

    Mean-normalized S=exp(Z-v/2) becomes exp(a*Z-a²*v/2), E[S_a]=1.
    Median-normalized S=exp(Z) becomes exp(a*Z), median[S_a]=1.
    Here Z is centered Gaussian with declared variance v at each date.
    """
    s=np.asarray(shock,dtype=float);v=np.asarray(log_variance,dtype=float)
    if not np.isfinite(s).all() or np.any(s<=0): raise ValueError("Shocks must be finite and positive")
    if not np.isfinite(v).all() or np.any(v<0): raise ValueError("Log variance must be finite and nonnegative")
    if not np.isfinite(amplitude) or amplitude<0: raise ValueError("Amplitude must be finite and nonnegative")
    if normalisation not in ("mean","median"): raise ValueError("Unknown normalization")
    try: np.broadcast_shapes(s.shape,v.shape)
    except ValueError as e: raise ValueError("Variance shape must match shock dates") from e
    if amplitude==1.: return s.copy()
    adjustment=.5*amplitude*(1.-amplitude)*v if normalisation=="mean" else 0.
    return positive_exp(amplitude*np.log(s)+adjustment)


def factor_from_innovations(z,sigma,process="gbm",normalisation="mean",half_life=10.):
    """Generate one factor from independent standard-normal yearly innovations.

    First column is the known present price, fixed at multiplier one.
    """
    z=np.asarray(z,dtype=float)
    if z.ndim!=2 or not np.isfinite(z).all(): raise ValueError("Finite two-dimensional innovations required")
    variance=log_variance_path(sigma,z.shape[1],process,half_life)
    if normalisation not in ("mean","median"): raise ValueError("Unknown normalization")
    log_state=np.zeros_like(z)
    phi=1. if process=="gbm" else np.exp(-np.log(2.)/half_life)
    for t in range(1,z.shape[1]): log_state[:,t]=phi*log_state[:,t-1]+sigma*z[:,t]
    shift=.5*variance if normalisation=="mean" else 0.
    return positive_exp(log_state-shift),variance


class PriceShocks(dict):
    """Factor arrays with normalization metadata preserved through transformations."""

    def __init__(self, arrays, log_variance, normalisation="mean", metadata=None):
        super().__init__(arrays)
        if normalisation not in ("mean", "median"):
            raise ValueError("Unknown normalization")
        self.normalisation = normalisation
        self.log_variance = {k: np.asarray(v, dtype=float).copy() for k, v in log_variance.items()}
        self.metadata = dict(metadata or {})
        shapes = {np.asarray(v).shape for v in self.values()}
        if len(shapes) != 1 or len(next(iter(shapes), ())) != 2:
            raise ValueError("All price factors must have the same two-dimensional shape")
        if min(next(iter(shapes))) < 1:
            raise ValueError("At least one sample and date are required")
        if any(not np.isfinite(v).all() or (v <= 0).any() for v in self.values()):
            raise ValueError("Price factors must be finite and positive")
        for k, v in self.log_variance.items():
            if k not in self or v.shape != (self[k].shape[1],) or not np.isfinite(v).all() or (v < 0).any():
                raise ValueError(f"Invalid analytic variance for {k}")

    def copy(self):
        return PriceShocks(dict(self), self.log_variance, self.normalisation, self.metadata)

    def subset(self, count):
        if not isinstance(count, (int, np.integer)) or isinstance(count, bool) or count < 1:
            raise ValueError("Subset count must be a positive integer")
        return PriceShocks({k: v[:count] for k, v in self.items()}, self.log_variance,
                           self.normalisation, self.metadata)

    def with_factor(self, name, values, log_variance=None):
        if name in self and log_variance is None:
            raise ValueError("Replacing a factor requires its updated analytic variance")
        arrays, variances = dict(self), dict(self.log_variance)
        arrays[name] = values
        if log_variance is not None:
            variances[name] = log_variance
        return PriceShocks(arrays, variances, self.normalisation, self.metadata)

    def rescale(self, factor, amplitude):
        if factor not in self.log_variance:
            raise ValueError(f"Analytic variance metadata required to rescale {factor}")
        scaled = scale_lognormal_multiplier(self[factor], amplitude, self.log_variance[factor],
                                           self.normalisation)
        return self.with_factor(factor, scaled, self.log_variance[factor] * amplitude**2)


def technology_capex_multiplier(shocks, amplitude):
    values = np.asarray(shocks["capex"])
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("CAPEX multipliers must be finite and positive")
    if amplitude == 1:
        return values
    # Explicit central-path evaluation has no random variance to amplify.
    if np.all(values == 1):
        return scale_lognormal_multiplier(values, amplitude, 0.)
    if not isinstance(shocks, PriceShocks) or "capex" not in shocks.log_variance:
        raise ValueError("CAPEX scaling requires price-model metadata; rerun E3 or preserve PriceShocks")
    return scale_lognormal_multiplier(values, amplitude, shocks.log_variance["capex"],
                                       shocks.normalisation)


def rescale_factor(shocks, factor, amplitude):
    if isinstance(shocks, PriceShocks):
        return shocks.rescale(factor, amplitude)
    if np.all(shocks[factor] == 1):
        return {**shocks, factor: scale_lognormal_multiplier(shocks[factor], amplitude, 0.)}
    raise ValueError("Volatility sensitivity requires analytic price-model metadata")
