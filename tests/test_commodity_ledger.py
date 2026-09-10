from dataclasses import replace

import numpy as np
import pytest

from cap import config as C
from cap.commodity_ledger import CommodityFlow, additional_commodity_cost_k
from cap.plancost import PlanProfile, simulate_cost


def setup_case():
    cfg = C.load(data_dir='data/sample', discount_rate=0.)
    cfg['years'] = dict(start=2027, end=2028)
    cfg['carbon_accounting_mode'] = 'gross_obligation_proxy'
    z = np.zeros(2)
    # 2 tonnes of gas at 300 KRW/t + 3 tonnes of coal at 200 KRW/t
    p = PlanProfile(z.copy(), z.copy(), z.copy(), np.full(2, 1.2), z.copy(),
                    {}, {}, z.copy(), 0., 0, 0, gas_t=np.full(2, 2.), coal_t=np.full(2, 3.))
    prices = {k:np.full(2, v) for k,v in dict(elec=100., re=100., h2=30.,
                                            gas=300., coal=200., co2=0.).items()}
    shocks = {k:np.ones((3,2)) for k in ('elec','h2','capex')}
    return cfg, p, prices, shocks


def test_fuel_shocks_preserve_central_and_do_not_double_charge():
    cfg,p,prices,shocks = setup_case()
    support = dict(subsidy={})
    base = simulate_cost(p,prices,shocks,support,cfg)
    np.testing.assert_allclose(base,2.4e-6)
    augmented = {**shocks,'gas':np.array([[1.,1.],[2.,2.],[.5,.5]]),
                 'coal':np.ones((3,2))}
    np.testing.assert_allclose(simulate_cost(p,prices,augmented,support,cfg),
                               [2.4e-6,3.6e-6,1.8e-6])
    np.testing.assert_allclose(simulate_cost(p,prices,augmented,support,cfg,freeze='gas'),base)
    with pytest.raises(ValueError,match='quantity'):
        simulate_cost(replace(p,gas_t=None),prices,augmented,support,cfg)


def test_ncc_incremental_energy_netback_matches_independent_cash_arithmetic():
    cfg,p,prices,shocks = setup_case()
    flow = CommodityFlow('freed_internal_methane','methane_netback',np.full(2,-.488),
                         'tCH4','export_netback','Layritz preprint A.2 + declared saleability')
    p = replace(p,other_cost_k=np.zeros(2),gas_t=np.zeros(2),coal_t=np.zeros(2),
                re_mwh=np.full(2,6.78),additional_commodity_flows=(flow,))
    # Explicit illustrative exchange rate, not a market observation.
    fx = 1500.
    prices = {**prices,'re':np.full(2,100.*fx),'methane_netback':np.full(2,500.*fx)}
    shocks = {**shocks,'methane_netback':np.array([[1.,1.],[2.,2.],[.5,.5]])}
    got = simulate_cost(p,prices,shocks,dict(subsidy={}),cfg)
    expected = 2*fx*np.array([678-244,678-488,678-122])*1e-9
    np.testing.assert_allclose(got,expected)
    # An export price increase reduces cost; no avoided purchase of natural gas.
    assert got[1] < got[0] < got[2]
    cfg['discount_rate'] = .1
    discounted = simulate_cost(p,prices,shocks,dict(subsidy={}),cfg)
    np.testing.assert_allclose(discounted,expected/2*(1+1/1.1))


def test_netback_uses_the_same_paths_as_power_and_freeze_is_local():
    cfg,p,prices,shocks = setup_case()
    flow = CommodityFlow('export','netback',np.full(2,-1.),'t','export_netback','assumption')
    p = replace(p,other_cost_k=np.zeros(2),re_mwh=np.ones(2),
                additional_commodity_flows=(flow,))
    prices['netback'] = prices['re'].copy()
    shocks['elec'] = np.array([[1.,2.],[2.,1.],[3.,4.]])
    shocks['netback'] = shocks['elec'].copy()
    np.testing.assert_allclose(simulate_cost(p,prices,shocks,dict(subsidy={}),cfg),0.,atol=1e-15)
    frozen = simulate_cost(p,prices,shocks,dict(subsidy={}),cfg,freeze='netback')
    np.testing.assert_allclose(frozen,np.array([100.,100.,500.])*1e-9)


@pytest.mark.parametrize('change', [dict(role='internal_transfer'),dict(role='component'),
    dict(quantity=np.ones(2)),dict(quantity=np.array([-.5,np.nan])),
    dict(quantity=np.array([-.5])),dict(evidence='')])
def test_unbillable_or_untraceable_exports_are_rejected(change):
    f = CommodityFlow('f','p',-np.ones(2),'t','export_netback','source')
    with pytest.raises(ValueError):
        additional_commodity_cost_k((replace(f,**change),),{'p':np.ones(2)},
                                    {'p':np.ones((3,2))},(3,2))


def test_duplicate_missing_and_unpaired_paths_are_rejected():
    f = CommodityFlow('f','p',-np.ones(2),'t','export_netback','source')
    for flows,shocks in [((f,f),{'p':np.ones((3,2))}),((f,),{}),
                         ((f,),{'p':np.ones((1,2))})]:
        with pytest.raises(ValueError):
            additional_commodity_cost_k(flows,{'p':np.ones(2)},shocks,(3,2))
