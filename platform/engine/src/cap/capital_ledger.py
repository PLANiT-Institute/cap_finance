"""Annual capital quantities, with cash payments separate from book entries.

Renewal costs/cycles and straight-line residual values are explicit modeling
assumptions, not observations inferred from accounting standards. Renewals are
instantaneous at the start of the due year; ongoing operating maintenance must
exclude these capital renewals to avoid double counting.
"""
from dataclasses import dataclass
import math

import numpy as np


@dataclass
class CapitalLedger:
    construction_k: np.ndarray
    incumbent_renewal_k: np.ndarray
    transition_renewal_k: np.ndarray
    noncash_writeoff_k: np.ndarray
    terminal_value_k: np.ndarray

    @property
    def cash_capex_k(self):
        return self.construction_k + self.incumbent_renewal_k + self.transition_renewal_k


def _number(row, key, *, positive=False, integer=False):
    value = float(row[key])
    if not math.isfinite(value) or (positive and value <= 0):
        raise ValueError(f"{key} must be finite" + (" and positive" if positive else ""))
    if integer and value != int(value):
        raise ValueError(f"{key} must be an integer year or duration")
    return int(value) if integer else value


def facility_capital_ledger(facility, technology, adopt_year, years, *,
                            retire=False, incumbent_scale=1.0,
                            include_renewals=True, terminal_rule="none"):
    """One facility under one fixed decision; ``technology=None`` is baseline.

    Full replacement stops incumbent renewals at operation. A retrofit retains
    the incumbent campaign. Both new and incumbent capital use the same renewal
    convention. Noncash writeoffs occur on actual retirement/replacement, never
    as a payment or a construction-price exposure. Default terminal cash receipt
    is zero. ``straight_line_proxy`` is an explicitly assumed terminal value of
    surviving capital, not a verified resale value.
    """
    years = np.asarray(years)
    if (years.ndim != 1 or not len(years) or not np.isfinite(years).all()
            or not np.equal(years, years.astype(int)).all()
            or not np.all(np.diff(years) == 1)):
        raise ValueError("years must be consecutive integer calendar years")
    years = years.astype(int)
    if terminal_rule not in ("none", "straight_line_proxy"):
        raise ValueError("terminal_rule must be none or straight_line_proxy")
    if not np.isfinite(incumbent_scale) or incumbent_scale < 0:
        raise ValueError("incumbent_scale must be finite and nonnegative")
    capacity = _number(facility, "capacity", positive=True)
    unit_cost = _number(facility, "incumbent_capex_unit")
    if unit_cost < 0:
        raise ValueError("incumbent_capex_unit must be nonnegative")
    cycle = _number(facility, "reinvest_cycle_yr", positive=True, integer=True)
    last = _number(facility, "last_reline_year", integer=True)
    if last > years[0]:
        raise ValueError("campaign origin after analysis start; reconcile facility boundary first")
    incumbent_cost = capacity * unit_cost * incumbent_scale
    ledger = CapitalLedger(*(np.zeros(len(years)) for _ in range(5)))
    if retire and technology is not None:
        raise ValueError("retirement cannot also specify a transition technology")
    decision = retire or technology is not None
    if decision:
        if adopt_year is None or not np.isfinite(adopt_year) or adopt_year != int(adopt_year):
            raise ValueError("adopt_year must be an exact integer year")
        adopt_year = int(adopt_year)
        if not years[0] <= adopt_year <= years[-1]:
            raise ValueError("adoption outside the analysis horizon")
    elif adopt_year is not None:
        raise ValueError("baseline cannot specify an adoption year")
    build, life, base = 0, 0, 0.0
    retrofit = False
    if technology is not None:
        build = _number(technology, "build_years", integer=True)
        life = _number(technology, "lifetime", positive=True, integer=True)
        base = capacity * _number(technology, "capex_unit")
        if build < 0 or base < 0:
            raise ValueError("construction duration and expenditure must be nonnegative")
        flag = _number(technology, "retrofit", integer=True)
        if flag not in (0, 1):
            raise ValueError("retrofit must be 0 or 1")
        retrofit = bool(flag)
    operation = adopt_year + build if decision else math.inf
    if decision and operation > years[-1]:
        raise ValueError("operation outside the analysis horizon")
    incumbent_stop = operation if decision and not retrofit else math.inf
    # Origins before the analysis date are sunk. Continuing operation presumes
    # the campaign was renewed when due; no historical payment is recharged.
    incumbent_origin = last
    for event in range(last + cycle, int(years[-1]) + 1, cycle):
        if event >= incumbent_stop:
            break
        if include_renewals:
            incumbent_origin = event
            if event >= years[0]:
                ledger.incumbent_renewal_k[event - years[0]] += incumbent_cost
    if decision and not retrofit:
        # At a renewal boundary the prior campaign has zero remaining life.
        origin_before_stop = last
        if include_renewals:
            k = max(0, math.ceil((operation - last) / cycle) - 1)
            origin_before_stop = last + k * cycle
        remaining = max(0.0, 1.0 - (operation - origin_before_stop) / cycle)
        ledger.noncash_writeoff_k[operation - years[0]] = incumbent_cost * remaining
    new_origin = operation
    if technology is not None:
        duration = max(build, 1)
        for event in range(adopt_year, adopt_year + duration):
            ledger.construction_k[event - years[0]] += base / duration
        if include_renewals:
            for event in range(operation + life, int(years[-1]) + 1, life):
                ledger.transition_renewal_k[event - years[0]] += base
                new_origin = event
    if terminal_rule == "straight_line_proxy":
        horizon_end = int(years[-1]) + 1
        if incumbent_stop > years[-1]:
            ledger.terminal_value_k[-1] += incumbent_cost * max(0.0, 1 - (horizon_end - incumbent_origin) / cycle)
        if technology is not None:
            ledger.terminal_value_k[-1] += base * max(0.0, 1 - (horizon_end - new_origin) / life)
    return ledger
