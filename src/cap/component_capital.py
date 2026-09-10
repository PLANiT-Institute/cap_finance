"""Dated capital payments for a process with components of different lives.

Amounts remain in a caller-declared unit of account. No price-year conversion,
annual capital charge, incumbent replacement or operating cost is inferred.
"""
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class CapitalComponent:
    component_id: str
    cost_per_capacity: float
    lifetime_years: int


@dataclass(frozen=True)
class ComponentCapitalCashflows:
    years: tuple[int, ...]
    component_ids: tuple[str, ...]
    unit_of_account: str
    construction: np.ndarray
    renewal: np.ndarray
    terminal_receipt: np.ndarray

    def __post_init__(self):
        for field in ('construction','renewal','terminal_receipt'):
            a=np.array(getattr(self,field),dtype=float,copy=True)
            if a.shape!=(len(self.component_ids),len(self.years)) or not np.isfinite(a).all() or (a<0).any():
                raise ValueError('Component cashflows must be finite nonnegative component-by-year arrays')
            a.setflags(write=False);object.__setattr__(self,field,a)

    @property
    def cash_payments(self):
        return (self.construction+self.renewal).sum(axis=0)

    @property
    def net_cash_payments(self):
        return self.cash_payments-self.terminal_receipt.sum(axis=0)


def _integer(v,name,minimum=None):
    if isinstance(v,(bool,np.bool_)) or not isinstance(v,(int,float,np.number)) or not np.isfinite(v) or int(v)!=v:
        raise ValueError(f'{name} must be an exact integer')
    if minimum is not None and v<minimum:raise ValueError(f'{name} below its allowed minimum')
    return int(v)


def component_capital_cashflows(components,capacity,adopt_year,build_years,years,*,
                               unit_of_account,construction_weights=None,
                               include_renewals=True,terminal_rule='none'):
    """Construct cash only; retirement/replacement of incumbent is a separate ledger.

    Construction pays over adopt_year..operation_year-1, or at operation if build
    is zero. Renewal pays at the beginning of each component's due operating year.
    The optional straight-line proxy is credited in the final model-year bucket,
    using remaining life at the end of that year; it is not a resale observation.
    Lifetimes, constant replacement costs and zero renewal downtime are assumptions.
    """
    years=tuple(_integer(y,'year') for y in years)
    if not years or any(b-a!=1 for a,b in zip(years,years[1:])):
        raise ValueError('Years must be a nonempty consecutive calendar sequence')
    adopt=_integer(adopt_year,'adopt_year');build=_integer(build_years,'build_years',0)
    operation=adopt+build
    if adopt<years[0] or operation>years[-1]:raise ValueError('Construction and operation must lie within the modeled horizon')
    if isinstance(capacity,(bool,np.bool_)) or not isinstance(capacity,(int,float,np.number)) or not np.isfinite(capacity) or capacity<0:
        raise ValueError('Capacity must be a finite nonnegative number')
    if not isinstance(unit_of_account,str) or not unit_of_account.strip():
        raise ValueError('An explicit unit of account is required; a source composite is not a real price year')
    if not isinstance(include_renewals,bool):raise ValueError('include_renewals must be boolean')
    if terminal_rule not in ('none','straight_line_proxy'):raise ValueError('Unknown terminal-value convention')
    components=tuple(components)
    if not components:raise ValueError('At least one explicitly costed component is required')
    ids=[]
    for c in components:
        if not isinstance(c,CapitalComponent) or not isinstance(c.component_id,str) or not c.component_id.strip() or c.component_id in ids:
            raise ValueError('Component IDs must be unique nonempty strings')
        ids.append(c.component_id);_integer(c.lifetime_years,'lifetime_years',1)
        v=c.cost_per_capacity
        if isinstance(v,(bool,np.bool_)) or not isinstance(v,(int,float,np.number)) or not np.isfinite(v) or v<0:
            raise ValueError('Component unit cost must be finite and nonnegative')
    duration=max(build,1)
    weights=np.full(duration,1/duration) if construction_weights is None else np.asarray(construction_weights,dtype=float)
    if weights.shape!=(duration,) or not np.isfinite(weights).all() or (weights<0).any() or not math.isclose(float(weights.sum()),1.,abs_tol=1e-12,rel_tol=0.):
        raise ValueError('Construction weights must match the duration and sum to one')
    arrays=[np.zeros((len(components),len(years))) for _ in range(3)]
    initial,renewal,terminal=arrays
    for i,c in enumerate(components):
        cost=float(capacity*c.cost_per_capacity);life=int(c.lifetime_years);origin=operation
        initial[i,adopt-years[0]:adopt-years[0]+duration]=cost*weights
        if include_renewals:
            for due in range(operation+life,years[-1]+1,life):
                renewal[i,due-years[0]]=cost;origin=due
        if terminal_rule=='straight_line_proxy':
            terminal[i,-1]=cost*max(0.,1-(years[-1]+1-origin)/life)
    return ComponentCapitalCashflows(years,tuple(ids),unit_of_account,*arrays)
