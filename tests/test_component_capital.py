import numpy as np
import pytest
from cap.component_capital import CapitalComponent,component_capital_cashflows


C=(CapitalComponent('electrolyser',160,10),CapitalComponent('shaft',230,20),CapitalComponent('EAF',184,20))


def make(**kwargs):
    args=dict(components=C,capacity=1,adopt_year=2027,build_years=3,years=range(2027,2051),unit_of_account='EUR_source_composite')
    args.update(kwargs);return component_capital_cashflows(**args)


def test_components_have_distinct_due_dates_and_initial_cost_is_not_recharged_as_annuity():
    p=make();assert p.construction.sum()==pytest.approx(574)
    assert list(np.array(p.years)[p.renewal[0]>0])==[2040,2050]
    assert list(np.array(p.years)[p.renewal[1]>0])==[2050]
    assert list(np.array(p.years)[p.renewal[2]>0])==[2050]
    assert p.cash_payments.sum()==pytest.approx(574+160+574)
    np.testing.assert_allclose(p.construction.sum(axis=0)[:3],[574/3]*3)


def test_terminal_proxy_tracks_remaining_life_of_each_last_component_campaign():
    p=make(terminal_rule='straight_line_proxy')
    np.testing.assert_allclose(p.terminal_receipt[:,-1],[144,218.5,174.8])
    np.testing.assert_equal(p.cash_payments,make().cash_payments)
    assert p.net_cash_payments[-1]==pytest.approx(574-537.3)


def test_component_split_and_capacity_scaling_conserve_every_cashflow():
    p=make();split=(CapitalComponent('electrolyser_a',80,10),CapitalComponent('electrolyser_b',80,10),*C[1:])
    np.testing.assert_allclose(make(components=split).cash_payments,p.cash_payments)
    np.testing.assert_allclose(make(capacity=2).cash_payments,2*p.cash_payments)
    assert not make(capacity=0).cash_payments.any()


def test_single_component_matches_existing_cash_ledger_when_incumbent_cost_is_zero():
    from cap.capital_ledger import facility_capital_ledger
    for life in (10,20):
        p=make(components=(CapitalComponent('single',574,life),),terminal_rule='straight_line_proxy')
        old=facility_capital_ledger(dict(capacity=1,incumbent_capex_unit=0,reinvest_cycle_yr=10,last_reline_year=2027),dict(capex_unit=574,build_years=3,lifetime=life,retrofit=0),2027,p.years,terminal_rule='straight_line_proxy')
        np.testing.assert_allclose(p.construction.sum(axis=0),old.construction_k)
        np.testing.assert_allclose(p.renewal.sum(axis=0),old.transition_renewal_k)
        np.testing.assert_allclose(p.terminal_receipt.sum(axis=0),old.terminal_value_k)


def test_end_year_annuity_and_beginning_year_replacement_cash_have_equal_infinite_horizon_value():
    p=make(components=(CapitalComponent('single',160,10),),adopt_year=0,build_years=0,years=range(0,1001))
    r=.05;d=1/(1+r);pv=p.cash_payments@d**np.arange(1001)
    annuity=160*r/(1-(1+r)**-10)
    assert pv==pytest.approx(annuity/r,rel=1e-12)
    # Charging the same CRF at each beginning of year is a different convention.
    assert annuity/(1-d)==pytest.approx((1+r)*pv,rel=1e-12)


def test_weights_zero_duration_no_renewal_and_readonly_arrays():
    p=make(build_years=0,include_renewals=False);assert p.cash_payments[0]==574 and p.cash_payments.sum()==574
    p=make(construction_weights=[.5,.3,.2]);np.testing.assert_allclose(p.cash_payments[:3],[287,172.2,114.8])
    with pytest.raises(ValueError):p.renewal[0,0]=3


@pytest.mark.parametrize('args',[
    {'components':()}, {'components':(C[0],C[0])}, {'components':(CapitalComponent('x',100,0),)},
    {'components':(CapitalComponent('x',float('nan'),10),)}, {'capacity':None}, {'capacity':-1},
    {'adopt_year':2026}, {'adopt_year':2050}, {'years':[2027,2029]}, {'build_years':1.5},
    {'construction_weights':[.5,.5]}, {'construction_weights':[.5,.5,.5]}, {'unit_of_account':''},
    {'include_renewals':'yes'}, {'terminal_rule':'guaranteed_resale'}])
def test_incomplete_or_inconsistent_capital_inputs_fail(args):
    with pytest.raises(ValueError):make(**args)
