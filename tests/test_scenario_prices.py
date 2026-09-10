"""Dimensional expenditure invariance and rejection of unsafe scenario bridges."""
from dataclasses import replace
import numpy as np
import pytest
from cap.scenario_prices import (ScenarioPriceCurve, price_unit_factor,
    interpolate_curve, convert_curve, real_currency_factor,
    stochastic_real_currency_factor, add_delivered_components)


def curve(**kw):
    fields=dict(model='reference',scenario='NZE',region='Japan',commodity='gas',
        years=(2025,2030),values=(10.,20.),quantity_unit='GJ',currency='USD',
        price_year=2024,boundary='customs_before_regasification',
        components=('commodity',),source='explicit test fixture, not observed prices')
    return ScenarioPriceCurve(**(fields|kw))


@pytest.mark.parametrize('target,quantity_in_target,metadata',[
    ('MWh',1/3.6,{}),
    ('kg_H2',1/.12,dict(gj_per_target_unit=.12,heat_basis='LHV',heat_evidence='declared fixture')),
    ('t_LNG',1/55.,dict(gj_per_target_unit=55.,heat_basis='HHV',heat_evidence='declared fixture'))])
def test_same_energy_expenditure_after_unit_change(target,quantity_in_target,metadata):
    # One GJ at100 currency/GJ must cost100 regardless of the price denominator.
    converted=100*price_unit_factor('GJ',target,**metadata)
    assert quantity_in_target*converted==pytest.approx(100)


def test_carbon_price_and_emissions_convert_in_opposite_directions():
    assert (44/12)*100*price_unit_factor('tC','tCO2')==pytest.approx(100)


def test_million_btu_is_not_one_btu():
    assert price_unit_factor('MMBtu_IT','GJ')*1.055056==pytest.approx(1)
    with pytest.raises(ValueError):price_unit_factor('MBtu','GJ')


@pytest.mark.parametrize('metadata',[{},dict(gj_per_target_unit=.12),
    dict(gj_per_target_unit=.12,heat_basis='LHV'),
    dict(gj_per_target_unit=-.12,heat_basis='LHV',heat_evidence='source')])
def test_no_silent_energy_mass_constant(metadata):
    with pytest.raises(ValueError):price_unit_factor('GJ','kg_H2',**metadata)


def test_constant_currency_and_nominal_bridge_agree_when_inflation_cancels():
    fixed=real_currency_factor(foreign_index_source=50,foreign_index_target=100,
        local_per_foreign_base=1300,evidence='synthetic indices and FX')
    actual=stochastic_real_currency_factor(foreign_index_source=50,
        foreign_index_at_t=np.array([110.,120.]),nominal_local_per_foreign=1300,
        local_index_at_t=np.array([110.,120.]),local_index_base=100,evidence='synthetic equal inflation')
    np.testing.assert_allclose(actual,fixed)
    c=convert_curve(curve(),quantity_unit='MWh',currency='KRW',price_year=2024,
        currency_factor=fixed,currency_evidence='explicit test bridge')
    np.testing.assert_allclose(c.values,[93600,187200])


def test_correlated_price_fx_means_do_not_multiply():
    price=np.array([.5,1.5]);fx=np.array([.5,1.5])
    assert price.mean()==fx.mean()==1
    assert (price*fx).mean()==1.25


def test_interpolation_preserves_nodes_and_never_extrapolates():
    c=interpolate_curve(curve(),(2025,2026,2027,2030),method='linear')
    assert c.values==(10.,12.,14.,20.)
    assert interpolate_curve(curve(),(2026,2030),method='previous').values==(10.,20.)
    for years in ((2024,2025),(2030,2031),(2026,2025),(2025,2025)):
        with pytest.raises(ValueError):interpolate_curve(curve(),years,method='linear')
    with pytest.raises(ValueError):interpolate_curve(curve(),np.array([2030,2025],dtype=np.uint64),method='linear')


@pytest.mark.parametrize('kw',[dict(region=''),dict(price_year=None),
    dict(years=(2025.,2030.)),dict(values=(10.,float('nan'))),dict(components=())])
def test_missing_source_dimensions_rejected(kw):
    with pytest.raises(ValueError):curve(**kw)


def test_delivery_adder_requires_matching_scope_and_no_overlap():
    base=curve(boundary='delivered_mapped')
    adder=replace(base,components=('regasification',),values=(2.,3.))
    total=add_delivered_components(base,adder)
    assert total.values==(12.,23.)
    for invalid in (base,replace(adder,scenario='CPS'),replace(adder,region='Korea'),
                    replace(adder,price_year=2025),replace(adder,commodity='H2'),
                    replace(adder,boundary='unmapped'),replace(adder,quantity_unit='MWh')):
        with pytest.raises(ValueError):add_delivered_components(base,invalid)


def test_zero_carbon_and_negative_netback_are_valid_levels():
    c=curve(values=(0.,-2.),commodity='coproduct')
    assert interpolate_curve(c,(2025,2030),method='linear').values==(0.,-2.)
    with pytest.raises(ValueError):convert_curve(c,quantity_unit='GJ',currency='KRW',
        price_year=2024,currency_factor=1,currency_evidence='')


def test_hhv_quotation_cannot_silently_use_lhv_mass_conversion():
    c=curve(heat_basis='HHV')
    with pytest.raises(ValueError,match='match the source'):
        convert_curve(c,quantity_unit='t_LNG',currency='USD',price_year=2024,
            currency_factor=1,currency_evidence='identity',gj_per_target_unit=50,
            heat_basis='LHV',heat_evidence='declared synthetic lower heating value')
