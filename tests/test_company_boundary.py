import pytest
from cap.company_boundary import reported_electricity_mwh,process_intensity,coverage_requirement

def test_unidentified_electricity_conversion_is_rejected():
 with pytest.raises(ValueError):reported_electricity_mwh(10963428,reported_gj_per_purchased_mwh=None)
 assert reported_electricity_mwh(360,reported_gj_per_purchased_mwh=3.6)==100

def test_capacity_statistic_is_not_an_unconditional_upper_bound():
 assert process_intensity(100,10,utilization=.5,process_energy_fraction=.75)==15
 assert process_intensity(100,10,utilization=1,process_energy_fraction=.75)==7.5

@pytest.mark.parametrize('u,f',[(0,.5),(None,.5),(.5,None),(1.1,.5),(.5,-.1),(True,.5)])
def test_unidentified_or_invalid_process_denominator(u,f):
 with pytest.raises(ValueError):process_intensity(100,10,utilization=u,process_energy_fraction=f)

def test_whole_site_removal_leaves_other_company_emissions():
 r=coverage_requirement(5902878,4972089,covered_residual_fraction=0,target_fraction=0)
 assert r['outside_baseline']==930789
 assert r['additional_outside_reduction_required']==930789
 assert r['possible_using_outside_reduction_only']

def test_other_sites_cannot_offset_covered_residual_by_negative_emissions():
 r=coverage_requirement(100,80,covered_residual_fraction=.1,target_fraction=0)
 assert r['additional_outside_reduction_required']==28
 assert not r['possible_using_outside_reduction_only']

def test_met_target_needs_no_extra_action():
 assert coverage_requirement(100,80,covered_residual_fraction=0,target_fraction=.3)['additional_outside_reduction_required']==0

@pytest.mark.parametrize('total,covered',[(100,101),(100,None),(-1,0)])
def test_coverage_boundary_errors(total,covered):
 with pytest.raises(ValueError):coverage_requirement(total,covered,covered_residual_fraction=0,target_fraction=0)
