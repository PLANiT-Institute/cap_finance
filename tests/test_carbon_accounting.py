import numpy as np
import pytest

from cap.carbon_accounting import allowance_payment, incremental_allowance_payment, free_allowance_path


def test_free_allocation_is_not_a_discount_to_the_marginal_price():
    # 100 free units against 100 baseline emissions: baseline net payment zero.
    # Cutting emissions to 80 generates a 20-unit surplus worth 20 * price.
    assert allowance_payment(100, 30, 100) == 0
    assert incremental_allowance_payment(80, 100, 30, 100, 100) == -600


def test_fixed_allocations_cancel_pathwise_but_adjusted_allocations_do_not():
    prices = np.array([[20, 40], [50, 80]])
    plan, base = np.array([80, 60]), np.array([100, 100])
    for allocation in ([0, 0], [90, 110]):
        d = incremental_allowance_payment(plan, base, prices, allocation, allocation)
        np.testing.assert_equal(d, prices * (plan - base))
    adjusted = incremental_allowance_payment(plan, base, prices, [70, 50], [90, 90])
    np.testing.assert_equal(adjusted, np.zeros_like(prices))


def test_purchase_only_has_a_kink_and_does_not_credit_unused_allowances():
    e = np.array([80, 90, 100])
    np.testing.assert_equal(allowance_payment(e, 30, 90, mode='purchase_only'), [0, 0, 300])
    assert incremental_allowance_payment(80, 100, 30, 90, 90, mode='purchase_only') == -300


def test_bad_quantities_prices_modes_and_shapes_fail():
    for args in [dict(emissions=-1), dict(prices=np.nan), dict(free_allowances=-2),
                 dict(mode='auction_discount'), dict(prices=[1, 2, 3])]:
        values = dict(emissions=[1, 2], prices=3, free_allowances=0)
        values.update(args)
        with pytest.raises(ValueError):
            allowance_payment(**values)


def test_company_allocation_path_requires_every_year_and_never_infers_from_auction_share():
    cfg = dict(carbon_accounting_mode='net_trade',carbon_auction_share={2025:0.15},
               free_allowances_tco2={'POSCO':{2025:100}})
    with pytest.raises(ValueError,match='POSCO 2026'):
        free_allowance_path(cfg,'POSCO',[2025,2026])
    with pytest.raises(ValueError,match='NSC 2025'):
        free_allowance_path(cfg,'NSC',[2025])
    np.testing.assert_equal(free_allowance_path(dict(carbon_accounting_mode='gross_obligation_proxy'),'NSC',[2025,2026]),[0,0])
