"""Sharp arithmetic bounds conditional on an explicit additive output identity.

Limits are assumed effective output ceilings, not automatically nameplate capacity.
No probability distribution or technical joint-production ratios are inferred.
"""
import math
from numbers import Real


def additive_output_bounds(total, ceilings):
    """For sum(q_i)=total, 0<=q_i<=ceiling_i, return each feasible interval."""
    def number(v):
        if isinstance(v, bool) or not isinstance(v, Real) or not math.isfinite(v) or v < 0:
            raise ValueError('Finite nonnegative outputs and ceilings required')
        return float(v)
    total=number(total)
    if not ceilings or any(not isinstance(k,str) or not k for k in ceilings):
        raise ValueError('Named component ceilings required')
    ceilings={k:number(v) for k,v in ceilings.items()}
    if total > math.fsum(ceilings.values()):
        raise ValueError('Aggregate output exceeds the assumed effective ceilings')
    return {k:(max(0.,total-math.fsum(v for key,v in ceilings.items() if key!=k)),min(total,v))
            for k,v in ceilings.items()}
