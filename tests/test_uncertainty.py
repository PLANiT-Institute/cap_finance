"""F3 불확실성 분해기 — 산술과 경계 성질.

전 파이프라인을 돌리는 것은 여기서 하지 않는다(스크립트가 한다). 대신 분해가
**가법성을 가장하지 않는지**, 교란이 곱수 1에서 항등인지, vol 교란이 결정론적
가격 경로에서 아무 일도 하지 않는지를 본다 — 셋 다 틀리면 표의 해석이 바뀐다.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from cap import config as C  # noqa: E402
from uncertainty_propagation import decompose, perturb, tcar  # noqa: E402


def test_tcar_matches_normal_quantile_gap():
    x = np.random.default_rng(0).normal(100.0, 10.0, 400_000)
    assert abs(tcar(x) - 1.2816 * 10.0) < 0.2


def test_decomposition_keeps_the_interaction_residual():
    rng = np.random.default_rng(1)
    price = rng.normal(0, 3.0, 50_000)
    param = rng.normal(0, 1.0, 50_000)
    joint = rng.normal(0, np.hypot(3.0, 1.0), 50_000)
    d = decompose(price, param, joint)
    # 분위수는 가법적이지 않다 — 잔차가 0이 아니고, 명시적으로 보고돼야 한다
    assert abs(d["interaction"] - (d["tcar_joint"] - d["tcar_price"] - d["tcar_param"])) < 1e-9
    assert d["interaction"] < 0          # sqrt(a²+b²) < a+b
    assert 0 < d["param_share_pct"] < 100


def _frames():
    fac = pd.DataFrame({"capacity": [1.0, 2.0], "ef_inc": [1.5, 1.6]})
    d3 = pd.DataFrame({"capex_unit": [100.0], "h2_intensity": [30.0]})
    shocks = {"elec": np.full((3, 4), 1.2), "h2": np.full((3, 4), 0.8)}
    return C.Config({"discount_rate": 0.05}), fac, d3, shocks


def test_unit_multiplier_is_identity():
    cfg, fac, d3, shocks = _frames()
    mult = {"cfg.discount": 1.0, "fac.capacity": 1.0, "tech.capex": 1.0,
            "price.h2": 1.0, "vol.elec": 1.0}
    c2, f2, d32, pxs, sh2 = perturb(cfg, fac, d3, shocks, mult)
    assert c2.discount_rate == 0.05
    pd.testing.assert_frame_equal(f2, fac)
    pd.testing.assert_frame_equal(d32, d3)
    assert pxs == {"h2": 1.0}
    assert np.allclose(sh2["elec"], shocks["elec"])


def test_vol_perturbation_cannot_move_a_deterministic_path():
    """파라미터-단독 통과에서 vol은 정의상 아무 일도 하지 않는다 — 이 성질이 깨지면
    '가격분/파라미터분' 라벨이 거짓이 된다."""
    cfg, fac, d3, _ = _frames()
    ones = {"elec": np.ones((1, 4)), "h2": np.ones((1, 4))}
    _, _, _, _, sh = perturb(cfg, fac, d3, ones, {"vol.elec": 1.8, "vol.h2": 0.4})
    assert np.allclose(sh["elec"], 1.0) and np.allclose(sh["h2"], 1.0)


def test_perturbation_scales_the_right_column_only():
    cfg, fac, d3, shocks = _frames()
    _, f2, d32, _, sh2 = perturb(cfg, fac, d3, shocks,
                                 {"fac.capacity": 1.3, "tech.capex": 0.7, "vol.elec": 2.0})
    assert np.allclose(f2.capacity, fac.capacity * 1.3)
    assert np.allclose(f2.ef_inc, fac.ef_inc)          # 다른 열은 그대로
    assert np.allclose(d32.capex_unit, d3.capex_unit * 0.7)
    assert np.allclose(sh2["elec"], shocks["elec"] ** 2.0)
    assert np.allclose(sh2["h2"], shocks["h2"])
