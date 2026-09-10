from dataclasses import replace
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from cap.reference_ncc import NCCConditions,build_ncc_reference

YEARS=tuple(range(2027,2051))
OBS=pd.read_csv(Path(__file__).resolve().parents[1]/'data/research_v2/tiggeloven_reference/source_observations.csv').to_dict('records')
C=NCCConditions(1.,8000.,30,.04,.04,.05,1.,'none')


def build(case='conventional',conditions=C,observations=OBS):
    return build_ncc_reference(observations,case,YEARS,conditions,numerical_KRW_per_EUR=1000.)


@pytest.mark.parametrize('recovery',[0.,.8,1.])
@pytest.mark.parametrize('sale',[0.,.5,1.])
def test_mass_energy_closure_and_external_cash_roles(recovery,sale):
    for case in ['conventional','electric']:
        r=build(case,replace(C,useful_steam_recovery=recovery,methane_sale_fraction=sale))
        q=r['quantities_per_t_naphtha']
        assert q['methane_generated_MWh']+q['methane_purchased_MWh']==pytest.approx(q['cracker_methane_MWh']+q['boiler_methane_MWh']+q['methane_sold_MWh']+q['methane_transferred_MWh'])
        assert q['useful_steam_MWh']+q['boiler_heat_MWh']==pytest.approx(q['steam_demand_MWh']+q['unused_heat_MWh'])
        assert q['methane_purchased_MWh']*q['methane_sold_MWh']==0
        assert (r['profile'].additional_commodity_flows[-1].quantity<=0).all()
        assert not r['profile'].grid_mwh[:3].any()
        assert np.all(r['output_t'][3:]==920000.)


def test_full_recovery_reference_and_zero_recovery_purchase():
    b=build();e=build('electric')
    assert b['quantities_per_t_naphtha']['boiler_heat_MWh']==pytest.approx(.082)
    assert e['quantities_per_t_naphtha']['unused_heat_MWh']==pytest.approx(.05)
    assert e['initial_boiler_EUR']==0 and e['initial_plant_EUR']==pytest.approx(994490000.)
    assert build(conditions=replace(C,useful_steam_recovery=0.))['quantities_per_t_naphtha']['methane_purchased_MWh']>0


def test_renewal_and_terminal_value_are_dated_not_annuitized_capital():
    a=build('electric',replace(C,plant_lifetime=20))
    b=build('electric',replace(C,plant_lifetime=20,terminal_rule='straight_line_proxy'))
    assert a['capital'].renewal[0,-1]==pytest.approx(a['initial_plant_EUR'])
    assert b['capital'].terminal_receipt[0,-1]==pytest.approx(.95*a['initial_plant_EUR'])
    assert a['capital'].construction.sum()==pytest.approx(a['initial_plant_EUR'])
    assert a['maintenance_EUR'][3]==pytest.approx(.04*994490000.*(.05/(1-1.05**-20)))


def test_boiler_and_plant_maintenance_use_their_own_fractions():
    r=build('electric',replace(C,useful_steam_recovery=.8,maintenance_fraction=.02,boiler_maintenance_fraction=.04,maintenance_annuity_rate=0.))
    boiler=72.1*(.492-.542*.8)*(115/.303)*1000
    assert r['maintenance_EUR'][3]==pytest.approx(.02*994490000./30+.04*boiler/25)


@pytest.mark.parametrize('key,value',[('useful_steam_recovery',1.1),('operating_hours',0),('plant_lifetime',20.5),('maintenance_fraction',-.1),('methane_sale_fraction',True)])
def test_invalid_conditions_fail(key,value):
    with pytest.raises(ValueError):build(conditions=replace(C,**{key:value}))


def test_duplicate_and_wrong_unit_source_are_rejected():
    with pytest.raises(ValueError):build(observations=OBS+[OBS[0]])
    obs=[dict(x) for x in OBS]
    next(x for x in obs if x['case']=='conventional' and x['item']=='TOC_slope')['unit']='EUR2019/(t/year)'
    with pytest.raises(ValueError):build(observations=obs)
