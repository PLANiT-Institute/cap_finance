"""Cost/quantity invariants when source steel components enter actual FIN."""
from pathlib import Path
import json

import numpy as np
import pytest
from cap import config as C
from cap.reference_steel import build_vogl_reference_profile
from cap.plancost import simulate_cost

ROOT=Path(__file__).resolve().parents[1]


def case(utilization=1.,capacity=1e6):
    package=json.loads((ROOT/'data/research_v2/steel_cost_reference/vogl_main_text_package.json').read_text())
    years=tuple(range(2027,2051));n=len(years)
    r=build_vogl_reference_profile(package,years,capacity_t_per_year=capacity,
        annual_utilization=np.full(n,utilization),adopt_year=2027,build_years=3,
        numerical_KRW_per_source_EUR=1500.,oxygen_sale_fraction=.6,direct_emission_factor_tco2_per_t=0.)
    cfg=C.load(discount_rate=.05,carbon_accounting_mode='gross_obligation_proxy');cfg['years']={'start':2027,'end':2050}
    prices={k:np.zeros(n) for k in ['elec','re','h2','co2','coal','gas']}
    prices['elec'][:]=40*1500
    for row in package['purchases']:prices[row['flow_id']]=np.full(n,row['price_EUR']*1500)
    prices['oxygen_netback']=np.full(n,60.8*1500)  # explicit zero-conditioning-cost source reproduction
    shocks={k:np.ones((3,n)) for k in ['elec','h2','capex','pellets','lime','alloys','graphite_electrodes','oxygen_netback']}
    return package,years,r,cfg,prices,shocks


def test_published_unit_cost_reconstruction_and_cash_NPV():
    pkg,years,r,cfg,px,s=case();d=1.05**-np.arange(len(years))
    operating=3.48*40+1.504*100+.05*100+.011*1777+.002*4000+53.2+574*.03-.411*.6*60.8
    assert operating+pkg['annualized_capital_EUR_t']==pytest.approx(431.5148830914192)
    cash=np.zeros(len(years));cash[:3]=574e6/3;cash[13]=160e6;cash[23]=574e6
    expected=((cash+operating*r.output_t)*d).sum()*1500/1e9
    np.testing.assert_allclose(simulate_cost(r.profile,px,s,{'subsidy':{}},cfg,freeze='capex'),expected)
    assert not r.profile.h2_kg.any()


def test_half_utilization_leaves_capacity_maintenance_and_capital_fixed():
    _,_,full,cfg,px,s=case();_,_,half,_,_,_=case(.5)
    np.testing.assert_equal(full.profile.capex_k,half.profile.capex_k)
    np.testing.assert_equal(full.operating_cost_components_k['fixed_maintenance'],half.operating_cost_components_k['fixed_maintenance'])
    np.testing.assert_equal(half.output_t,full.output_t*.5)
    np.testing.assert_equal(half.profile.grid_mwh,full.profile.grid_mwh*.5)
    assert simulate_cost(half.profile,px,s,{'subsidy':{}},cfg)[0] > .5*simulate_cost(full.profile,px,s,{'subsidy':{}},cfg)[0]


def test_zero_utilization_is_not_zero_installed_capacity():
    _,_,idle,cfg,px,s=case(0.);_,_,absent,_,_,_=case(0.,0.)
    assert not idle.output_t.any()
    assert simulate_cost(idle.profile,px,s,{'subsidy':{}},cfg)[0]>0
    np.testing.assert_equal(simulate_cost(absent.profile,px,s,{'subsidy':{}},cfg),0)


def test_common_joint_price_paths_match_independent_material_formula():
    _,years,r,cfg,px,s=case();d=1.05**-np.arange(len(years))
    base=simulate_cost(r.profile,px,s,{'subsidy':{}},cfg)
    factors=np.array([.7,1,1.8])[:,None]*np.ones((3,len(years)))
    stressed={**s,'elec':factors,'pellets':factors,'oxygen_netback':factors}
    result=simulate_cost(r.profile,px,stressed,{'subsidy':{}},cfg)
    expected=((factors-1)*(3.48*40+1.504*100-.411*.6*60.8)*r.output_t[None,:]*d).sum(axis=1)*1500/1e9
    np.testing.assert_allclose(result-base,expected,atol=1e-10)


def test_missing_material_shock_is_rejected():
    _,_,r,cfg,px,s=case();del s['pellets']
    with pytest.raises(ValueError,match='Explicit central price and shock'):simulate_cost(r.profile,px,s,{'subsidy':{}},cfg)


@pytest.mark.parametrize('kwargs',[{'capacity_t_per_year':-1},{'numerical_KRW_per_source_EUR':0},
    {'oxygen_sale_fraction':1.1},{'direct_emission_factor_tco2_per_t':-1},
    {'annual_utilization':[1.]},{'annual_utilization':[1.1]*24},{'annual_utilization':[float('nan')]*24}])
def test_invalid_input_boundaries(kwargs):
    p,years,*_=case()
    params=dict(capacity_t_per_year=1e6,annual_utilization=np.ones(24),adopt_year=2027,build_years=3,
        numerical_KRW_per_source_EUR=1500.,oxygen_sale_fraction=.6,direct_emission_factor_tco2_per_t=0.)
    with pytest.raises(ValueError):build_vogl_reference_profile(p,years,**{**params,**kwargs})
