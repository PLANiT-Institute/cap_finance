"""Control boundary and paired FIN identities for the workbook's partial case."""
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ncc_joint_control import DEFAULTS,validate_controls,evaluate


@pytest.mark.parametrize('key,value',[('production_t',None),('paths',True),('seed',.5),
    ('end_year',2051),('alpha',1),('discount_rate',-1),('power_indexed_share',1.1),
    ('methane_sale_fraction',-.1),('KRW2024_per_EUR2024',0)])
def test_bad_controls_fail_before_sampling(key,value):
    with pytest.raises(ValueError):validate_controls(dict(DEFAULTS,**{key:value}))


def test_naphtha_anchor_changes_total_cost_but_cancels_in_incremental_cost():
    controls=dict(DEFAULTS,paths=150,end_year=2031)
    a,da=evaluate(controls);b,db=evaluate(dict(controls,naphtha_EUR2024_t=1200))
    assert b['baseline_mean_bnKRW2024']>a['baseline_mean_bnKRW2024']
    np.testing.assert_allclose(da['incremental'],db['incremental'],rtol=1e-12,atol=1e-9)


def test_zero_production_is_valid_but_blank_is_not():
    result,draws=evaluate(dict(DEFAULTS,paths=20,end_year=2027,production_t=0))
    assert result['metrics']['mean']==result['metrics']['tcar']==0
    assert all(np.array_equal(d,np.zeros(20)) for d in draws.values())


def test_negative_netback_is_a_disposal_cost_not_a_sales_credit():
    controls=dict(DEFAULTS,paths=100,end_year=2027)
    a,da=evaluate(dict(controls,methane_EUR2024_t=0))
    b,db=evaluate(dict(controls,methane_EUR2024_t=-100))
    assert (db['incremental']>da['incremental']).all()


def test_shared_index_cancellation_and_source_quantities():
    beta=.488*500/(6.78*100)
    result,draws=evaluate(dict(DEFAULTS,paths=200,end_year=2031,power_indexed_share=beta))
    assert result['quantities']['added_electricity_MWh_t']==pytest.approx(6.78)
    assert np.ptp(draws['incremental'])<1e-8
    assert result['metrics']['mean']==pytest.approx(result['theoretical_mean_bnKRW2024'])
