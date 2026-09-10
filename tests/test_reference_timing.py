from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from cap.reference_timing import timing_menu,emission_qualification
from cap.reference_incumbent import existing_ncc_pair
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture
def menu():
 obs=pd.read_csv(ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv').to_dict('records')
 return timing_menu(obs,[2030,2035,2040,2045],remaining_years=8,replacement_cost_scale=1.,numerical_KRW_per_EUR=1000.)
def test_default_reproduces_independent_existing_bridge(menu):
 pair=existing_ncc_pair(*menu['references'],years=menu['years'],remaining_years=8,replacement_cost_scale=1.,retirement_cash_EUR=0.,salvage_receipt_EUR=0.,terminal_rule='none',ethylene_yield=.303,numerical_KRW_per_EUR=1000.)
 r=menu['candidates']['replace_2030'];p=pair['profiles']['replace_2030']
 for field in ['grid_mwh','other_cost_k','capex_k','maintenance_capex_k']:np.testing.assert_allclose(getattr(r['profile'],field),getattr(p,field),rtol=0,atol=1e-7)
 np.testing.assert_allclose(r['fixed_cash_EUR'],pair['annual']['replace_2030']['net_fixed_cash_EUR'])
def test_dated_cash_and_equal_delivery(menu):
 for r in menu['candidates'].values():
  date=r['commission_year'];y=np.array(menu['years'])
  assert list(y[r['construction_EUR']>0])==list(range(date-3,date))
  assert list(y[r['new_renewal_EUR']>0])==([2050] if date==2030 else [])
  assert list(y[r['incumbent_renewal_EUR']>0])==([2035] if date>2035 else [])
  np.testing.assert_allclose(r['profile'].additional_commodity_flows[0].quantity*.303,920000,rtol=0,atol=1e-7)
  assert np.all(r['output_t']==920000)
  assert not np.any(r['profile'].emissions) # cash-only placeholder, never the eligibility input
@pytest.mark.parametrize('dates',[[2029],[2051],[2030,2030],[2030.0],[True],[]])
def test_invalid_dates(dates):
 with pytest.raises(ValueError):timing_menu([],dates,remaining_years=8,replacement_cost_scale=1.,numerical_KRW_per_EUR=1000.)
def test_annual_is_not_cumulative():
 q=emission_qualification([10,9,0],annual_caps=[10,5,0],cumulative_cap=20,terminal_cap=0)
 assert q==dict(annual_feasible=False,cumulative_feasible=True,terminal_feasible=True)
@pytest.mark.parametrize('e,a,c,t',[([1,float('nan')],[1,0],1,0),([1],[1,0],1,0),([-1],[1],1,0),([1],[1],-1,0),([1],[1],1,True)])
def test_invalid_emission_boundary(e,a,c,t):
 with pytest.raises(ValueError):emission_qualification(e,annual_caps=a,cumulative_cap=c,terminal_cap=t)
