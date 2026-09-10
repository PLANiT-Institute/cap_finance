"""Analytic block second moments against exhaustive path enumeration."""
import itertools
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from research_block_price_paths import block_paths
from cap.block_moments import block_level_covariance,gaussian_level_covariance,weighted_sum_variance


@pytest.mark.parametrize('length,months',[(1,3),(2,5),(3,5),(4,7)])
def test_exact_covariance_and_discounted_cost_against_all_possible_blocks(length,months):
    r=np.array([.1,.3,-.2,.05])
    centered=r-r.mean()
    _,anchor,_=block_paths(r[:,None],months,2,length,3)
    paths=[]
    for starts in itertools.product(range(len(r)-length+1),repeat=(months+length-1)//length):
        z=np.concatenate([centered[s:s+length] for s in starts])[:months].cumsum()
        paths.append(np.exp(z-anchor[:,0]))
    x=np.asarray(paths)
    np.testing.assert_allclose(x.mean(axis=0),1,atol=1e-14)
    exact=block_level_covariance(r,months,length)
    np.testing.assert_allclose(exact,(x-1).T@(x-1)/len(x),atol=2e-14)
    w=(1.05)**-np.arange(months)
    assert weighted_sum_variance(w,exact)==pytest.approx(np.var(x@w),abs=1e-12)


def test_gaussian_moments_match_one_step_lognormal_and_constant_history():
    r=np.array([-.2,.2])
    c=gaussian_level_covariance(r,3)
    assert c[0,2]==pytest.approx(np.expm1(np.var(r,ddof=1)))
    assert c[2,2]==pytest.approx(np.expm1(3*np.var(r,ddof=1)))
    np.testing.assert_allclose(block_level_covariance(np.ones(6),24,3),0,atol=1e-14)


@pytest.mark.parametrize('args',[(np.array([np.nan]),3,1),(np.ones(2),0,1),
    (np.ones(2),3,3),(np.ones(2),3.2,1)])
def test_invalid_history_or_dimensions_rejected(args):
    with pytest.raises(ValueError):block_level_covariance(*args)
