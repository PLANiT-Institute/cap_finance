"""Economic invariants across the actual MILP and simulated costing engines."""
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from cap import config as C
from cap.e2_milp import _solve_company
from cap.plancost import build_profile, simulate_cost


def case():
    years = np.arange(2025, 2037)
    cfg = C.load(capital_accounting='cash_v1', data_dir='data/sample', discount_rate=0)
    cfg['years'] = dict(start=2025, end=2036)
    cfg['contracts'] = dict(ppa_premium_pct=.1, epc_premium_pct=.1, ccfd_fee_pct=0)
    cfg['milp'] = dict(cfg['milp'], solver_time_limit_s=10, retire_max_share=0)
    fac = pd.DataFrame([dict(facility_id='A',company_id='POSCO',sector='petchem',
        unit_type='NCC',capacity=10.,production=10.,ef_inc=2.,elec_int_inc=.2,
        coal_int_inc=.1,gas_int_inc=.1,last_reline_year=2025,reinvest_cycle_yr=5,
        next_reinvest_year=2030,incumbent_capex_unit=10.,margin_kthou_t=0.)]).set_index('facility_id')
    tech = pd.DataFrame([dict(tech_id='T',sector='petchem',applies_to_unit='NCC',
        capex_unit=20.,opex_fixed=1.,opex_var=1.,elec_intensity=.5,h2_intensity=.1,
        emission_factor=1.,avail_year=2025,build_years=2,lifetime=5,
        capex_uncertainty=40.,retrofit=0)])
    px = {k:np.full(len(years),v) for k,v in
          dict(elec=100.,re=120.,coal=200.,gas=300.,co2=0.,h2=30.).items()}
    plan = pd.DataFrame([dict(company_id='POSCO',facility_id='A',tech_id='T',
        adopt_year=2028,op_year=2030,ppa_share=0.,epc=0,ccfd=0)])
    return cfg,years,fac,tech,px,plan


@pytest.mark.parametrize('retention', [(0.,0.,0.), (1.,.5,.8)])
@pytest.mark.parametrize('carbon_basis', ['gross_obligation_proxy','net_trade','purchase_only'])
def test_milp_central_cash_cost_equals_e4_for_fixed_unhedged_plan(retention,carbon_basis):
    cfg,years,fac,tech,px,plan = case()
    cfg['energy_balance_mode'] = 'explicit_retention'
    cfg['carbon_accounting_mode'] = carbon_basis
    cfg['free_allowances_tco2'] = {'POSCO':{int(y):15 for y in years}}
    px['co2'] = np.full(len(years),30.)
    for field,value in zip(['retained_coal_fraction','retained_gas_fraction','retained_grid_fraction'],retention):
        tech[field] = value
    prices = pd.DataFrame([dict(region='Korea',scenario='S',variable=k+'_price',
        year=int(y),value=float(v)) for k,a in px.items() for y,v in zip(years,a)])
    constraints = pd.DataFrame(dict(company_id='POSCO',scenario='S',year=years,
                                   company_budget_tco2=np.full(len(years),1000.)))
    avail = pd.DataFrame(columns=['scenario','region','tech_id','avail_year_scenario'])
    cal = SimpleNamespace(vol=dict(elec=.1,h2=.2,capex=.1))
    result = _solve_company(cfg,'POSCO','S',fac,tech,cal,prices,constraints,avail,
                           fixed=dict(x={('A','T',2028):1},ppa=0,epc=0,ccfd=0))
    assert result is not None and result['budget_slack'] == 0
    profile = build_profile(plan,fac,tech,px,years,cfg)
    shocks = {k:np.ones((1,len(years))) for k in ['elec','h2','capex']}
    simulated = simulate_cost(profile,px,shocks,dict(subsidy={}),cfg)[0]
    assert result['npv_cost'] == pytest.approx(simulated, abs=1e-10)
    assert profile.capex_k.sum() == 400
    # E5's removed carbon component must equal the actual deterministic payment.
    from cap.e5_metrics import _carbon_npv
    from cap.plancost import auction_share
    carbon = _carbon_npv(profile,px,np.ones(len(years)),auction_share(years,cfg))
    zero_carbon = simulate_cost(profile,{**px,'co2':np.zeros(len(years))},shocks,dict(subsidy={}),cfg)[0]
    assert simulated-zero_carbon == pytest.approx(carbon,abs=1e-12)
    expected = {'gross_obligation_proxy':5100.,'net_trade':-300.,'purchase_only':750.}[carbon_basis]
    assert carbon == pytest.approx(expected*1e-9)


def test_epc_and_subsidy_cover_initial_project_not_renewals_or_book_entries():
    cfg,years,fac,tech,px,plan = case()
    profile = replace(build_profile(plan,fac,tech,px,years,cfg),epc=1)
    shocks = {k:np.ones((1,len(years))) for k in ['elec','h2','capex']}
    base = simulate_cost(profile,px,shocks,dict(subsidy={}),cfg)[0]
    stressed = {**shocks,'capex':shocks['capex']*2}
    cost = simulate_cost(profile,px,stressed,dict(subsidy={}),cfg)[0]
    assert cost-base == pytest.approx(200e-6)  # renewal still exposed under project EPC
    supported = simulate_cost(profile,px,shocks,dict(subsidy={'T':np.full(len(years),.5)}),cfg)[0]
    assert base-supported == pytest.approx(200*.5*1.1e-6)
    arbitrary_book = replace(profile,noncash_writeoff_k=np.full(len(years),1e12))
    np.testing.assert_equal(simulate_cost(arbitrary_book,px,shocks,dict(subsidy={}),cfg),[base])


def test_baseline_renewal_and_actual_operation_writeoff_are_visible_in_profiles():
    cfg,years,fac,tech,px,plan = case()
    baseline = plan.assign(facility_id=None,tech_id=None,adopt_year=None,op_year=None)
    b = build_profile(baseline,fac,tech,px,years,cfg)
    assert b.capex_k.sum() == 200 and not b.capex_by_tech
    later = plan.assign(adopt_year=2030,op_year=2032)
    p = build_profile(later,fac,tech,px,years,cfg)
    assert p.noncash_writeoff_k[7] == pytest.approx(60)
    assert p.capex_k.sum() == 300  # 100 incumbent renewal + 200 construction


def test_explicit_fuel_quantities_follow_retention_and_stop_at_retirement():
    cfg,years,fac,tech,px,plan = case()
    cfg['energy_balance_mode'] = 'explicit_retention'
    tech['retained_coal_fraction'] = .25
    tech['retained_gas_fraction'] = .5
    tech['retained_grid_fraction'] = 1.
    p = build_profile(plan,fac,tech,px,years,cfg)
    np.testing.assert_allclose(p.gas_t, np.where(years<2030,1.,.5))
    np.testing.assert_allclose(p.coal_t, np.where(years<2030,1.,.25))
    retire = plan.assign(tech_id='retire',adopt_year=2030,op_year=2030)
    closed = build_profile(retire,fac,tech,px,years,cfg)
    np.testing.assert_allclose(closed.gas_t, np.where(years<2030,1.,0.))
    np.testing.assert_allclose(closed.coal_t, np.where(years<2030,1.,0.))


def test_changed_central_fuel_requires_rebuild_and_matches_new_total_bill():
    cfg,years,fac,tech,px,plan=case()
    p=build_profile(plan,fac,tech,px,years,cfg)
    new={**px,'gas':px['gas']*2,'coal':px['coal']*1.5}
    sh={k:np.ones((1,len(years))) for k in ('elec','h2','capex')}
    with pytest.raises(ValueError,match='Embedded .* central price changed'):
        simulate_cost(p,new,sh,dict(subsidy={}),cfg)
    rebuilt=build_profile(plan,fac,tech,new,years,cfg)
    oldcost=simulate_cost(p,px,sh,dict(subsidy={}),cfg)[0]
    newcost=simulate_cost(rebuilt,new,sh,dict(subsidy={}),cfg)[0]
    expected=(p.gas_t*(new['gas']-px['gas'])+p.coal_t*(new['coal']-px['coal'])).sum()/1e9
    assert newcost-oldcost==pytest.approx(expected,abs=1e-12)
    # A further gas shock acts on the new central price, exactly once.
    stressed=simulate_cost(rebuilt,new,{**sh,'gas':np.full((1,len(years)),2.)},dict(subsidy={}),cfg)[0]
    assert stressed-newcost==pytest.approx((p.gas_t*new['gas']).sum()/1e9,abs=1e-12)


def test_profile_records_years_and_copies_price_basis():
    cfg,years,fac,tech,px,plan=case()
    p=build_profile(plan,fac,tech,px,years,cfg)
    saved=p.embedded_price_basis['gas'].copy()
    px['gas'][:]=999
    np.testing.assert_equal(p.embedded_price_basis['gas'],saved)
    cfg['years']=dict(start=2026,end=2037)
    with pytest.raises(ValueError,match='Profile years changed'):
        simulate_cost(p,px,{'elec':np.ones((1,len(years)))},dict(subsidy={}),cfg)


def test_retirement_embedded_electricity_offset_requires_rebuild():
    cfg,years,fac,tech,px,plan=case()
    retired=plan.assign(tech_id='retire',adopt_year=2025,op_year=2025)
    p=build_profile(retired,fac,tech,px,years,cfg)
    assert not np.any(p.gas_t) and not np.any(p.coal_t)
    assert 'elec' in p.embedded_price_basis
    with pytest.raises(ValueError,match='Embedded elec'):
        simulate_cost(p,{**px,'elec':px['elec']*2},{'elec':np.ones((1,len(years)))},dict(subsidy={}),cfg)
