import pytest

from cap.energy_balance import retained_energy


def test_explicit_partial_displacement_does_not_follow_emission_factor():
    row = dict(retrofit=1,retained_coal_fraction=1.,retained_gas_fraction=.5,
               retained_grid_fraction=.8,emission_factor=.1)
    assert retained_energy(row,{}) == (1.,.5,.8)
    row['emission_factor']=100
    assert retained_energy(row,{}) == (1.,.5,.8)


def test_unverified_missing_partial_or_out_of_range_retention_is_rejected():
    row = dict(retrofit=1,retained_coal_fraction=1.,retained_gas_fraction=.5,
               retained_grid_fraction=.8)
    for change in [dict(retained_gas_fraction=None),dict(retained_grid_fraction=1.1),
                   dict(retained_coal_fraction=-.1)]:
        with pytest.raises(ValueError):retained_energy({**row,**change},{})
    with pytest.raises(ValueError):retained_energy(dict(retrofit=0),{})


def test_baseline_and_explicit_historical_mode_are_distinct():
    assert retained_energy(None,{}) == (1.,1.,1.)
    assert retained_energy(dict(retrofit=0),dict(energy_balance_mode='legacy_retrofit_all')) == (0.,0.,0.)
    assert retained_energy(dict(retrofit=1),dict(energy_balance_mode='legacy_retrofit_all')) == (1.,1.,1.)
