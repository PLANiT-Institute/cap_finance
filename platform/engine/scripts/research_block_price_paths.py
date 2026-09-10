"""Joint empirical block price paths, conditional on an explicit scenario anchor.

Research candidate only: historical benchmark returns are not IAM forecast errors.
All series share block starts. Exact finite-support exponential moments anchor
expected prices; the simulated sample is never divided by its own sample mean.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def log_mean_exp(x: np.ndarray, axis: int = 0) -> np.ndarray:
    top = np.max(x, axis=axis, keepdims=True)
    return np.squeeze(top, axis=axis) + np.log(np.mean(np.exp(x-top), axis=axis))


def block_paths(returns, months, paths, block_length, seed):
    """Return positive monthly multipliers, log anchors, and sampled block starts.

    Blocks are contiguous, overlapping historical windows sampled independently
    without circular wrapping. A final partial block uses the same start support
    as a full block. Drift is removed by series; mean anchoring then removes the
    exponential moment of cumulative returns under this exact block mechanism.
    """
    r = np.asarray(returns, dtype=float)
    if r.ndim != 2 or not np.isfinite(r).all():
        raise ValueError('returns must be a finite [month, factor] matrix')
    if not (1 <= block_length <= len(r)) or months < 1 or paths < 1:
        raise ValueError('invalid block length, horizon, or path count')
    r = r-r.mean(axis=0)
    support = len(r)-block_length+1
    windows = r[np.arange(support)[:, None] + np.arange(block_length)]
    partial = np.cumsum(windows, axis=1)
    partial_log_moment = log_mean_exp(partial, axis=0)
    nblocks = (months+block_length-1)//block_length
    starts = np.random.default_rng(seed).integers(0, support, size=(paths, nblocks))
    innovations = windows[starts].reshape(paths, nblocks*block_length, r.shape[1])[:, :months]
    log_levels = np.cumsum(innovations, axis=1)
    h = np.arange(months)
    log_anchor = ((h//block_length)[:, None]*partial_log_moment[-1]
                  + partial_log_moment[h % block_length])
    multipliers = np.exp(log_levels-log_anchor)
    if not np.isfinite(multipliers).all() or not (multipliers > 0).all():
        raise ValueError('price multipliers overflowed or underflowed; shorten horizon/review model')
    return multipliers, log_anchor, starts


def gaussian_paths(returns, months, paths, seed):
    r = np.asarray(returns, dtype=float)
    cov = np.cov(r, rowvar=False, ddof=1)
    innovations = np.random.default_rng(seed).multivariate_normal(np.zeros(r.shape[1]), cov,
                                                                  size=(paths, months))
    anchor = np.arange(1, months+1)[:, None]*np.diag(cov)/2
    return np.exp(np.cumsum(innovations, axis=1)-anchor)


def expected_shortfall(values, alpha=.95):
    """Empirical integral quantile ES, including fractional boundary mass."""
    x = np.sort(np.asarray(values, dtype=float))
    if x.ndim != 1 or not len(x) or not np.isfinite(x).all() or not 0 <= alpha < 1:
        raise ValueError('ES needs finite nonempty scalar losses and 0 <= alpha < 1')
    mass = (1-alpha)*len(x)
    k = int(np.floor(mass))
    total = x[-k:].sum() if k else 0.
    if mass > k:
        total += (mass-k)*x[-k-1]
    return float(total/mass)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--paths', type=int, default=10000)
    ap.add_argument('--months', type=int, default=60)
    ap.add_argument('--seed', type=int, default=20260907)
    args = ap.parse_args()
    if args.months % 12:
        ap.error('demo requires complete calendar years')
    source = ROOT/'data/research_v2/price_history/aligned_monthly_log_returns.csv'
    df = pd.read_csv(source).set_index('period')
    r = df.to_numpy()
    out = ROOT/'data/research_v2/block_price_paths'
    out.mkdir(parents=True, exist_ok=True)
    rows, saved, anchors = [], {}, {}
    for length in (0, 1, 6, 12, 24):
        model = 'iid_gaussian' if length == 0 else f'empirical_block_{length}'
        if length:
            mult, anchor, starts = block_paths(r, args.months, args.paths, length, args.seed)
            anchors[model] = anchor.tolist()
        else:
            mult = gaussian_paths(r, args.months, args.paths, args.seed)
        # Annual purchases at constant monthly quantity use arithmetic, not
        # end-of-year or geometric-average prices.
        annual = mult.reshape(args.paths, args.months//12, 12, r.shape[1]).mean(axis=2)
        saved[model] = annual
        for yr in range(annual.shape[1]):
            for j, series in enumerate(df.columns):
                x = annual[:, yr, j]
                p50, p90, p95 = np.quantile(x, [.5, .9, .95])
                rows.append(dict(model=model, block_length=length, year_index=yr+1,
                    series=series, paths=args.paths, mean=x.mean(), mean_mc_se=x.std(ddof=1)/np.sqrt(len(x)),
                    theoretical_mean=1., p50=p50, p90=p90, p95=p95,
                    upper_gap90=p90-p50, es95=expected_shortfall(x),
                    unit='annual_arithmetic_mean_price_multiplier',
                    interpretation='conditional benchmark process sensitivity; not company TCaR'))
    pd.DataFrame(rows).to_csv(out/'annual_multiplier_metrics.csv', index=False)
    np.savez_compressed(out/'annual_multipliers.npz', **saved)
    (out/'exact_log_anchors.json').write_text(json.dumps(anchors, indent=2)+'\n')
    manifest = dict(source=str(source.relative_to(ROOT)),
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_period=[str(df.index[0]),str(df.index[-1])], factors=list(df.columns),
        **vars(args), models=list(saved), anchor='exact E[multiplier]=1 under declared process',
        annual_aggregation='arithmetic mean of 12 monthly price multipliers; constant monthly purchases',
        joint_resampling=True, circular_blocks=False, block_length_fitted=False,
        calibration_uncertainty_included=False, long_run_mean_reversion=False,
        historical_crisis_frequency_reused=True, unobserved_crisis_probability_identified=False,
        gcam_forecast_residuals=False, company_prices_mapped=False, FIN_modified=False,
        implementation_status='research candidate; not an externally validated cost distribution',
        limits=['Block boundaries break dependence beyond the block',
                'A finite monthly support does not cap cumulative prices as horizon grows',
                'Repeated crisis blocks may create long-run paths absent from history',
                'Same mean across methods does not imply equal median, ES, or economic plausibility',
                'Full history informed candidate design; no untouched holdout',
                'No electricity, hydrogen, carbon, currency, basis or contract residuals'])
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(dict(rows=len(rows), models=len(saved), paths=args.paths,
                         out=str(out.relative_to(ROOT))), indent=2))


if __name__ == '__main__':
    main()
