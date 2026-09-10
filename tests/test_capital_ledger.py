import numpy as np
import pytest

from cap.capital_ledger import facility_capital_ledger


FAC = dict(capacity=10, incumbent_capex_unit=10, reinvest_cycle_yr=5, last_reline_year=2025)
TECH = dict(capex_unit=20, build_years=2, lifetime=5, retrofit=0)
YEARS = np.arange(2025, 2037)


def test_baseline_pays_renewal_cash_but_no_new_construction_or_book_writeoff():
    p = facility_capital_ledger(FAC, None, None, YEARS)
    assert list(YEARS[p.cash_capex_k > 0]) == [2030, 2035]
    assert p.cash_capex_k.sum() == 200
    assert not p.construction_k.any() and not p.noncash_writeoff_k.any()
    assert not p.terminal_value_k.any()


def test_replacement_at_renewal_boundary_avoids_incumbent_renewal_without_writeoff():
    p = facility_capital_ledger(FAC, TECH, 2028, YEARS)
    np.testing.assert_equal(p.construction_k[3:5], [100, 100])
    assert not p.incumbent_renewal_k.any()
    assert not p.noncash_writeoff_k.any()
    assert p.transition_renewal_k[10] == 200
    assert p.cash_capex_k.sum() == 400


def test_retrofit_retains_incumbent_campaign_and_renews_both_assets():
    p = facility_capital_ledger(FAC, {**TECH, 'retrofit': 1}, 2028, YEARS)
    assert p.incumbent_renewal_k.sum() == 200
    assert p.transition_renewal_k.sum() == 200
    assert not p.noncash_writeoff_k.any()
    assert p.cash_capex_k.sum() == 600


def test_early_retirement_records_remaining_book_separately_from_cash():
    p = facility_capital_ledger(FAC, None, 2032, YEARS, retire=True)
    assert p.incumbent_renewal_k.sum() == 100
    assert p.noncash_writeoff_k[7] == pytest.approx(60)
    assert p.cash_capex_k.sum() == 100  # book entry is not a second cash payment
    assert not p.cash_capex_k[7:].any()


def test_terminal_proxy_is_explicit_and_applies_to_both_baseline_and_transition():
    b = facility_capital_ledger(FAC, None, None, YEARS, terminal_rule='straight_line_proxy')
    p = facility_capital_ledger(FAC, TECH, 2028, YEARS, terminal_rule='straight_line_proxy')
    assert b.terminal_value_k[-1] == pytest.approx(60)
    assert p.terminal_value_k[-1] == pytest.approx(120)
    # A terminal convention does not alter earlier payments or book entries.
    raw = facility_capital_ledger(FAC, TECH, 2028, YEARS)
    np.testing.assert_equal(p.cash_capex_k, raw.cash_capex_k)


def test_invalid_dates_and_costs_are_rejected_and_no_renewal_is_explicit_sensitivity():
    for args in [dict(adopt_year=2024), dict(adopt_year=2035),
                 dict(technology={**TECH, 'capex_unit': -1}),
                 dict(years=[2025, 2027]), dict(terminal_rule='book_is_cash')]:
        values = dict(facility=FAC, technology=TECH, adopt_year=2028, years=YEARS)
        values.update(args)
        with pytest.raises(ValueError):
            facility_capital_ledger(**values)
    p = facility_capital_ledger(FAC, None, None, YEARS, include_renewals=False)
    assert not p.cash_capex_k.any()
