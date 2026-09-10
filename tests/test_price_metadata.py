"""Production price metadata, process normalization and safe transformations."""
import json
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from cap import config as C
from cap.e3_prices import FACTORS, simulate_factors, run, load_shocks
from cap.price_process import PriceShocks, technology_capex_multiplier, log_variance_path


def calibration():
    return SimpleNamespace(corr=pd.DataFrame(np.eye(3),index=FACTORS,columns=FACTORS),
                           vol={'elec':.15,'h2':.25,'capex':.06},electrolyzer_vol=.1)


@pytest.mark.parametrize('process',['gbm','ou'])
def test_actual_e3_respects_both_normalizations(process):
    args=(calibration(),np.arange(2025,2051),2000)
    a=simulate_factors(*args,np.random.default_rng(71),process,2.,'mean')
    b=simulate_factors(*args,np.random.default_rng(71),process,2.,'median')
    for factor in a:
        np.testing.assert_allclose(b[factor]/a[factor],np.broadcast_to(np.exp(a.log_variance[factor]/2),a[factor].shape))
    np.testing.assert_allclose(a.log_variance['capex'],log_variance_path(.06,26,process,2.))


def test_subsampling_and_rescaling_keep_variance_and_positive_cost():
    s=simulate_factors(calibration(),np.arange(2025,2051),100,np.random.default_rng(61),'ou',2.,'mean')
    scaled=s.rescale('capex',2.).subset(7)
    reference=s.subset(7).rescale('capex',2.)
    np.testing.assert_array_equal(scaled['capex'],reference['capex'])
    np.testing.assert_allclose(scaled.log_variance['capex'],s.log_variance['capex']*4)
    assert np.all(technology_capex_multiplier(scaled,1.5)>0)
    with pytest.raises(ValueError,match='metadata'):technology_capex_multiplier(dict(scaled),1.5)
    augmented=scaled.with_factor('co2',np.ones_like(scaled['elec']))
    np.testing.assert_array_equal(technology_capex_multiplier(augmented,1.5),technology_capex_multiplier(scaled,1.5))
    for count in (-1, 0, True, 1.5):
        with pytest.raises(ValueError,match='positive integer'):s.subset(count)


def test_e3_roundtrip_rejects_stale_metadata(tmp_path):
    cfg=C.load(out_dir=str(tmp_path),simulation={'n_sims':2000},price_process='ou',ou_halflife_years=1.,shock_normalisation='median')
    # E3 currently reads the central-path file for stage ordering.
    (tmp_path/'e1').mkdir();pd.DataFrame({'unused':[]}).to_csv(tmp_path/'e1/price_paths_central.csv',index=False)
    actual,_=run(cfg);loaded=load_shocks(cfg)
    for f in actual:
        np.testing.assert_array_equal(actual[f],loaded[f])
        np.testing.assert_array_equal(actual.log_variance[f],loaded.log_variance[f])
    changed=C.Config({**cfg,'shock_normalisation':'mean'})
    with pytest.raises(ValueError,match='normalization'):load_shocks(changed)
    with pytest.raises(ValueError,match='half-life'):load_shocks(C.Config({**cfg,'ou_halflife_years':4.}))
    with pytest.raises(ValueError,match='count'):load_shocks(C.Config({**cfg,'simulation':{'n_sims':4000}}))
    with pytest.raises(ValueError,match='seed'):load_shocks(C.Config({**cfg,'seed':cfg.seed+1}))
    meta=tmp_path/'e3/price_model.json';saved=json.loads(meta.read_text());saved['paths_sha256']='bad';meta.write_text(json.dumps(saved))
    with pytest.raises(ValueError,match='mismatch'):load_shocks(cfg)
    meta.unlink()
    with pytest.raises(ValueError,match='missing'):load_shocks(cfg)
    with pytest.warns(UserWarning,match='legacy audit'):
        old=load_shocks(C.Config({**cfg,'allow_legacy_price_paths':True}))
    assert type(old) is dict


def test_extreme_valid_ou_half_lives_are_finite():
    for half in (1e-20,1e20):
        v=log_variance_path(.2,26,'ou',half)
        assert np.isfinite(v).all() and v[0]==0
    np.testing.assert_allclose(log_variance_path(.2,26,'ou',1e20),log_variance_path(.2,26,'gbm'))
