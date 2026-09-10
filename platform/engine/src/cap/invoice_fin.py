"""Replace FIN's additional commodity ledger with explicit invoice settlement.

The remaining FIN channels retain their existing annual KRW accounting. This
adapter does not reinterpret embedded fuels, PPA/CCfD, capital or carbon costs.
It requires an explicit declaration that their price basis matches the output.
"""
from dataclasses import dataclass, replace
from typing import Mapping

import numpy as np

from .fx_settlement import PathValues, PricePath, InvoiceFlow, SettlementResult, settle_invoices
from .plancost import simulate_cost


@dataclass(frozen=True)
class InvoiceTerms:
    price: PricePath
    pricing_dates: tuple[str, ...]
    settlement_dates: tuple[str, ...]
    evidence: str


@dataclass(frozen=True)
class InvoiceFINResult:
    npv_krw_billion: np.ndarray
    remaining_fin_npv_krw_billion: np.ndarray
    settlement: SettlementResult
    discount_factors: PathValues
    annual_dates: tuple[str, ...]
    basis_evidence: str


def _same_sample(a, b):
    if (a.sample_id, a.path_ids) != (b.sample_id, b.path_ids):
        raise ValueError('FIN and invoice scenarios/samples and ordered path IDs must match')


def simulate_cost_with_invoices(profile, prices, shocks: Mapping[str, PathValues],
        support, cfg, *, terms: Mapping[str, InvoiceTerms], fx,
        discount_factors: PathValues, real_base_year, basis_evidence,
        invoice_indices=None, evaluation_index=None, freeze=None):
    """Return total FIN cost, replacing every additional commodity flow once.

    Signed annual CommodityFlow quantities become nonnegative InvoiceFlow
    quantities with purchase/export roles. Each annual quantity has one explicit
    pricing date within its production year and one payment date. Split billing
    must first split the annual physical stream into separately identified flows.

    All noninvoice shock arrays carry annual dates and the same sample/path IDs
    as FX. The invoice calendar may be finer and include payments after FIN's last
    production year. Its discount factors at annual FIN dates must equal FIN's
    configured factors. No payment is silently truncated at the production end.

    real_base_year=None explicitly declares nominal KRW for remaining FIN costs;
    an integer declares that real KRW basis. basis_evidence is a caller-provided
    accounting declaration, not a machine verification of economic calibration.
    """
    if not isinstance(basis_evidence, str) or not basis_evidence.strip():
        raise ValueError('Explicit evidence for the common FIN/invoice price basis is required')
    years = tuple(range(cfg.years.start, cfg.years.end + 1))
    annual_dates = tuple(f'{year:04d}-01-01' for year in years)
    if not shocks:
        raise ValueError('Explicit FIN shock paths are required')
    for shock in shocks.values():
        if not isinstance(shock, PathValues):
            raise ValueError('Every FIN shock must carry sample/path/calendar identity')
        _same_sample(fx.grid, shock)
        if shock.dates != annual_dates:
            raise ValueError('FIN shock dates must exactly match annual production dates')
    fx.grid.align(discount_factors)
    try:
        annual_positions = [fx.grid.dates.index(d) for d in annual_dates]
    except ValueError as exc:
        raise ValueError('Invoice calendar must include all annual FIN dates') from exc
    expected_discount = (1. + cfg.discount_rate) ** -np.arange(len(years), dtype=float)
    if not np.isfinite(expected_discount).all() or (expected_discount <= 0).any():
        raise ValueError('Invalid FIN discount convention')
    if not np.allclose(discount_factors.values[:, annual_positions], expected_discount,
                       rtol=1e-12, atol=0):
        raise ValueError('Invoice and annual FIN discount conventions differ')
    flows = tuple(profile.additional_commodity_flows)
    ids = [f.flow_id for f in flows]
    if not ids or len(set(ids)) != len(ids) or set(terms) != set(ids):
        raise ValueError('Exactly one terms record per unique additional commodity flow is required')
    if freeze is not None and freeze in {f.price_key for f in flows}:
        raise ValueError('Invoice price/FX freezing needs an explicit counterfactual price bundle')
    invoices = []
    for flow in flows:
        contract = terms[flow.flow_id]
        q = np.asarray(flow.quantity, dtype=float)
        if q.shape != (len(years),) or not np.isfinite(q).all():
            raise ValueError('Commodity quantities must cover the modeled years')
        if flow.role == 'purchased' and (q >= 0).all():
            role = 'purchase'
        elif flow.role == 'export_netback' and (q <= 0).all():
            role = 'export_netback'
        else:
            raise ValueError('External commodity role and signed quantities must agree')
        if not isinstance(flow.evidence, str) or not flow.evidence.strip() or not isinstance(contract.evidence, str) or not contract.evidence.strip():
            raise ValueError('Both physical-flow and invoice-terms evidence are required')
        if (len(contract.pricing_dates) != len(years) or
                any(d not in fx.grid.dates or int(d[:4]) != y
                    for d, y in zip(contract.pricing_dates, years))):
            raise ValueError('Each annual quantity needs a pricing date in its production year')
        invoices.append(InvoiceFlow(flow.flow_id, role, tuple(abs(q)), flow.quantity_unit,
            contract.pricing_dates, contract.settlement_dates, contract.price,
            flow.evidence + ' | ' + contract.evidence))
    settlement = settle_invoices(invoices, fx, 'KRW', discount_factors,
        output_real_base_year=real_base_year, invoice_indices=invoice_indices,
        evaluation_index=evaluation_index)
    # Remove the old entire additional ledger before pricing the retained FIN.
    # Never add an FX surcharge on top of the already charged commodity stream.
    remainder = simulate_cost(replace(profile, additional_commodity_flows=()),
        prices, {k: v.values for k, v in shocks.items()}, support, cfg, freeze=freeze)
    with np.errstate(over='ignore', invalid='ignore'):
        total = remainder + settlement.npv_by_path * 1e-9  # KRW -> KRW billion
    if not np.isfinite(total).all():
        raise ValueError('Nonfinite combined FIN and invoice cost')
    total.setflags(write=False)
    remainder.setflags(write=False)
    return InvoiceFINResult(total, remainder, settlement, discount_factors,
                            annual_dates, basis_evidence)


def paired_incremental_cost(alternative: InvoiceFINResult, baseline: InvoiceFINResult):
    """Same-state total cost difference; no assumption that common quantity cancels."""
    a, b = alternative.settlement, baseline.settlement
    if (a.currency, a.real_base_year, a.sample_id, a.path_ids, a.dates,
        alternative.annual_dates) != (b.currency, b.real_base_year, b.sample_id,
        b.path_ids, b.dates, baseline.annual_dates):
        raise ValueError('Paired alternatives need the same currency, basis, sample and calendars')
    if not np.array_equal(alternative.discount_factors.values, baseline.discount_factors.values):
        raise ValueError('Paired alternatives must use the same discount factors')
    with np.errstate(over='ignore', invalid='ignore'):
        delta = alternative.npv_krw_billion - baseline.npv_krw_billion
    if not np.isfinite(delta).all():
        raise ValueError('Nonfinite paired incremental cost')
    delta.setflags(write=False)
    return delta
