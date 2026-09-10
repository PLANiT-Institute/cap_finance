from dataclasses import replace

import numpy as np
import pytest

from cap import config as C
from cap.commodity_ledger import CommodityFlow
from cap.fx_settlement import PathValues, FXQuotes, PricePath, PriceIndex
from cap.invoice_fin import InvoiceTerms, simulate_cost_with_invoices, paired_incremental_cost
from cap.plancost import PlanProfile, simulate_cost

ANNUAL = ('2027-01-01', '2028-01-01')
CALENDAR = ('2027-01-01', '2027-07-01', '2028-01-01', '2029-01-01')
IDS = ('joint_a', 'joint_b')


def grid(values, dates=CALENDAR, ids=IDS, sample='arithmetic_example'):
    return PathValues(np.broadcast_to(values, (2, len(dates))), ids, dates, sample)


def fixture():
    cfg = C.load(data_dir='data/sample', discount_rate=.1,
                 carbon_accounting_mode='gross_obligation_proxy')
    cfg['years'] = dict(start=2027, end=2028)
    z = np.zeros(2)
    p = PlanProfile(np.ones(2), z, z, z, z, {}, {}, z, 0., 0, 0,
        additional_commodity_flows=(
            CommodityFlow('oil', 'oil', np.full(2, 2.), 'tonne', 'purchased', 'Toy quantity'),
            CommodityFlow('sale', 'netback', -np.ones(2), 'tonne', 'export_netback', 'Toy netback')),
        profile_years=(2027, 2028), embedded_price_basis={})
    prices = {k: np.zeros(2) for k in ['elec', 're', 'h2', 'coal', 'gas', 'co2']}
    prices.update(elec=np.full(2, 100.), oil=np.full(2, 10000.), netback=np.full(2, 4000.))
    shocks = {k: grid(1, ANNUAL) for k in ['elec', 'h2', 'capex']}
    shocks.update(oil=grid([[1, 2], [2, 1]], ANNUAL),
                  netback=grid([[1, 2], [2, 1]], ANNUAL))
    fx = FXQuotes('USD', {'USD': grid(1), 'KRW': grid(1000)})
    price = grid([[10, 15, 20, 25], [20, 25, 10, 15]])
    terms = {f.flow_id: InvoiceTerms(PricePath('USD', 'tonne',
                 grid(price.values * (1 if f.flow_id == 'oil' else .4)), None),
                 ANNUAL, ANNUAL, 'Toy invoice conditions') for f in p.additional_commodity_flows}
    kwargs = dict(terms=terms, fx=fx, discount_factors=grid([1, 1.1**-.5, 1/1.1, 1/1.1**2]),
                   real_base_year=None, basis_evidence='Explicit nominal toy KRW prices')
    return p, prices, shocks, cfg, kwargs


def run(p, prices, shocks, cfg, kwargs):
    return simulate_cost_with_invoices(p, prices, shocks, {'subsidy': {}}, cfg, **kwargs)


def test_fixed_fx_reproduces_legacy_full_cost_without_double_charging():
    p, prices, shocks, cfg, kwargs = fixture()
    legacy = simulate_cost(p, prices, {k:v.values for k,v in shocks.items()}, {'subsidy': {}}, cfg)
    result = run(p, prices, shocks, cfg, kwargs)
    np.testing.assert_allclose(result.npv_krw_billion, legacy, rtol=1e-14)
    # Once replaced, obsolete KRW commodity price slots are not billed as well.
    changed = {**prices, 'oil': np.full(2, 1e100), 'netback': np.full(2, 1e100)}
    np.testing.assert_array_equal(run(p, changed, shocks, cfg, kwargs).npv_krw_billion,
                                   result.npv_krw_billion)


def test_common_invoice_cash_cancels_even_with_joint_price_fx_shocks():
    p, prices, shocks, cfg, kwargs = fixture()
    kwargs['fx'] = FXQuotes('USD', {'USD': grid(1),
        'KRW': grid([[1000, 1200, 1400, 1600], [1800, 1500, 1200, 900]])})
    baseline = run(p, prices, shocks, cfg, kwargs)
    alternative = run(replace(p, grid_mwh=p.grid_mwh*2), prices, shocks, cfg, kwargs)
    delta = paired_incremental_cost(alternative, baseline)
    np.testing.assert_allclose(delta, 100*(1+1/1.1)*1e-9, atol=1e-20)
    np.testing.assert_array_equal(alternative.settlement.cash_by_date,
                                   baseline.settlement.cash_by_date)


def test_equal_quantity_does_not_cancel_with_changed_payment_date():
    p, prices, shocks, cfg, kwargs = fixture()
    kwargs['fx'] = FXQuotes('USD', {'USD': grid(1),
        'KRW': grid([[1000, 1200, 1400, 1600], [1800, 1500, 1200, 900]])})
    baseline = run(p, prices, shocks, cfg, kwargs)
    t = dict(kwargs['terms'])
    t['oil'] = replace(t['oil'], settlement_dates=('2027-07-01', '2029-01-01'))
    alternative = run(p, prices, shocks, cfg, {**kwargs, 'terms': t})
    delta = paired_incremental_cost(alternative, baseline)
    # Second payment lies beyond the production horizon but remains in NPV.
    expected = np.array([
        2*10*(1200/1.1**.5 - 1000)+2*20*(1600/1.1**2 - 1400/1.1),
        2*20*(1500/1.1**.5 - 1800)+2*10*(900/1.1**2 - 1200/1.1),
    ])*1e-9
    np.testing.assert_allclose(delta, expected, rtol=1e-13)
    assert (alternative.settlement.cash_by_date[:, -1] > 0).all()


def test_unchanged_contract_price_requoted_in_same_currency_is_equivalent():
    p, prices, shocks, cfg, kwargs = fixture()
    base = run(p, prices, shocks, cfg, kwargs)
    t = {k: replace(v, price=PricePath('KRW', 'tonne', grid(v.price.paths.values*1000), None))
         for k, v in kwargs['terms'].items()}
    local = run(p, prices, shocks, cfg, {**kwargs, 'terms': t})
    np.testing.assert_allclose(paired_incremental_cost(local, base), 0, atol=1e-20)


@pytest.mark.parametrize('change', ['raw_array', 'path_order', 'sample', 'annual_dates'])
def test_noninvoice_shocks_cannot_silently_join_different_paths(change):
    p, prices, shocks, cfg, kwargs = fixture()
    shocks = dict(shocks)
    shocks['elec'] = {
        'raw_array': np.ones((2,2)),
        'path_order': grid(1, ANNUAL, tuple(reversed(IDS))),
        'sample': grid(1, ANNUAL, sample='unpaired'),
        'annual_dates': grid(1, ('2027-07-01','2028-01-01')),
    }[change]
    with pytest.raises(ValueError):
        run(p, prices, shocks, cfg, kwargs)


@pytest.mark.parametrize('change', ['missing', 'extra', 'wrong_role', 'wrong_year', 'freeze', 'discount', 'basis', 'evidence'])
def test_replacement_scope_and_accounting_fail_closed(change):
    p, prices, shocks, cfg, kwargs = fixture()
    if change == 'missing': kwargs['terms'] = {'oil': kwargs['terms']['oil']}
    if change == 'extra': kwargs['terms']['phantom'] = kwargs['terms']['oil']
    if change == 'wrong_role': p = replace(p, additional_commodity_flows=(replace(p.additional_commodity_flows[0], role='internal'), p.additional_commodity_flows[1]))
    if change == 'wrong_year': kwargs['terms']['oil'] = replace(kwargs['terms']['oil'], pricing_dates=('2028-01-01','2029-01-01'))
    if change == 'freeze': kwargs['freeze'] = 'oil'
    if change == 'discount': kwargs['discount_factors'] = grid(1)
    if change == 'basis': kwargs['real_base_year'] = 2020  # No real-price index supplied.
    if change == 'evidence': kwargs['basis_evidence'] = ''
    with pytest.raises(ValueError):
        run(p, prices, shocks, cfg, kwargs)


def test_paired_difference_requires_same_basis_and_discount_bundle():
    p, prices, shocks, cfg, kwargs = fixture()
    base = run(p, prices, shocks, cfg, kwargs)
    real = run(p, prices, shocks, cfg, {**kwargs, 'real_base_year': 2020,
        'evaluation_index': PriceIndex('KRW', 2020, grid(1))})
    with pytest.raises(ValueError, match='same currency, basis'):
        paired_incremental_cost(real, base)
    changed = run(p, prices, shocks, cfg, {**kwargs,
        'discount_factors': grid([1, .8, 1/1.1, 1/1.1**2])})
    with pytest.raises(ValueError, match='same discount'):
        paired_incremental_cost(changed, base)
