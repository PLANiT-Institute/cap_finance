import numpy as np
import pandas as pd
import pytest
from cap.disclosed_feasibility import emission_floor


def inputs():
    f=pd.DataFrame([dict(facility_id='A',company_id='C',sector='steel',unit_type='BF',
                         production=10.,ef_inc=2.)]).set_index('facility_id')
    t=pd.DataFrame([dict(tech_id='T',sector='steel',applies_to_unit='BF',
                         emission_factor=.2,avail_year=2027,build_years=2)])
    return f,t


def test_lead_time_and_scenario_unavailability_are_respected():
    f,t=inputs()
    a,_=emission_floor(f,t,[2027,2028,2029],earliest_start_year=2027,availability={})
    assert a.floor_emissions_tco2.tolist()==[20.,20.,2.]
    a,_=emission_floor(f,t,[2027,2028,2029],earliest_start_year=2027,availability={'T':9999})
    assert a.floor_emissions_tco2.tolist()==[20.,20.,20.]


def test_incompatible_route_does_not_create_fictitious_zero_emissions():
    f,t=inputs();t['applies_to_unit']='NCC';t['emission_factor']=0.
    a,_=emission_floor(f,t,[2030,2050],earliest_start_year=2027,availability={})
    assert a.floor_emissions_tco2.tolist()==[20.,20.]


def test_floor_is_optimistic_even_when_route_would_be_replaced_twice():
    f,t=inputs()
    later=t.assign(tech_id='U',avail_year=2035,emission_factor=.1)
    a,d=emission_floor(f,pd.concat([t,later]),[2029,2037],earliest_start_year=2027,availability={})
    assert a.floor_emissions_tco2.tolist()==[2.,1.]
    assert d.floor_tech_id.tolist()==['T','U'] # not a one-adoption investment schedule


@pytest.mark.parametrize('field,value',[('production',-1.),('ef_inc',np.nan)])
def test_invalid_physical_inputs_rejected(field,value):
    f,t=inputs();f[field]=value
    with pytest.raises(ValueError):emission_floor(f,t,[2030],earliest_start_year=2027,availability={})
