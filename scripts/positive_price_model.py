"""Pure research reference; deliberately independent of production module imports."""
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
    if phi==0.:return sigma*sigma*np.r_[0.,np.ones(periods-1)]
    if phi==1.:return sigma*sigma*np.arange(periods)
    return sigma*sigma*(-np.expm1(2*np.log(phi)*np.arange(periods)))/(-np.expm1(2*np.log(phi)))


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

