"""Auditable scenario price units and currency basis, without implicit data.

Price denominators convert in the reciprocal direction to physical quantities.
Currency indices/FX and delivery mappings must be supplied with evidence.
This module does not identify a corporate contract from an IAM benchmark.
"""
from dataclasses import dataclass, replace
import numpy as np


def _positive(value, name):
    a = np.asarray(value, dtype=float)
    if not np.isfinite(a).all() or (a <= 0).any():
        raise ValueError(f'{name} must be finite and strictly positive')
    return a


def _years(values):
    a = np.asarray(values)
    if a.ndim != 1 or not len(a) or a.dtype.kind not in 'iu' or (a[1:] <= a[:-1]).any():
        raise ValueError('Years must be nonempty strictly increasing integers')
    return a


def price_unit_factor(source_unit, target_unit, *, gj_per_target_unit=None,
                      heat_basis=None, heat_evidence=None):
    """Multiply a price per source unit to obtain a price per target unit.

    A GJ-to-mass bridge needs a commodity-specific heat content, not a universal
    coal/LNG/H2 constant. Heat basis must match the original energy quotation.
    """
    if not source_unit or not target_unit:
        raise ValueError('Price denominator units are required')
    if source_unit == target_unit:
        return 1.
    exact = {('GJ', 'MWh'): 3.6, ('MWh', 'GJ'): 1/3.6,
             ('kWh', 'MWh'): 1000., ('MWh', 'kWh'): .001,
             ('tC', 'tCO2'): 12/44, ('tCO2', 'tC'): 44/12,
             ('MMBtu_IT', 'GJ'): 1/1.055056, ('GJ', 'MMBtu_IT'): 1.055056}
    if (source_unit, target_unit) in exact:
        return exact[(source_unit, target_unit)]
    if source_unit == 'GJ' and (target_unit.startswith('kg_') or target_unit.startswith('t_')):
        if gj_per_target_unit is None or heat_basis not in ('LHV', 'HHV') or not heat_evidence:
            raise ValueError('Energy-to-mass price needs heat content, basis and evidence')
        a = _positive(gj_per_target_unit, 'Heat content')
        if a.ndim:
            raise ValueError('Heat content must be a scalar for this conversion')
        return float(a)
    raise ValueError(f'Undeclared price-unit conversion: {source_unit} -> {target_unit}')


@dataclass(frozen=True)
class ScenarioPriceCurve:
    model: str
    scenario: str
    region: str
    commodity: str
    years: tuple
    values: tuple
    quantity_unit: str
    currency: str
    price_year: int
    boundary: str
    components: tuple
    source: str
    heat_basis: str | None = None

    def __post_init__(self):
        if not all(isinstance(v, str) and v.strip() for v in
                   (self.model, self.scenario, self.region, self.commodity,
                    self.quantity_unit, self.currency, self.boundary, self.source)):
            raise ValueError('Scenario/model/region/commodity/unit/boundary/source are mandatory')
        years = _years(self.years)
        values = np.asarray(self.values, dtype=float)
        if values.shape != years.shape or not np.isfinite(values).all():
            raise ValueError('Finite price values must align with years')
        if isinstance(self.price_year, bool) or not isinstance(self.price_year, int) or self.price_year < 1900:
            raise ValueError('Explicit constant-price currency year is required')
        if not self.components or len(set(self.components)) != len(self.components) or any(not c for c in self.components):
            raise ValueError('Nonempty unique cost components are required')
        if self.heat_basis not in (None, 'LHV', 'HHV'):
            raise ValueError('Heat basis must be LHV, HHV or explicitly unspecified')
        object.__setattr__(self, 'years', tuple(int(y) for y in years))
        object.__setattr__(self, 'values', tuple(float(v) for v in values))
        object.__setattr__(self, 'components', tuple(self.components))


def interpolate_curve(curve, years, *, method):
    """Explicit interpolation, no extrapolation or invented scenario label."""
    target = _years(years)
    known = np.asarray(curve.years)
    if target[0] < known[0] or target[-1] > known[-1]:
        raise ValueError('Scenario extrapolation is not authorized')
    if method == 'linear':
        result = np.interp(target, known, curve.values)
    elif method == 'previous':
        result = np.asarray(curve.values)[np.searchsorted(known, target, side='right')-1]
    else:
        raise ValueError('Declare interpolation method: linear or previous')
    return replace(curve, years=tuple(target), values=tuple(result),
                   source=curve.source + f'; derived interpolation={method}')


def convert_curve(curve, *, quantity_unit, currency, price_year,
                  currency_factor, currency_evidence, **heat_metadata):
    """Caller supplies a sourced constant-currency conversion, not nominal FX.

    currency_factor converts source constant-price currency to the requested
    constant-price currency. It cannot silently default to 1 on missing data.
    """
    if not isinstance(currency_evidence, str) or not currency_evidence.strip():
        raise ValueError('Currency conversion evidence/convention is required')
    factor = _positive(currency_factor, 'Currency conversion')
    if factor.shape not in ((), (len(curve.years),)):
        raise ValueError('Currency factor must be scalar or match curve years')
    if curve.quantity_unit == 'GJ' and (quantity_unit.startswith('kg_') or quantity_unit.startswith('t_')):
        if curve.heat_basis is None or heat_metadata.get('heat_basis') != curve.heat_basis:
            raise ValueError('Heat basis must match the source quotation before mass conversion')
    unit = price_unit_factor(curve.quantity_unit, quantity_unit, **heat_metadata)
    result = np.asarray(curve.values) * factor * unit
    return replace(curve, values=tuple(result), quantity_unit=quantity_unit,
                   currency=currency, price_year=price_year,
                   source=curve.source + '; conversion: ' + currency_evidence)


def real_currency_factor(*, foreign_index_source, foreign_index_target,
                         local_per_foreign_base, evidence):
    """Constant-price conversion with fixed target-base-year FX.

    Foreign price in source-year money -> target-year foreign money -> target
    year local money. This reporting convention introduces no future FX risk.
    """
    if not evidence:
        raise ValueError('Index and base-year FX evidence required')
    return (_positive(foreign_index_target, 'Foreign target index') /
            _positive(foreign_index_source, 'Foreign source index') *
            _positive(local_per_foreign_base, 'Base-year FX'))


def stochastic_real_currency_factor(*, foreign_index_source, foreign_index_at_t,
                                    nominal_local_per_foreign, local_index_at_t,
                                    local_index_base, evidence):
    """Foreign real source year -> foreign nominal t -> local nominal t -> local real base.

    Time/path alignment must be checked by the caller before multiplication;
    returned factors do not carry path IDs. Marginal mean corrections for prices
    and FX do not in general preserve the mean of their correlated product.
    """
    if not evidence:
        raise ValueError('Inflation and nominal FX conventions/evidence required')
    return (_positive(foreign_index_at_t, 'Foreign index at t') /
            _positive(foreign_index_source, 'Foreign source index') *
            _positive(nominal_local_per_foreign, 'Nominal FX') *
            _positive(local_index_base, 'Local base index') /
            _positive(local_index_at_t, 'Local index at t'))


def add_delivered_components(*curves):
    """Add already-mapped, nonoverlapping components of one delivered commodity.

    This deliberately rejects raw iron ore + pellet quotations with different
    commodity/boundary labels. A sourced grade/delivery bridge must map them
    first; changing units alone never turns a benchmark into a plant contract.
    """
    if not curves:
        raise ValueError('At least one mapped price component required')
    reference = curves[0]
    fields = ('model', 'scenario', 'region', 'commodity', 'years', 'quantity_unit',
              'currency', 'price_year', 'boundary', 'heat_basis')
    seen = set()
    for curve in curves:
        if any(getattr(curve, key) != getattr(reference, key) for key in fields):
            raise ValueError('Price components must share scenario, units, currency and mapped boundary')
        if seen.intersection(curve.components):
            raise ValueError('Overlapping cost components would double count price')
        seen.update(curve.components)
    return replace(reference, values=tuple(np.sum([c.values for c in curves], axis=0)),
                   components=tuple(sorted(seen)), source='; '.join(c.source for c in curves))
