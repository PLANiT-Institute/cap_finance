from copy import deepcopy
import pytest
from cap.grid_factors import CONTEXT_FIELDS, select_grid_factor


def sample():
    r=dict(identifier='historical',country='KOR',gas='CO2',gwp_basis='not_applicable',energy_boundary='consumption',
           accounting_basis='national_inventory_2006IPCC',period_start=2023,period_end=2023,
           statistic='single_year',allowed_use='regional_reference',status='verified_primary',
           unit='tCO2/MWh',value=.4149,source_url='https://www.gir.go.kr/')
    return r,{k:r[k] for k in CONTEXT_FIELDS}


def test_exact_historical_use_preserves_context():
    r,c=sample();out=select_grid_factor([r],r['identifier'],context=c)
    assert out['value']==.4149 and out['context']==c
    assert not out['corporate_calibration'] and not out['future_scenario']


@pytest.mark.parametrize('key,value',[
    ('country','JPN'),('gas','CO2e'),('energy_boundary','generation'),
    ('accounting_basis','location_based_grid'),('period_start',2024),
    ('period_end',2050),('statistic','three_year_average'),
    ('allowed_use','reporting_parameter'),('allowed_use','corporate_inventory'),
])
def test_semantic_substitution_rejected(key,value):
    r,c=sample();c[key]=value
    with pytest.raises(ValueError):select_grid_factor([r],r['identifier'],context=c)


@pytest.mark.parametrize('unit,value,expected',[
    ('tCO2/kWh',.000423,.423),('kgCO2/kWh',.422,.422),('kgCO2/MWh',414.9,.4149),
])
def test_unit_conversions(unit,value,expected):
    r,c=sample();r.update(unit=unit,value=value)
    assert select_grid_factor([r],r['identifier'],context=c)['value']==pytest.approx(expected)


@pytest.mark.parametrize('status',['superseded','held_conflict','provisional'])
def test_known_source_failures_not_selectable(status):
    r,c=sample();r['status']=status
    with pytest.raises(ValueError):select_grid_factor([r],r['identifier'],context=c)


@pytest.mark.parametrize('field,value',[
    ('value',None),('value',float('nan')),('value',-1),('value',True),
    ('unit','tCO2e/MWh'),('period_start',2023.),('source_url',''),
])
def test_bad_record_rejected(field,value):
    r,c=sample();r[field]=value
    with pytest.raises(ValueError):select_grid_factor([r],r['identifier'],context=c)


def test_missing_context_and_ambiguous_id():
    r,c=sample()
    with pytest.raises(ValueError):select_grid_factor([r],r['identifier'],context={})
    with pytest.raises(ValueError):select_grid_factor([r,deepcopy(r)],r['identifier'],context=c)
    with pytest.raises(ValueError):select_grid_factor([r],'absent',context=c)


def test_co2e_requires_gwp_basis_even_without_conversion():
    r,c=sample();r.update(gas='CO2e',gwp_basis='unspecified',unit='tCO2e/MWh')
    c.update(gas='CO2e',gwp_basis='unspecified')
    with pytest.raises(ValueError):select_grid_factor([r],r['identifier'],context=c)
    r['gwp_basis']=c['gwp_basis']='AR5'
    assert select_grid_factor([r],r['identifier'],context=c)['unit']=='tCO2e/MWh'
