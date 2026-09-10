"""Cashflow identities and rejection of economically ambiguous joins.

All fixtures are arithmetic examples, not calibrated corporate inputs.
"""
from dataclasses import replace
from fractions import Fraction

import numpy as np
import pytest

from cap.fx_settlement import (PathValues, FXQuotes, PricePath, PriceIndex,
                               InvoiceFlow, settle_invoices)

DATES = ('2027-01-01', '2027-02-01', '2027-03-01')
IDS = ('state_a', 'state_b')


def paths(values, **kwargs):
    return PathValues(np.broadcast_to(values, (2, 3)),
                      kwargs.get('path_ids', IDS), kwargs.get('dates', DATES),
                      kwargs.get('sample_id', 'arithmetic_example'))


def fixtures(real=False):
    fx = FXQuotes('USD', {'USD': paths(1),
                         'KRW': paths([[1000, 1200, 1500], [1000, 900, 800]]),
                         'EUR': paths([[.8, 1, 1.2], [.8, .75, .7]])})
    price = PricePath('USD', 'tonne', paths([[10, 20, 30], [20, 30, 40]]),
                      2020 if real else None)
    flow = InvoiceFlow('feedstock', 'purchase', (2,), 'tonne', (DATES[0],),
                       (DATES[1],), price, 'Explicit arithmetic fixture')
    return fx, flow, paths([1, .9, .8])


def test_pricing_inflation_then_payment_fx_deflator_and_discount():
    fx, flow, discount = fixtures(real=True)
    usd = PriceIndex('USD', 2020, paths([2, 3, 4]))
    krw = PriceIndex('KRW', 2020, paths([1, 2, 4]))
    result = settle_invoices([flow], fx, 'KRW', discount, 2020,
                             {('USD', 2020): usd}, krw)
    # Independent exact arithmetic: q * Jan real price * Jan US index *
    # Feb KRW/USD / Feb KRW index * Feb discount. No January payment.
    expected = [float(Fraction(2) * p * 2 * x / 2 * Fraction(9, 10))
                for p, x in [(10, 1200), (20, 900)]]
    np.testing.assert_allclose(result.npv_by_path, expected)
    np.testing.assert_allclose(result.cash_by_date, [[0, 24000, 0], [0, 36000, 0]])
    assert result.real_base_year == 2020


def test_nominal_and_real_invoice_representations_agree():
    fx, real_flow, discount = fixtures(real=True)
    index = PriceIndex('USD', 2020, paths([2, 3, 4]))
    nominal_flow = replace(real_flow, price=PricePath('USD', 'tonne',
        paths(real_flow.price.paths.values * index.paths.values), None))
    a = settle_invoices([real_flow], fx, 'KRW', discount,
                        invoice_indices={('USD', 2020): index})
    b = settle_invoices([nominal_flow], fx, 'KRW', discount)
    np.testing.assert_array_equal(a.cash_by_date, b.cash_by_date)


def test_real_and_nominal_discount_conventions_can_give_identical_pv():
    fx, flow, nominal_discount = fixtures()
    index = PriceIndex('KRW', 2020, paths([1, 2, 4]))
    # At an evaluation origin with index 1: D_real(t) = D_nominal(t)*I(t).
    real_discount = paths(nominal_discount.values * index.paths.values)
    nominal = settle_invoices([flow], fx, 'KRW', nominal_discount)
    real = settle_invoices([flow], fx, 'KRW', real_discount, 2020,
                           evaluation_index=index)
    np.testing.assert_allclose(real.npv_by_path, nominal.npv_by_path)


def test_pathwise_cross_inverse_triangle_and_same_currency():
    fx, flow, discount = fixtures()
    np.testing.assert_allclose(fx.rate('USD', 'KRW') * fx.rate('KRW', 'USD'), 1)
    np.testing.assert_allclose(fx.rate('EUR', 'USD') * fx.rate('USD', 'KRW'),
                               fx.rate('EUR', 'KRW'))
    local_flow = replace(flow, price=replace(flow.price, currency='KRW'))
    result = settle_invoices([local_flow], fx, 'KRW', discount)
    np.testing.assert_allclose(result.npv_by_path, [18, 36])


def test_equal_opposite_external_legs_cancel_in_every_state():
    fx, flow, discount = fixtures()
    receipt = replace(flow, flow_id='netback', role='export_netback')
    result = settle_invoices([flow, receipt], fx, 'KRW', discount)
    np.testing.assert_array_equal(result.npv_by_path, 0)
    np.testing.assert_array_equal(result.flow_cash_by_date['feedstock'],
                                  -result.flow_cash_by_date['netback'])


def test_multiple_invoices_on_same_payment_date_accumulate():
    fx, flow, discount = fixtures()
    flow = replace(flow, quantities=(2, 3), pricing_dates=(DATES[0], DATES[1]),
                   settlement_dates=(DATES[1], DATES[1]))
    result = settle_invoices([flow], fx, 'KRW', discount)
    np.testing.assert_allclose(result.npv_by_path,
        [(2*10 + 3*20)*1200*.9, (2*20 + 3*30)*900*.9])


def test_joint_price_fx_mean_is_not_recentered():
    fx, flow, _ = fixtures()
    factors = paths([[.5]*3, [1.5]*3])
    fx = FXQuotes('USD', {'USD': paths(1), 'KRW': factors})
    flow = replace(flow, quantities=(1,), price=replace(flow.price, paths=factors))
    result = settle_invoices([flow], fx, 'KRW', paths(1))
    np.testing.assert_array_equal(result.npv_by_path, [.25, 2.25])
    assert result.npv_by_path.mean() == 1.25  # E[P]E[X] + Cov(P,X)


def test_negative_price_is_preserved_as_a_receipt_on_purchase():
    fx, flow, discount = fixtures()
    flow = replace(flow, price=replace(flow.price, paths=paths(-10)))
    assert (settle_invoices([flow], fx, 'KRW', discount).npv_by_path < 0).all()


@pytest.mark.parametrize('change', [
    {'path_ids': tuple(reversed(IDS))}, {'sample_id': 'another_scenario'},
    {'dates': ('2028-01-01', '2028-02-01', '2028-03-01')},
])
def test_same_shape_but_different_path_identity_is_rejected(change):
    fx, flow, discount = fixtures()
    bad = paths(flow.price.paths.values, **change)
    with pytest.raises(ValueError, match='must match exactly'):
        settle_invoices([replace(flow, price=replace(flow.price, paths=bad))],
                        fx, 'KRW', discount)


@pytest.mark.parametrize('change,message', [
    ({'quantity_unit': 'kilogram'}, 'units must match'),
    ({'role': 'internal_use'}, 'Only external'),
    ({'evidence': ''}, 'evidence'),
    ({'quantities': (-1,)}, 'nonnegative'),
    ({'quantities': ((1, 2), (3, 4))}, 'fixed profile'),
    ({'quantities': (1, 2)}, 'Each quantity'),
    ({'settlement_dates': ('2030-01-01',)}, 'supplied calendar'),
    ({'pricing_dates': (DATES[2],)}, 'prepayment'),
])
def test_ambiguous_or_invalid_invoice_is_rejected(change, message):
    fx, flow, discount = fixtures()
    with pytest.raises(ValueError, match=message):
        settle_invoices([replace(flow, **change)], fx, 'KRW', discount)


def test_duplicate_stream_and_missing_currency_rejected():
    fx, flow, discount = fixtures()
    with pytest.raises(ValueError, match='Duplicate'):
        settle_invoices([flow, flow], fx, 'KRW', discount)
    with pytest.raises(ValueError, match='currency quotes'):
        settle_invoices([replace(flow, price=replace(flow.price, currency='JPY'))],
                        fx, 'KRW', discount)


@pytest.mark.parametrize('bad', [0, -1])
def test_nonpositive_fx_index_and_discount_rejected(bad):
    fx, flow, _ = fixtures()
    with pytest.raises(ValueError, match='positive'):
        FXQuotes('USD', {'USD': paths(1), 'KRW': paths(bad)})
    with pytest.raises(ValueError, match='positive'):
        PriceIndex('USD', 2020, paths(bad))
    with pytest.raises(ValueError, match='positive'):
        settle_invoices([flow], fx, 'KRW', paths(bad))


def test_anchor_must_be_explicit_unit_quote():
    with pytest.raises(ValueError, match='Explicit anchor'):
        FXQuotes('USD', {'KRW': paths(1000)})
    with pytest.raises(ValueError, match='equal one'):
        FXQuotes('USD', {'USD': paths(2), 'KRW': paths(1000)})


def test_missing_or_wrong_real_price_bases_rejected():
    fx, flow, discount = fixtures(real=True)
    with pytest.raises(ValueError, match='invoice-currency'):
        settle_invoices([flow], fx, 'KRW', discount)
    with pytest.raises(ValueError, match='invoice-currency'):
        settle_invoices([flow], fx, 'KRW', discount,
            invoice_indices={('USD', 2020): PriceIndex('USD', 2021, paths(1))})
    with pytest.raises(ValueError, match='evaluation-currency'):
        settle_invoices([flow], fx, 'KRW', discount, 2020,
                        evaluation_index=PriceIndex('JPY', 2020, paths(1)))
    with pytest.raises(ValueError, match='nominal output'):
        settle_invoices([flow], fx, 'KRW', discount,
                        evaluation_index=PriceIndex('KRW', 2020, paths(1)))


def test_nonfinite_and_overflow_rejected():
    with pytest.raises(ValueError, match='Finite'):
        paths(np.nan)
    fx, flow, discount = fixtures()
    flow = replace(flow, price=replace(flow.price, paths=paths(1e308)))
    with pytest.raises(ValueError, match='overflow'):
        settle_invoices([flow], fx, 'KRW', discount)


def test_inputs_are_copied_and_results_are_read_only():
    source = np.ones((2, 3))
    p = paths(source)
    source[:] = 2
    np.testing.assert_array_equal(p.values, 1)
    fx, flow, discount = fixtures()
    result = settle_invoices([flow], fx, 'KRW', discount)
    with pytest.raises(ValueError, match='read-only'):
        result.npv_by_path[0] = 42
