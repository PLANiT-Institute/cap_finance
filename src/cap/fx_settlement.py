"""Explicit fixed-quantity invoice and settlement cashflows in a common currency.

No prices, FX forecasts, inflation, probabilities, hedge terms or corporate
exposure shares are inferred. FX quotes are nominal currency units per one
anchor-currency unit. Cross rates come from this spanning set without reanchoring.
"""
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Mapping

import numpy as np


def _label(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be an explicit nonempty label')


def _currency(value):
    if not isinstance(value, str) or len(value) != 3 or not value.isascii() or not value.isalpha() or not value.isupper():
        raise ValueError('Currency must be an explicit three-letter uppercase code')


def _year(value):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or not 1 <= value <= 9999:
        raise ValueError('Price/index base year must be an explicit calendar year')


@dataclass(frozen=True)
class PathValues:
    """Read-only values with scenario/sample, path and calendar identity."""
    values: np.ndarray
    path_ids: tuple[str, ...]
    dates: tuple[str, ...]
    sample_id: str

    def __post_init__(self):
        _label(self.sample_id, 'Scenario/sample ID')
        ids, dates = tuple(self.path_ids), tuple(self.dates)
        if not ids or any(not isinstance(x, str) or not x.strip() for x in ids) or len(set(ids)) != len(ids):
            raise ValueError('Nonempty unique path IDs are required')
        try:
            calendar = [date.fromisoformat(x) for x in dates]
        except (TypeError, ValueError) as exc:
            raise ValueError('Dates must be ISO calendar dates') from exc
        if not dates or any(x.isoformat() != y for x, y in zip(calendar, dates)) or calendar != sorted(set(calendar)):
            raise ValueError('Dates must be unique and chronological ISO calendar dates')
        a = np.array(self.values, dtype=float, copy=True)
        if a.shape != (len(ids), len(dates)) or not np.isfinite(a).all():
            raise ValueError('Finite values must match all path IDs and dates exactly')
        a.setflags(write=False)
        object.__setattr__(self, 'values', a)
        object.__setattr__(self, 'path_ids', ids)
        object.__setattr__(self, 'dates', dates)

    def align(self, other):
        if (self.sample_id, self.path_ids, self.dates) != (other.sample_id, other.path_ids, other.dates):
            raise ValueError('Scenario/sample, path order and calendar must match exactly')


@dataclass(frozen=True)
class FXQuotes:
    """Nominal units_per_anchor includes an exact unit quote for the anchor."""
    anchor_currency: str
    units_per_anchor: Mapping[str, PathValues]

    def __post_init__(self):
        _currency(self.anchor_currency)
        quotes = dict(self.units_per_anchor)
        if self.anchor_currency not in quotes:
            raise ValueError('Explicit anchor quote is required')
        anchor = quotes[self.anchor_currency]
        if not np.all(anchor.values == 1):
            raise ValueError('Anchor quote must equal one in every state and date')
        for currency, paths in quotes.items():
            _currency(currency)
            anchor.align(paths)
            if (paths.values <= 0).any():
                raise ValueError('Nominal FX quotes must be strictly positive')
        object.__setattr__(self, 'units_per_anchor', MappingProxyType(quotes))

    @property
    def grid(self):
        return self.units_per_anchor[self.anchor_currency]

    def rate(self, invoice_currency, evaluation_currency):
        """Evaluation-currency units per one invoice-currency unit, pathwise."""
        if invoice_currency not in self.units_per_anchor or evaluation_currency not in self.units_per_anchor:
            raise ValueError('Both invoice and evaluation currency quotes are required')
        with np.errstate(over='ignore', divide='ignore', invalid='ignore'):
            result = self.units_per_anchor[evaluation_currency].values / self.units_per_anchor[invoice_currency].values
        if not np.isfinite(result).all() or (result <= 0).any():
            raise ValueError('Cross-rate overflow or underflow; check quote scale')
        return result


@dataclass(frozen=True)
class PricePath:
    currency: str
    quantity_unit: str
    paths: PathValues
    real_base_year: int | None  # None means nominal invoice-currency prices.

    def __post_init__(self):
        _currency(self.currency)
        _label(self.quantity_unit, 'Price quantity unit')
        if self.real_base_year is not None:
            _year(self.real_base_year)


@dataclass(frozen=True)
class PriceIndex:
    currency: str
    base_year: int
    paths: PathValues

    def __post_init__(self):
        _currency(self.currency)
        _year(self.base_year)
        if (self.paths.values <= 0).any():
            raise ValueError('Price indices must be strictly positive')


@dataclass(frozen=True)
class InvoiceFlow:
    flow_id: str
    role: str  # purchase or export_netback; quantities themselves are nonnegative.
    quantities: tuple[float, ...]
    quantity_unit: str
    pricing_dates: tuple[str, ...]
    settlement_dates: tuple[str, ...]
    price: PricePath
    evidence: str


@dataclass(frozen=True)
class SettlementResult:
    currency: str
    real_base_year: int | None
    sample_id: str
    path_ids: tuple[str, ...]
    dates: tuple[str, ...]
    cash_by_date: np.ndarray  # Positive cost, negative cash receipt.
    discounted_cash_by_date: np.ndarray
    npv_by_path: np.ndarray
    flow_cash_by_date: Mapping[str, np.ndarray]


def settle_invoices(flows, fx, evaluation_currency, discount_factors,
                    output_real_base_year=None, invoice_indices=None, evaluation_index=None):
    """Value fixed invoices on settlement dates, then discount those cashflows.

    real invoice price at pricing date -> nominal invoice amount -> nominal FX at
    payment date -> optional real evaluation currency at payment date -> discount.
    Discount factors must already use the same nominal/real convention as output.
    Their economic calibration and the normalization of index base years are the
    caller's explicit responsibility, not inferred from the arrays.

    Each flow ID is billed once. Indices are indexed by (invoice currency, base
    year). Prepayments, adaptive quantities, derivatives and financing legs need
    separate models; settlement before pricing is rejected here.
    """
    _currency(evaluation_currency)
    grid = fx.grid
    grid.align(discount_factors)
    if (discount_factors.values <= 0).any():
        raise ValueError('Discount factors must be positive and aligned with settlement dates')
    indices = dict(invoice_indices or {})
    if output_real_base_year is not None:
        _year(output_real_base_year)
        if evaluation_index is None or (evaluation_index.currency, evaluation_index.base_year) != (evaluation_currency, output_real_base_year):
            raise ValueError('Matching evaluation-currency price index and base year are required')
        grid.align(evaluation_index.paths)
        denominator = evaluation_index.paths.values
    else:
        if evaluation_index is not None:
            raise ValueError('A nominal output must not silently apply a real-price deflator')
        denominator = np.ones_like(grid.values)
    if evaluation_currency not in fx.units_per_anchor:
        raise ValueError('Evaluation currency quote is required')
    flows = tuple(flows)
    if not flows:
        raise ValueError('At least one explicitly identified invoice flow is required')
    positions = {value: i for i, value in enumerate(grid.dates)}
    result = np.zeros_like(grid.values)
    legs = {}
    for flow in flows:
        _label(flow.flow_id, 'Flow ID')
        _label(flow.evidence, 'Flow evidence')
        if flow.flow_id in legs:
            raise ValueError('Duplicate flow ID would bill the same stream twice')
        if flow.role not in ('purchase', 'export_netback'):
            raise ValueError('Only external purchases and export netbacks belong in the invoice ledger')
        if flow.quantity_unit != flow.price.quantity_unit:
            raise ValueError('Quantity and price denominator units must match exactly')
        grid.align(flow.price.paths)
        q = np.asarray(flow.quantities, dtype=float)
        if q.ndim != 1 or not len(q) or not np.isfinite(q).all() or (q < 0).any():
            raise ValueError('Quantities must be a nonempty finite nonnegative fixed profile')
        if not len(q) == len(flow.pricing_dates) == len(flow.settlement_dates):
            raise ValueError('Each quantity needs explicit pricing and settlement dates')
        try:
            priced = [positions[x] for x in flow.pricing_dates]
            paid = [positions[x] for x in flow.settlement_dates]
        except (KeyError, TypeError) as exc:
            raise ValueError('Pricing and payment dates must be in the supplied calendar') from exc
        if any(b < a for a, b in zip(priced, paid)):
            raise ValueError('Settlement before pricing requires an explicit prepayment model')
        base = flow.price.real_base_year
        if base is None:
            numerator = np.ones_like(grid.values)
        else:
            key = (flow.price.currency, base)
            index = indices.get(key)
            if index is None or (index.currency, index.base_year) != key:
                raise ValueError('Matching invoice-currency price index and base year are required')
            grid.align(index.paths)
            numerator = index.paths.values
        cross = fx.rate(flow.price.currency, evaluation_currency)
        sign = 1 if flow.role == 'purchase' else -1
        cash = np.zeros_like(grid.values)
        with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
            for quantity, a, b in zip(q, priced, paid):
                cash[:, b] += sign * quantity * flow.price.paths.values[:, a] * numerator[:, a] * cross[:, b] / denominator[:, b]
        if not np.isfinite(cash).all():
            raise ValueError('Cashflow overflow; inspect price, FX and index scales')
        with np.errstate(over='ignore', invalid='ignore'):
            result += cash
        cash.setflags(write=False)
        legs[flow.flow_id] = cash
    with np.errstate(over='ignore', invalid='ignore'):
        discounted = result * discount_factors.values
        npv = discounted.sum(axis=1)
    if not np.isfinite(discounted).all() or not np.isfinite(npv).all():
        raise ValueError('Aggregate discounted cashflow overflow')
    for a in (result, discounted, npv):
        a.setflags(write=False)
    return SettlementResult(evaluation_currency, output_real_base_year, grid.sample_id,
                            grid.path_ids, grid.dates, result, discounted, npv,
                            MappingProxyType(legs))
