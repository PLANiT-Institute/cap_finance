import numpy as np
import pandas as pd
from types import SimpleNamespace

from cap import config as C
from cap.e1_constraints import run as run_e1
from cap.e2_milp import _solve_company


def test_moving_analysis_start_does_not_reset_the_scenario_budget_anchor(tmp_path):
    cfg=C.load(data_dir='data/sample',out_dir=str(tmp_path/'full'))
    cfg['scenario_base_year']=2025
    full=run_e1(cfg)['constraints']
    cfg['years']=dict(start=2027,end=2050)
    cfg['out_dir']=str(tmp_path/'later')
    later=run_e1(cfg)['constraints']
    keys=['company_id','scenario','year']
    merged=later.merge(full,on=keys,suffixes=('_later','_full'),validate='one_to_one')
    np.testing.assert_allclose(merged.company_budget_tco2_later,merged.company_budget_tco2_full,rtol=1e-12)


def test_cumulative_compliance_does_not_imply_annual_compliance():
    # A two-year plan emits20 then10 against annual budgets15,15.
    # The fixed plan satisfies the total30 but violates the first-year cap.
    cfg=C.load(data_dir='data/sample',discount_rate=0.,capital_accounting='cash_v1',
               carbon_accounting_mode='gross_obligation_proxy',candidate_contracts='unhedged')
    cfg['years']=dict(start=2025,end=2026)
    cfg['milp']=dict(cfg['milp'],retire_max_share=0,solver_time_limit_s=5)
    fac=pd.DataFrame([dict(facility_id='A',company_id='POSCO',sector='steel',unit_type='BF',
        production=10.,capacity=10.,ef_inc=2.,elec_int_inc=0.,coal_int_inc=0.,gas_int_inc=0.,
        last_reline_year=2025,reinvest_cycle_yr=5,next_reinvest_year=2030,
        incumbent_capex_unit=10.,margin_kthou_t=0.)]).set_index('facility_id')
    tech=pd.DataFrame([dict(tech_id='T',sector='steel',applies_to_unit='BF',capex_unit=1.,
        opex_fixed=0.,opex_var=0.,elec_intensity=0.,h2_intensity=0.,emission_factor=1.,
        avail_year=2025,build_years=1,lifetime=20,capex_uncertainty=40.,retrofit=0)])
    prices=pd.DataFrame([dict(region='Korea',scenario='S',variable=k+'_price',year=y,value=10.)
                         for k in ['elec','coal','gas','co2','h2','re'] for y in [2025,2026]])
    constraints=pd.DataFrame(dict(company_id='POSCO',scenario='S',year=[2025,2026],company_budget_tco2=[15.,15.]))
    avail=pd.DataFrame(columns=['scenario','region','tech_id','avail_year_scenario'])
    args=(cfg,'POSCO','S',fac,tech,SimpleNamespace(vol=dict(elec=.1,h2=.2,capex=.1)),prices,constraints,avail)
    fixed=dict(x={('A','T',2025):1},ppa=0,epc=0,ccfd=0)
    cfg['budget_mode']='cumulative_hard'
    result=_solve_company(*args,fixed=fixed)
    assert result is not None and result['cum_emis_tco2']==30
    assert result['budget_slack']==5
    cfg['budget_mode']='annual_hard'
    assert _solve_company(*args,fixed=fixed) is None
