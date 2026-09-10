"""Independent Gaussian quadrature checks of the production positive price model."""
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from cap.price_process import factor_from_innovations,log_variance_path,scale_lognormal_multiplier


@pytest.mark.parametrize("variance",[.01,.36,1.])
@pytest.mark.parametrize("amplitude",[0.,.75,1.,1.5,2.])
def test_mean_one_against_independent_gaussian_quadrature(variance,amplitude):
    # Gauss-Hermite integrates the Gaussian law independently of sampled paths.
    nodes,weights=np.polynomial.hermite.hermgauss(80)
    shocks=np.exp(np.sqrt(2*variance)*nodes-variance/2)
    value=scale_lognormal_multiplier(shocks,amplitude,variance,"mean")
    assert np.all(value>0)
    assert abs(np.dot(weights,value)/np.sqrt(np.pi)-1)<1e-10


def test_same_path_mapping_and_median_normalization():
    s=np.array([.01,.3,1.,2.,100.])
    out=scale_lognormal_multiplier(s,1.5,.2,"median")
    assert np.all(np.diff(out)>0)
    assert out[2]==1.
    assert (1+(s[1]-1)*1.5)<0 and out[1]>0
    np.testing.assert_array_equal(scale_lognormal_multiplier(s,1.,.2),s)


@pytest.mark.parametrize("process",["gbm","ou"])
def test_process_moments_and_normalization_with_same_innovations(process):
    rng=np.random.default_rng(732)
    z=rng.normal(size=(100_000,26))
    mean,v=factor_from_innovations(z,.2,process,"mean",4.)
    median,vm=factor_from_innovations(z,.2,process,"median",4.)
    np.testing.assert_array_equal(mean[:,0],np.ones(len(z)))
    np.testing.assert_allclose(median/mean,np.broadcast_to(np.exp(v/2),mean.shape))
    assert abs(mean[:,-1].mean()-1)<.012
    assert abs(np.median(median[:,-1])-1)<.012
    assert abs(np.var(np.log(mean[:,-1]))-v[-1])/v[-1]<.012
    # Normalization does not depend on unrelated Monte Carlo paths in a batch.
    sub,_=factor_from_innovations(z[:100],.2,process,"mean",4.)
    np.testing.assert_array_equal(sub,mean[:100])


def test_ou_variance_saturates_while_gbm_increases():
    v=log_variance_path(.2,1000,"ou",4.)
    stationary=.2**2/(1-2**(-2/4))
    assert abs(v[-1]-stationary)<1e-12
    assert log_variance_path(.2,1000,"gbm")[-1]>100*v[-1]


@pytest.mark.parametrize("shock,amplitude,variance,norm",[
    ([0.],1.,.2,"mean"),([-1.],1.,.2,"mean"),([np.nan],1.,.2,"mean"),
    ([1.],-1.,.2,"mean"),([1.],1.,-.2,"mean"),([1.],1.,.2,"invalid")])
def test_invalid_price_model_inputs_are_rejected(shock,amplitude,variance,norm):
    with pytest.raises(ValueError):scale_lognormal_multiplier(shock,amplitude,variance,norm)
