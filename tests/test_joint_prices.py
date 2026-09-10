"""Catch silent Monte Carlo re-pairing, currency errors and wrong index weights."""
from dataclasses import replace

import numpy as np
import pytest

from cap.scenario_prices import ScenarioPriceCurve
from cap.joint_prices import (DrawAxis, JointPricePaths, JointPriceBundle,
    FINPriceRequirement, prices_from_multipliers, indexed_procurement_price,
    paired_cost_difference)


def fixture():
    c = ScenarioPriceCurve('model', 'STEPS', 'Japan', 'gas', (2027, 2028),
        (10., 20.), 't_gas', 'KRW', 2024, 'declared_delivery', ('commodity',),
        'synthetic fixture', 'HHV')
    axis = DrawAxis(c.years, ('draw:a', 'draw:b'), 'sample:1')
    p = prices_from_multipliers(c, axis, np.array([[.5, 1.5], [1.5, .5]]),
                               evidence='synthetic joint sample')
    req = FINPriceRequirement('gas', 't_gas', 'KRW', 2024, 'declared_delivery', 'HHV')
    return p, req


@pytest.mark.parametrize('change', [dict(draw_ids=('draw:b', 'draw:a')),
    dict(sample_id='sample:2'), dict(draw_ids=('other:a', 'other:b'))])
def test_same_shape_different_states_rejected(change):
    p, _ = fixture()
    other = replace(p, axis=replace(p.axis, **change))
    with pytest.raises(ValueError, match='mismatched draw'):
        JointPriceBundle({'gas': p, 'power': other})
    with pytest.raises(ValueError, match='identical labelled'):
        paired_cost_difference([1,2], [1,2], transition_axis=p.axis, baseline_axis=other.axis)


def test_same_shape_shifted_years_rejected():
    p, _ = fixture()
    with pytest.raises(ValueError, match='years must match'):
        replace(p, axis=replace(p.axis, years=(2028,2029)))


def test_scenario_pooling_rejected_even_with_same_draws():
    p, _ = fixture()
    other = replace(p, curve=replace(p.curve, scenario='NZE'))
    with pytest.raises(ValueError, match='distinct model/scenario'):
        JointPriceBundle({'gas': p, 'power': other})


@pytest.mark.parametrize('field,value', [('currency','EUR'), ('price_year',2025),
    ('quantity_unit','MWh'), ('boundary','border'), ('commodity','hydrogen'),
    ('heat_basis','LHV')])
def test_fin_boundary_must_match_explicit_expectation(field, value):
    p, req = fixture()
    with pytest.raises(ValueError, match='mismatch'):
        JointPriceBundle({'gas':p}).to_fin_inputs({'gas':replace(req, **{field:value})}, years=p.axis.years)


def test_fin_cannot_silently_accept_foreign_currency_or_omit_channel():
    p, req = fixture()
    foreign = replace(p, curve=replace(p.curve,currency='USD'))
    with pytest.raises(ValueError, match='expects KRW'):
        JointPriceBundle({'gas':foreign}).to_fin_inputs({'gas':replace(req,currency='USD')},years=p.axis.years)
    with pytest.raises(ValueError, match='exactly one'):
        JointPriceBundle({'gas':p}).to_fin_inputs({}, years=p.axis.years)


def test_fin_array_bridge_preserves_expenditure_and_paired_feedstock_cancellation():
    p, req = fixture()
    px, shocks = JointPriceBundle({'gas':p}).to_fin_inputs({'gas':req},years=p.axis.years)
    q = np.array([3.,4.])
    np.testing.assert_allclose(q*px['gas']*shocks['gas'],q*p.values)
    baseline = (q*p.values).sum(axis=1)
    delta = np.array([7.,-2.])
    result = paired_cost_difference(baseline+delta,baseline,
        transition_axis=p.axis,baseline_axis=p.axis)
    np.testing.assert_allclose(result,delta)


def test_fixed_plus_indexed_component_needs_changing_share():
    p, _ = fixture()
    # Gas doubles centrally. Electricity =50 fixed +5*gas. Its central prices
    # become100 and150, with the indexed share rising from1/2 to2/3.
    target = replace(p.curve,commodity='power',values=(100.,150.),quantity_unit='MWh',heat_basis=None)
    mapped = indexed_procurement_price(p,target,indexed_share=(.5,2/3),evidence='synthetic tariff')
    np.testing.assert_allclose(mapped.values,50+5*p.values)
    wrong = indexed_procurement_price(p,target,indexed_share=.5,evidence='deliberately different tariff')
    assert not np.allclose(wrong.values,50+5*p.values)


@pytest.mark.parametrize('share', [-.1,1.1,[.5,.5,.5],float('nan')])
def test_invalid_mapping_share_rejected(share):
    p, _ = fixture()
    with pytest.raises(ValueError, match='Indexed share'):
        indexed_procurement_price(p,p.curve,indexed_share=share,evidence='synthetic tariff')


def test_zero_and_negative_prices_do_not_disappear_at_legacy_bridge():
    p, req = fixture()
    fixed = replace(p,curve=replace(p.curve,values=(0.,-2.)),values=np.array([[0.,-1.],[0.,-3.]]))
    px,s=JointPriceBundle({'gas':fixed}).to_fin_inputs({'gas':req},years=p.axis.years)
    np.testing.assert_allclose(px['gas']*s['gas'],fixed.values)
    for values in (np.array([[1.,-1.],[0.,-3.]]),np.array([[0.,1.],[0.,-3.]])):
        with pytest.raises(ValueError):
            JointPriceBundle({'gas':replace(fixed,values=values)}).to_fin_inputs({'gas':req},years=p.axis.years)


def test_immutable_paths_and_duplicate_ids():
    p,_=fixture()
    values=p.values.copy()
    owned=replace(p,values=values)
    values[:]=999
    assert not np.array_equal(owned.values,values)
    with pytest.raises(ValueError):owned.values[0,0]=999
    with pytest.raises(ValueError):owned.values.setflags(write=True)
    with pytest.raises(ValueError):replace(p.axis,draw_ids=('a','a'))


def test_shape_broadcasting_not_allowed_for_paths():
    p,_=fixture()
    with pytest.raises(ValueError):replace(p,values=np.array([1.,2.]))
    with pytest.raises(ValueError):prices_from_multipliers(p.curve,p.axis,np.ones((1,2)),evidence='fixture')


def test_native_fin_unit_and_shared_power_shock_cannot_be_overridden():
    p, req=fixture()
    with pytest.raises(ValueError,match='physical profile requires'):
        JointPriceBundle({'gas':replace(p,curve=replace(p.curve,quantity_unit='GJ'))}).to_fin_inputs(
            {'gas':replace(req,quantity_unit='GJ')},years=p.axis.years)
    power=replace(p,curve=replace(p.curve,commodity='power',quantity_unit='MWh',heat_basis=None))
    preq=replace(req,commodity='power',quantity_unit='MWh',heat_basis=None)
    renewable=replace(power,values=power.values[::-1])
    with pytest.raises(ValueError,match='shares one elec shock'):
        JointPriceBundle({'elec':power,'re':renewable}).to_fin_inputs(
            {'elec':preq,'re':preq},years=p.axis.years)


def test_different_real_price_years_cannot_be_added():
    p,req=fixture()
    later=replace(p,curve=replace(p.curve,price_year=2025))
    with pytest.raises(ValueError,match='constant-currency years'):
        JointPriceBundle({'gas':p,'extra':later}).to_fin_inputs(
            {'gas':req,'extra':replace(req,price_year=2025)},years=p.axis.years)


def test_actual_additional_flow_units_are_checked_before_fin():
    from types import SimpleNamespace
    from cap.commodity_ledger import CommodityFlow
    p,req=fixture()
    flow=CommodityFlow('feedstock','feedstock',np.ones(2),'kg','purchased','test')
    profile=SimpleNamespace(additional_commodity_flows=(flow,))
    names=('elec','re','h2','gas','coal','co2','feedstock')
    bundle=JointPriceBundle({k:p for k in names})
    with pytest.raises(ValueError,match='physical flow and price denominator'):
        bundle.fin_inputs_for_profile(profile,{k:req for k in names},years=p.axis.years)


def test_strict_bridge_rejects_unknown_embedded_price_basis():
    from types import SimpleNamespace
    p,req=fixture()
    units={'elec':'MWh','re':'MWh','h2':'kg_H2','gas':'t_gas','coal':'t_coal','co2':'tCO2'}
    prices={k:replace(p,curve=replace(p.curve,commodity=k,quantity_unit=u)) for k,u in units.items()}
    requirements={k:replace(req,commodity=k,quantity_unit=u) for k,u in units.items()}
    profile=SimpleNamespace(additional_commodity_flows=(),other_cost_k=np.ones(2),
                            embedded_price_basis=None,profile_years=p.axis.years)
    bundle=JointPriceBundle(prices)
    with pytest.raises(ValueError,match='embedded-price provenance'):
        bundle.fin_inputs_for_profile(profile,requirements,years=p.axis.years)
    # The author may explicitly declare an entirely non-price-indexed other cost.
    profile.embedded_price_basis={}
    px,_=bundle.fin_inputs_for_profile(profile,requirements,years=p.axis.years)
    assert set(px)==set(units)
