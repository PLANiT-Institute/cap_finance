"""Explicit purchased incumbent-energy retention for transition technologies.

These fractions describe purchased coal, gas and electricity, not total process
heat or feedstock carbon. They must not be inferred automatically from a Scope 1
emission factor. Internal coproduct use/export remains a separate system boundary.
"""
import numpy as np


FIELDS = ('retained_coal_fraction', 'retained_gas_fraction', 'retained_grid_fraction')


def retained_energy(technology, cfg):
    """Return retained fractions (coal, gas, grid) with no partial-field fallback."""
    if technology is None:
        return 1.0, 1.0, 1.0
    mode = cfg.get('energy_balance_mode', 'explicit_retention')
    if mode not in ('explicit_retention', 'legacy_retrofit_all'):
        raise ValueError(f'Unknown energy balance mode: {mode}')
    get = technology.get if hasattr(technology, 'get') else lambda k, default=None: getattr(technology,k,default)
    retrofit = float(get('retrofit', 0))
    if not np.isfinite(retrofit) or retrofit not in (0,1):
        raise ValueError('retrofit must be 0 or 1')
    if mode == 'legacy_retrofit_all':
        return (retrofit,) * 3
    values = [get(field, np.nan) for field in FIELDS]
    if any(v is None or not np.isfinite(float(v)) for v in values):
        raise ValueError('Explicit purchased-energy retention required: ' + ', '.join(FIELDS))
    result = tuple(float(v) for v in values)
    if any(v < 0 or v > 1 for v in result):
        raise ValueError('Purchased-energy retention fractions must lie in [0,1]')
    return result
