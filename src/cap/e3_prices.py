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


def simulate_factors(cal, years: np.ndarray, n_sims: int, rng) -> dict[str, np.ndarray]:
    """Multiplicative shock paths (sims x years), mean-one, GBM-style around central."""
    T = len(years)
    L = np.linalg.cholesky(cal.corr.loc[FACTORS, FACTORS].to_numpy())
    z = rng.standard_normal((n_sims, T, len(FACTORS))) @ L.T
    z[:, 0, :] = 0.0  # year 0 is "today": price known, dispersion starts in year 1
    out = {}
    for j, f in enumerate(FACTORS):
        sig = cal.vol[f]
        # cumulative log shocks with drift correction so E[shock]=1 each year
        inc = z[:, :, j] * sig - 0.5 * sig**2
        inc[:, 0] = 0.0
        out[f] = np.exp(np.cumsum(inc, axis=1))
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

    shocks = simulate_factors(cal, years, cfg.simulation.n_sims, rng)

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
