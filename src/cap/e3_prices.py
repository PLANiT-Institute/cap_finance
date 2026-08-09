"""E3 — correlated Monte Carlo price paths (REDESIGN_SPEC §3 E3).

Factors simulated: electricity, capex index (correlated GBM shocks around the
scenario central path), electrolyzer capex (independent trend+noise).
Hydrogen is NOT simulated independently: h2 = f(elec, electrolyzer capex)
via calibration.hydrogen_price — 설계서 §3 구조식 원칙.

Outputs: out/e3/price_sims.parquet (long: scenario, region, sim, year, factor, value),
         out/e3/calibration_report.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .calibration import calibrate, hydrogen_price
from .schemas import load_input

FACTORS = ["elec", "h2", "capex"]  # v2.1: hydrogen independent (외부 조달 상품)


def simulate_factors(cal, years: np.ndarray, n_sims: int, rng,
                     cfg_process: str | None = None,
                     cfg_half: float | None = None,
                     cfg_norm: str | None = None) -> dict[str, np.ndarray]:
    """Multiplicative shock paths (sims x years), mean-one, GBM-style around central."""
    T = len(years)
    L = np.linalg.cholesky(cal.corr.loc[FACTORS, FACTORS].to_numpy())
    z = rng.standard_normal((n_sims, T, len(FACTORS))) @ L.T
    z[:, 0, :] = 0.0  # year 0 is "today": price known, dispersion starts in year 1
    # I3: GBM(랜덤워크) vs OU(평균회귀). 같은 1년 변동성을 쓰되 **분산의 시간구조**가 다르다 —
    # GBM은 T에 비례해 벌어지고 OU는 포화한다. 우리 D4는 관측이 10~19개뿐이라 둘을 통계적으로
    # 가를 수 없다(docs/process_alternative.md). 그래서 선택을 config로 드러내고 차이를 잰다.
    proc = str(cfg_process or "gbm").lower()
    norm = str(cfg_norm or "mean").lower()
    half = float(cfg_half or 10.0)
    phi = np.exp(-np.log(2.0) / half) if proc == "ou" else None

    out = {}
    for j, f in enumerate(FACTORS):
        sig = cal.vol[f]
        if phi is None:                     # GBM: 로그공간 랜덤워크
            # 정규화 선택(A-24). mean: E[shock]=1 — 대신 로그정규 왜도 때문에 **중앙값이
            # 아래로 흐른다**(σ=0.25·25년이면 2050 중앙값 0.47). ②는 P50 지표이므로 그
            # 세계에서 계산된다. median: 중앙값을 중심경로에 고정하고 평균이 위로 간다.
            # D2b 중심경로가 '평균'인지 '중앙값'인지 출처가 말하지 않으므로 선택을 드러낸다.
            drift = -0.5 * sig**2 if norm == "mean" else 0.0
            inc = z[:, :, j] * sig + drift
            inc[:, 0] = 0.0
            out[f] = np.exp(np.cumsum(inc, axis=1))
        else:                               # OU: 로그공간 평균회귀 (1기 혁신은 GBM과 동일)
            y = np.zeros((n_sims, T))
            for t in range(1, T):
                y[:, t] = phi * y[:, t - 1] + sig * z[:, t, j]
            out[f] = np.exp(y - 0.5 * y.var(axis=0, keepdims=True))   # E[shock]=1 보정
    # electrolyzer capex: calibrated decline is already in the central path; simulate
    # residual noise around it (independent of market factors by construction)
    ez_z = rng.standard_normal((n_sims, T))
    ez_inc = ez_z * cal.electrolyzer_vol - 0.5 * cal.electrolyzer_vol**2
    ez_inc[:, 0] = 0.0
    out["electrolyzer"] = np.exp(np.cumsum(ez_inc, axis=1))
    return out


def run(cfg: C.Config):
    ddir = C.data_dir(cfg)
    odir = C.out_dir(cfg, "e3")
    d4 = load_input(ddir, "D4_price_history")
    cal = calibrate(d4)
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    rng = np.random.default_rng(cfg.seed)

    shocks = simulate_factors(cal, years, cfg.simulation.n_sims, rng,
                              cfg.get('price_process'), cfg.get('ou_halflife_years'),
                              cfg.get('shock_normalisation'))

    # persist compactly: shocks are scenario-independent multipliers; scenario central
    # paths are already in e1 output. Store shocks once (sims x years x factor).
    rows = []
    for f, arr in shocks.items():
        df = pd.DataFrame(arr, columns=years)
        df.insert(0, "sim", np.arange(arr.shape[0]))
        df.insert(0, "factor", f)
        rows.append(df)
    long = pd.concat(rows).melt(id_vars=["factor", "sim"], var_name="year", value_name="mult")
    long.to_parquet(odir / "price_sims.parquet", index=False)

    rep = pd.DataFrame({
        "param": [f"vol_{k}" for k in cal.vol] + ["electrolyzer_decline", "electrolyzer_vol",
                                                  "corr_elec_capex"],
        "value": [*cal.vol.values(), cal.electrolyzer_decline, cal.electrolyzer_vol,
                  float(cal.corr.loc["elec", "capex"])],
    })
    # verification: simulated stats must reproduce calibration (spec E3 검증)
    for j, f in enumerate(FACTORS):
        lr = np.diff(np.log(shocks[f]), axis=1)
        rep.loc[len(rep)] = [f"sim_vol_{f}", float(lr.std())]
    rep.to_csv(odir / "calibration_report.csv", index=False)

    sv = {f: float(np.diff(np.log(shocks[f]), axis=1).std()) for f in FACTORS}
    for f in FACTORS:
        assert abs(sv[f] - cal.vol[f]) / cal.vol[f] < 0.05, f"sim vol drift for {f}"
    return shocks, cal


def load_shocks(cfg: C.Config) -> dict[str, np.ndarray]:
    long = pd.read_parquet(C.out_dir(cfg, "e3") / "price_sims.parquet")
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    out = {}
    for f, g in long.groupby("factor"):
        out[f] = (g.pivot(index="sim", columns="year", values="mult")
                  .reindex(columns=years).to_numpy())
    return out


if __name__ == "__main__":
    run(C.load())
    print("e3 ok")
