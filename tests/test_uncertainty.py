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


# --- L2/FC4: 탄소가격 확률 축 -------------------------------------------------

def _plan_profile(emis: float):
    from cap.plancost import PlanProfile
    T = 4
    z = np.zeros(T)
    return PlanProfile(z.copy(), z.copy(), z.copy(), z.copy(), z.copy(), {}, {},
                       np.full(T, emis), ppa=0.0, epc=0, ccfd=0)


def _cfg_px_shocks(n=5, T=4):
    cfg = C.Config({"years": {"start": 2025, "end": 2028}, "discount_rate": 0.0,
                    "carbon_auction_share": {2025: 1.0},
                    "contracts": {"ppa_premium_pct": 0.0, "epc_premium_pct": 0.0,
                                  "ccfd_fee_pct": 0.0},
                    "data_dir": "data/prepared"})
    px = {k: np.zeros(T) for k in ("elec", "re", "h2", "coal", "gas")}
    px["co2"] = np.full(T, 50.0)
    shocks = {k: np.ones((n, T)) for k in ("elec", "h2", "capex")}
    return cfg, px, shocks


def test_absent_co2_shock_leaves_every_existing_number_unchanged():
    """확률화는 opt-in이어야 한다 — 'co2' 키가 없거나 1이면 기존 파이프라인과 동일."""
    from cap.plancost import simulate_cost
    cfg, px, shocks = _cfg_px_shocks()
    p, sup = _plan_profile(1000.0), {"subsidy": {}, "ccfd_strike": None}
    base = simulate_cost(p, px, shocks, sup, cfg)
    ones = simulate_cost(p, px, {**shocks, "co2": np.ones_like(shocks["elec"])}, sup, cfg)
    assert np.allclose(base, ones)


def test_co2_shock_moves_only_the_carbon_channel_and_scales_with_emissions():
    """충격이 탄소비용에만 닿는지. 배출 0이면 정책 위험도 0이어야 한다."""
    from cap.plancost import simulate_cost
    cfg, px, shocks = _cfg_px_shocks()
    sup = {"subsidy": {}, "ccfd_strike": None}
    sh2 = {**shocks, "co2": np.full_like(shocks["elec"], 2.0)}
    hot = simulate_cost(_plan_profile(1000.0), px, sh2, sup, cfg)
    cold = simulate_cost(_plan_profile(1000.0), px, shocks, sup, cfg)
    assert np.allclose(hot, 2.0 * cold)                       # 탄소비용이 유일한 비용
    zero = _plan_profile(0.0)
    assert np.allclose(simulate_cost(zero, px, sh2, sup, cfg),
                       simulate_cost(zero, px, shocks, sup, cfg))


def test_co2_shocks_are_mean_one_and_start_known():
    from uncertainty_propagation import co2_shocks
    cfg = C.Config({"seed": 7, "shock_normalisation": "mean"})
    s = co2_shocks(cfg, 30, 20000, 0.363)
    assert np.allclose(s[:, 0], 1.0)                          # 0년차 = 오늘, 분산 없음
    # 평균 1 규약은 로그공간에서 검정한다. σ=0.36·29년이면 로그정규 평균은 소수의 경로가
    # 지배해 20,000회로도 표본평균이 ±7%까지 흔들린다(꼬리가 두껍다는 것 자체가 §4의 논지).
    lg = np.log(s[:, -1])
    assert abs(lg.mean() + 0.5 * lg.var()) < 0.02             # E[shock]=1 ⇔ μ = −σ²/2
    assert s[:, -1].std() > s[:, 1].std()                     # GBM: 분산이 T에 비례해 벌어진다


def test_co2_vol_comes_from_the_kau_series_not_a_prior():
    from cap.calibration import _annual_vol
    from uncertainty_propagation import KAU, co2_vol
    cfg = C.load(data_dir="data/prepared")
    v, n, src = co2_vol(cfg)
    d4 = pd.read_csv(C.data_dir(cfg) / "D4_price_history.csv")
    d4["date"] = pd.to_datetime(d4.date.astype(str), format="mixed")
    s = d4[d4.series_id == KAU].set_index("date").value.sort_index()
    assert n == len(s) >= 6 and src
    assert abs(v - _annual_vol(s)[0]) < 1e-12
    assert v > 0.30          # K-ETS 실측: 전력(0.242)보다 크다 — 이 사실이 §4의 논지다


def test_evidence_bands_carry_literature_not_a_convention():
    """G2(D10) — 밴드가 (a) 값을 바꾸지 않고 (b) 규약이 아니라 파일에서 오며
    (c) 대칭이 아니라는 것. (c)가 깨지면 이 사이클의 결론(±30% 규약은 폭이 아니라
    중심이 틀렸다)이 성립하지 않는다."""
    from uncertainty_propagation import evidence_bands
    cfg = C.load(data_dir="data/prepared")
    prep = C.data_dir(cfg)
    tb = pd.read_csv(prep / "D3b_tech_bands.csv")
    d3 = pd.read_csv(prep / "D3_tech_options.csv")

    # (a) 밴드를 붙였다고 D3 값이 밴드 안으로 끌려 들어가지 않았다 — 하나는 밖에 있다
    vals = {(r.tech_id, r.field): float(d3.loc[d3.tech_id == r.tech_id, r.field].iloc[0])
            for r in tb.itertuples()}
    outside = [k for k, v in vals.items()
               if not (tb.set_index(["tech_id", "field"]).loc[k].value_low <= v
                       <= tb.set_index(["tech_id", "field"]).loc[k].value_high)]
    assert outside, "밴드 밖 값이 하나도 없다 — 값이 조용히 밴드에 맞춰졌는지 확인할 것"

    # (b) 승수 구간이 파일의 [low/value, high/value] 포락과 정확히 일치
    env = evidence_bands(cfg)
    assert env, "D3b_tech_bands.csv가 승수 구간으로 옮겨지지 않았다"
    for p, (lo, hi) in env.items():
        col = {"tech.capex": "capex_unit", "tech.emission_factor": "emission_factor",
               "tech.elec_intensity": "elec_intensity", "tech.h2_intensity": "h2_intensity",
               "tech.opex_var": "opex_var", "tech.opex_fixed": "opex_fixed"}[p]
        sub = tb[tb.field == col]
        assert abs(lo - min(r.value_low / vals[(r.tech_id, col)] for r in sub.itertuples())) < 1e-9
        assert abs(hi - max(r.value_high / vals[(r.tech_id, col)] for r in sub.itertuples())) < 1e-9
        # (c) 1이 구간 안쪽이 아니라 끝(또는 밖)에 있다 = 규약의 대칭 추첨과 다르다
        assert lo >= 1.0 or hi <= 1.0, f"{p} 구간이 1을 안쪽에 둔다 — 대칭 규약과 구별되지 않는다"
