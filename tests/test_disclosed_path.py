import numpy as np
import pytest
from cap.disclosed_path import linear_disclosed_path


def path(**kw):
    args=dict(company_id='illustration',base_year=2025,target_year=2050,
        base_emissions=100.,years=np.arange(2025,2052),
        declaration_source='2050 declaration fixture',baseline_source='normalized100 assumption',
        scope='declared boundary',accounting_basis='normalized_declaration_index',unit='index')
    return linear_disclosed_path(**(args|kw))


def test_declaration_alone_yields_comparator_without_technology_commitment():
    p=path().set_index('year')
    assert p.loc[2025,'emissions']==100
    assert p.loc[2030,'emissions']==80
    assert p.loc[2050,'emissions']==p.loc[2051,'emissions']==0
    assert not p.technology_schedule_inferred.any() and not p.cost_evaluated.any()


def test_analysis_start_does_not_restart_reduction_clock():
    p=path(years=np.arange(2027,2051)).set_index('year')
    assert p.loc[2027,'emissions']==pytest.approx(92.)


def test_absolute_scale_preserves_ratio_and_scope():
    a=path();b=path(base_emissions=8e6,unit='tCO2e',accounting_basis='net')
    np.testing.assert_allclose(a.relative_to_baseline,b.relative_to_baseline)
    assert set(b.accounting_basis)=={'net'}


@pytest.mark.parametrize('kw',[dict(declaration_source=''),dict(base_emissions=np.nan),
    dict(target_year=2025),dict(years=[2024,2025]),dict(years=[2030,2025]),
    dict(accounting_basis='gross'),dict(target_year=2050.5)])
def test_unstated_accounting_or_invalid_anchors_rejected(kw):
    with pytest.raises(ValueError):path(**kw)
