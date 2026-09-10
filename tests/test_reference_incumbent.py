from dataclasses import replace
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from cap.reference_ncc import NCCConditions,build_ncc_reference
from cap.reference_incumbent import existing_ncc_pair
Y=tuple(range(2027,2051))
OBS=pd.read_csv(Path(__file__).resolve().parents[1]/'data/research_v2/tiggeloven_reference/source_observations.csv').to_dict('records')

def inputs():
 return [build_ncc_reference(OBS,c,Y,NCCConditions(1,8000,life,psi,.04,.05,1,'none'),numerical_KRW_per_EUR=1000) for c,life,psi in [('conventional',30,.04),('electric',20,.02)]]

def build(**kw):
 args=dict(years=Y,remaining_years=8,replacement_cost_scale=1.,retirement_cash_EUR=0.,salvage_receipt_EUR=0.,terminal_rule='none',ethylene_yield=.303,numerical_KRW_per_EUR=1000.)
 args.update(kw);return existing_ncc_pair(*inputs(),**args)


def test_no_initial_recharge_and_future_due_date():
 r=build();a=r['annual'];b=a['continue_existing'];e=a['replace_2030']
 assert not b['construction_EUR'].any()
 assert np.array_equal(np.array(Y)[b['incumbent_renewal_EUR']>0],[2035])
 assert not e['incumbent_renewal_EUR'].any()
 np.testing.assert_array_equal(b['output_t'],e['output_t']);assert np.all(b['output_t']==920000)
 assert e['construction_EUR'].sum()==pytest.approx(inputs()[1]['initial_plant_EUR'])


def test_due_at_retirement_is_avoided_but_earlier_due_is_paid():
 at=build(remaining_years=3);before=build(remaining_years=1)
 assert not at['annual']['replace_2030']['incumbent_renewal_EUR'].any()
 assert before['annual']['replace_2030']['incumbent_renewal_EUR'][1]>0
 assert at['annual']['replace_2030']['noncash_writeoff_proxy_EUR'].sum()==0
 assert before['annual']['replace_2030']['noncash_writeoff_proxy_EUR'][3]>0


def test_pretransition_operating_costs_and_physical_demand_are_common():
 r=build();b,e=r['profiles'].values()
 np.testing.assert_array_equal(b.grid_mwh[:3],e.grid_mwh[:3])
 np.testing.assert_array_equal(b.other_cost_k[:3],e.other_cost_k[:3])
 for bf,ef in zip(b.additional_commodity_flows,e.additional_commodity_flows):np.testing.assert_array_equal(bf.quantity[:3],ef.quantity[:3])
 assert np.all(b.grid_mwh[:3]>0)


def test_retirement_and_salvage_cash_are_separate_from_writeoff_proxy():
 a=build();b=build(retirement_cash_EUR=12,salvage_receipt_EUR=7)
 diff=b['profiles']['replace_2030'].other_cost_k-a['profiles']['replace_2030'].other_cost_k
 np.testing.assert_array_equal(diff,np.eye(1,24,3)[0]*5)
 np.testing.assert_array_equal(a['annual']['replace_2030']['noncash_writeoff_proxy_EUR'],b['annual']['replace_2030']['noncash_writeoff_proxy_EUR'])
 assert a['profiles']['replace_2030'].noncash_writeoff_k is None


@pytest.mark.parametrize('change',[{'remaining_years':0},{'remaining_years':26},{'remaining_years':True},{'replacement_cost_scale':-1},{'retirement_cash_EUR':float('nan')},{'salvage_receipt_EUR':-1},{'numerical_KRW_per_EUR':0},{'terminal_rule':'straight_line_proxy'},{'ethylene_yield':.30}])
def test_inconsistent_contracts_rejected(change):
 with pytest.raises(ValueError):build(**change)
