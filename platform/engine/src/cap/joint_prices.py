"""Labelled joint price paths and an explicit bridge to legacy FIN arrays.

Matching shapes do not prove matching Monte Carlo states. Keep draw IDs, years,
sampling identity and scenario metadata until the final array boundary. Labels
can detect accidental mixing; they cannot verify that a caller labelled data
truthfully. Mapping evidence must state whether a coefficient is estimated or
an assumption. No contract, FX or procurement coefficient is supplied here.
"""
from dataclasses import dataclass
from types import MappingProxyType

import numpy as np

from cap.scenario_prices import ScenarioPriceCurve, _years


def _text(value):
    return isinstance(value, str) and bool(value.strip())


@dataclass(frozen=True)
class DrawAxis:
    years: tuple
    draw_ids: tuple
    sample_id: str

    def __post_init__(self):
        years = _years(self.years)
        ids = tuple(self.draw_ids)
        if not ids or any(not _text(x) for x in ids) or len(set(ids)) != len(ids):
            raise ValueError('Draw IDs must be nonempty, unique strings')
        if not _text(self.sample_id):
            raise ValueError('Sampling identity is required')
        object.__setattr__(self, 'years', tuple(int(y) for y in years))
        object.__setattr__(self, 'draw_ids', ids)

    @property
    def shape(self):
        return len(self.draw_ids), len(self.years)


@dataclass(frozen=True)
class JointPricePaths:
    curve: ScenarioPriceCurve
    axis: DrawAxis
    values: np.ndarray
    evidence: str

    def __post_init__(self):
        if self.curve.years != self.axis.years:
            raise ValueError('Price curve and draw years must match exactly')
        if not _text(self.evidence):
            raise ValueError('Price-path construction evidence is required')
        values = np.asarray(self.values, dtype=float)
        if values.shape != self.axis.shape or not np.isfinite(values).all():
            raise ValueError('Finite price paths must match labelled draws and years')
        # Own immutable storage: changing a caller's source array cannot corrupt
        # the price paths after their alignment has been checked.
        values = np.frombuffer(values.tobytes(), dtype=float).reshape(values.shape)
        object.__setattr__(self, 'values', values)


def prices_from_multipliers(curve, axis, multipliers, *, evidence):
    mult = np.asarray(multipliers, dtype=float)
    if mult.shape != axis.shape or not np.isfinite(mult).all() or (mult <= 0).any():
        raise ValueError('Multipliers must be finite, positive and match the draw axis')
    return JointPricePaths(curve, axis, mult * np.asarray(curve.values), evidence)


def indexed_procurement_price(source, target_curve, *, indexed_share, evidence):
    """P_target = central_target * (1-b + b*P_source/central_source).

    b may vary by year. Both central and realised source prices must be positive.
    A deterministic component and an indexed component need a time-varying b
    when their relative central costs change. This is a declared conditional
    mapping, not evidence that a benchmark equals a delivered plant price.
    """
    if not _text(evidence):
        raise ValueError('Procurement mapping evidence or explicit assumption required')
    if (source.curve.model, source.curve.scenario, source.curve.years) != (
            target_curve.model, target_curve.scenario, target_curve.years):
        raise ValueError('Procurement mapping must preserve model, scenario and years')
    central = np.asarray(source.curve.values)
    if (central <= 0).any() or (source.values <= 0).any():
        raise ValueError('A positive benchmark is required for ratio indexing')
    b = np.asarray(indexed_share, dtype=float)
    if b.shape not in ((), central.shape) or not np.isfinite(b).all() or ((b < 0) | (b > 1)).any():
        raise ValueError('Indexed share must be in [0,1], scalar or matched by year')
    if (np.asarray(target_curve.values) <= 0).any():
        raise ValueError('Indexed procurement needs positive target central prices')
    value = np.asarray(target_curve.values) * (1-b+b*source.values/central)
    return JointPricePaths(target_curve, source.axis, value,
        source.evidence + '; benchmark=' + source.curve.source + '; mapping=' + evidence)


@dataclass(frozen=True)
class FINPriceRequirement:
    commodity: str
    quantity_unit: str
    currency: str
    price_year: int
    boundary: str
    heat_basis: str | None = None


class JointPriceBundle:
    """One scenario and one labelled state space, with explicit price channels."""
    def __init__(self, prices):
        prices = dict(prices)
        if not prices or any(not _text(k) for k in prices):
            raise ValueError('Nonempty named price channels required')
        if any(not isinstance(p, JointPricePaths) for p in prices.values()):
            raise ValueError('Every channel must contain labelled price paths')
        ref = next(iter(prices.values()))
        for p in prices.values():
            if p.axis != ref.axis:
                raise ValueError('Price channels have mismatched draw IDs, years or sampling identity')
            if (p.curve.model, p.curve.scenario) != (ref.curve.model, ref.curve.scenario):
                raise ValueError('Do not pool distinct model/scenario conditions')
        self.prices = MappingProxyType(prices)
        self.axis = ref.axis

    def fin_inputs_for_profile(self, profile, requirements, *, years):
        required = {'elec','re','h2','gas','coal','co2'}
        required.update(f.price_key for f in profile.additional_commodity_flows)
        if not required.issubset(self.prices):
            raise ValueError('FIN profile has a missing price channel')
        for flow in profile.additional_commodity_flows:
            if flow.quantity_unit != self.prices[flow.price_key].curve.quantity_unit:
                raise ValueError(f'{flow.flow_id}: physical flow and price denominator mismatch')
        prices, shocks = self.to_fin_inputs(requirements, years=years)
        from cap.plancost import validate_profile_price_basis
        if profile.embedded_price_basis is None and np.any(profile.other_cost_k):
            raise ValueError('Strict joint-price bridge needs explicit embedded-price provenance for other costs')
        validate_profile_price_basis(profile,prices,years)
        return prices, shocks

    def to_fin_inputs(self, requirements, *, years):
        """Strip labels only after matching all declared FIN price requirements.

        Legacy FIN accepts multiplicative shocks. Zero or negative netbacks may
        be represented only if signs never change, and a zero centre must stay
        zero in every draw. General additive/cross-zero prices need a separate
        level-price evaluator; never silently coerce them into positive shocks.
        """
        if tuple(_years(years)) != self.axis.years:
            raise ValueError('FIN evaluation years do not match price years')
        if set(requirements) != set(self.prices):
            raise ValueError('Every FIN price channel needs exactly one explicit requirement')
        if len({p.curve.price_year for p in self.prices.values()}) != 1:
            raise ValueError('FIN cannot add prices in different constant-currency years')
        native_units = {'elec':'MWh', 're':'MWh', 'h2':'kg_H2',
                        'coal':'t_coal', 'gas':'t_gas', 'co2':'tCO2'}
        prices, shocks = {}, {}
        for key, p in self.prices.items():
            req = requirements[key]
            if not isinstance(req, FINPriceRequirement):
                raise ValueError('Use a typed FIN price requirement')
            for field in req.__dataclass_fields__:
                if getattr(p.curve, field) != getattr(req, field):
                    raise ValueError(f'{key}: FIN price {field} mismatch')
            if req.currency != 'KRW':
                raise ValueError('Legacy FIN expects KRW prices; supply an explicit currency conversion')
            if key in native_units and req.quantity_unit != native_units[key]:
                raise ValueError(f'{key}: FIN physical profile requires {native_units[key]}')
            c = np.asarray(p.curve.values)
            zero = c == 0
            if np.any(p.values[:, zero] != 0):
                raise ValueError(f'{key}: nonzero realisations around a zero central price need level pricing')
            mult = np.ones(p.axis.shape)
            np.divide(p.values, c, out=mult, where=~zero)
            if not np.isfinite(mult).all() or (mult <= 0).any():
                raise ValueError(f'{key}: sign-changing price cannot use legacy positive multipliers')
            prices[key], shocks[key] = c.copy(), mult
        # simulate_cost uses the elec multiplier for both grid and renewable
        # channels. Reject separate active RE shocks rather than ignore them.
        if 're' in prices and np.any(prices['re'] != 0):
            active = prices['re'] != 0
            if 'elec' not in shocks or not np.allclose(
                    shocks['elec'][:,active], shocks['re'][:,active],rtol=1e-12,atol=1e-14):
                raise ValueError('Legacy FIN shares one elec shock with renewable power')
        return prices, shocks


def paired_cost_difference(transition, baseline, *, transition_axis, baseline_axis):
    if transition_axis != baseline_axis:
        raise ValueError('Counterfactual costs require identical labelled draws and years')
    a, b = np.asarray(transition, dtype=float), np.asarray(baseline, dtype=float)
    if a.shape != (len(transition_axis.draw_ids),) or b.shape != a.shape:
        raise ValueError('Costs must have one scalar NPV per labelled draw')
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('Counterfactual costs must be finite')
    return a-b
