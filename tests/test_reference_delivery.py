from dataclasses import replace
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest
from cap.reference_ncc import NCCConditions,build_ncc_reference
from cap.reference_delivery import validate_ncc_delivery_pair

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import ncc_cash_workbook_control as control
YEARS=tuple(range(2027,2051))
OBS=pd.read_csv(ROOT/'data/research_v2/tiggeloven_reference/source_observations.csv').to_dict('records')


def cases(hours=8000):
    return {case:build_ncc_reference(OBS,case,YEARS,NCCConditions(1.,hours,30,.04,.04,.05,1.,'none'),numerical_KRW_per_EUR=1000.) for case in ['conventional','electric']}


def check(r):
    return validate_ncc_delivery_pair(r,years=YEARS,required_output_t=np.r_[np.zeros(3),np.full(21,920000.)],capacity_t=np.r_[np.zeros(3),np.full(21,1007400.)],ethylene_yields={'conventional':.303,'electric':.303})


def test_actual_reference_profiles_meet_shared_service():
    r=check(cases())
    assert r['cases']['electric']['delivery_total_t']==19320000
    assert not r['abatement_feasibility_verified']


def test_electric_output_cut_cannot_be_read_as_cheaper_same_service():
    r=cases();r['electric']['output_t']*=.9
    with pytest.raises(ValueError,match='Customer delivery'):check(r)


@pytest.mark.parametrize('target',['naphtha','methane_purchase','methane_sale','grid'])
def test_fin_charges_cannot_drift_from_material_output(target):
    r=cases();p=r['electric']['profile']
    if target=='grid':p.grid_mwh=p.grid_mwh.copy();p.grid_mwh[3]+=1
    else:
        flows=[]
        for f in p.additional_commodity_flows:
            q=f.quantity.copy()
            if f.flow_id==target:q[3]+=1
            flows.append(replace(f,quantity=q))
        p.additional_commodity_flows=tuple(flows)
    with pytest.raises(ValueError,match='inconsistent with delivery'):check(r)


def test_bad_case_stops_before_prices_or_fin(monkeypatch):
    original=control.build_ncc_reference;calls=[]
    def bad(obs,case,*args,**kwargs):
        r=original(obs,case,*args,**kwargs)
        if case=='electric':r['output_t']*=.9
        return r
    def forbidden(*args,**kwargs):calls.append(1);raise AssertionError('Should not reach price sampling/FIN')
    monkeypatch.setattr(control,'build_ncc_reference',bad);monkeypatch.setattr(control,'block_paths',forbidden);monkeypatch.setattr(control,'simulate_cost',forbidden)
    with pytest.raises(ValueError,match='Customer delivery'):control.evaluate(dict(control.DEFAULTS,paths=2))
    assert calls==[]


def test_lower_activity_preserves_reference_fixed_cash():
    high=cases();low=cases(4800)
    for case in high:
        np.testing.assert_array_equal(high[case]['capital'].net_cash_payments,low[case]['capital'].net_cash_payments)
        np.testing.assert_array_equal(high[case]['maintenance_EUR'],low[case]['maintenance_EUR'])
        np.testing.assert_allclose(low[case]['output_t'],high[case]['output_t']*.6)
    # Different delivery contracts are separate sensitivities, not one frontier.
    with pytest.raises(ValueError,match='Customer delivery'):check(low)
