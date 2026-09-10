"""Carbon allowance quantities and payments; auction shares are not tax rates.

The caller supplies jurisdiction-specific prices and allocations. This module
does not infer a company's allocation from a sector's auction fraction. A gross
obligation with zero allocation is a price-exposure proxy unless it is verified
as the applicable company rule.
"""
import numpy as np


def carbon_mode(cfg):
    mode = cfg.get('carbon_accounting_mode', 'gross_obligation_proxy')
    if mode not in ('legacy_auction_discount', 'gross_obligation_proxy', 'net_trade', 'purchase_only'):
        raise ValueError(f'Unknown carbon accounting mode: {mode}')
    return mode


def free_allowance_path(cfg, company, years):
    """Read an explicit annual company allocation; never extrapolate missing law."""
    mode = carbon_mode(cfg)
    if mode in ('legacy_auction_discount', 'gross_obligation_proxy'):
        return np.zeros(len(years))
    table = cfg.get('free_allowances_tco2', {}).get(company, {})
    values = []
    for year in years:
        value = table.get(int(year), table.get(str(int(year))))
        if value is None or not np.isfinite(float(value)) or float(value) < 0:
            raise ValueError(f'Explicit free allowance quantity required for {company} {int(year)}')
        values.append(float(value))
    return np.asarray(values)


def allowance_payment(emissions, prices, free_allowances, *, mode="net_trade"):
    """Payment in price currency; prices may have a leading simulation axis.

    ``net_trade`` credits surplus sales at the same price; ``purchase_only``
    values only uncovered emissions and assigns zero value to surplus. Both
    omit banking, borrowing, transaction costs and allocation adjustment unless
    the caller explicitly supplies their effect in allowance quantities.
    """
    arrays = []
    for name, values in (("emissions", emissions), ("prices", prices),
                         ("free_allowances", free_allowances)):
        arr = np.asarray(values, dtype=float)
        if not np.isfinite(arr).all() or np.any(arr < 0):
            raise ValueError(f"{name} must contain finite nonnegative values")
        arrays.append(arr)
    e, p, a = arrays
    if mode not in ("net_trade", "purchase_only"):
        raise ValueError("mode must be net_trade or purchase_only")
    try:
        obligation = e - a
        if mode == "purchase_only":
            obligation = np.maximum(obligation, 0)
        return obligation * p
    except ValueError as exc:
        raise ValueError("emissions, prices and allocations have incompatible shapes") from exc


def incremental_allowance_payment(plan_emissions, baseline_emissions, prices,
                                  plan_allowances, baseline_allowances, *,
                                  mode="net_trade"):
    """Paired-path difference; plan-dependent allocations must remain explicit."""
    return (allowance_payment(plan_emissions, prices, plan_allowances, mode=mode)
            - allowance_payment(baseline_emissions, prices, baseline_allowances, mode=mode))
