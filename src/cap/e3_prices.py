"""E3 — correlated Monte Carlo price paths (REDESIGN_SPEC §3 E3).

Electricity, purchased hydrogen and construction CAPEX use correlated log-price
GBM/OU factors around scenario central paths. Electrolyzer residual noise uses
independent GBM. Purchased hydrogen is a separate factor in the current model.

Outputs: out/e3/price_sims.parquet (long: scenario, region, sim, year, factor, value),
         out/e3/calibration_report.csv and price_model.json
"""

from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C
from .calibration import calibrate, calibrate_for, hydrogen_price, V2_FACTORS
from .schemas import load_input
from .price_process import PriceShocks, factor_from_innovations, log_variance_path

FACTORS = ["elec", "h2", "capex"]  # v1 (historical): hydrogen independent prior, capex prior


def factor_list(cfg) -> list[str]:
    """v1: elec/h2/capex (two priors). v2: verified-series factors only (finding A3)."""
    return list(V2_FACTORS) if str(cfg.get("price_factor_set", "v1")).lower() == "v2" else list(FACTORS)


def simulate_factors(cal, years: np.ndarray, n_sims: int, rng,
                     cfg_process: str | None = None,
                     cfg_half: float | None = None,
                     cfg_norm: str | None = None,
                     factors: list[str] | None = None,
                     h2_elec_share: float | None = None) -> dict[str, np.ndarray]:
    """Correlated factors using analytic mean/median normalization.

    Electricity, hydrogen and CAPEX follow the configured log GBM/OU process.
    Electrolyzer residual noise remains independent GBM around its central trend.
    """
    T = len(years)
    if T < 2 or not np.all(np.diff(years) == 1):
        raise ValueError("Price simulation requires consecutive annual dates")
    FACTORS = list(factors) if factors is not None else globals()["FACTORS"]
    v2 = "co2" in FACTORS
    L = np.linalg.cholesky(cal.corr.loc[FACTORS, FACTORS].to_numpy())
    z = rng.standard_normal((n_sims, T, len(FACTORS))) @ L.T
    proc = str(cfg_process or "gbm").lower()
    norm = str(cfg_norm or "mean").lower()
    half = 10.0 if cfg_half is None else float(cfg_half)
    out, variance = {}, {}
    for j, f in enumerate(FACTORS):
        out[f], variance[f] = factor_from_innovations(z[:, :, j], cal.vol[f], proc, norm, half)
    sigma_meta = {f: float(cal.vol[f]) for f in FACTORS}
    proc_meta = {f: proc for f in FACTORS}
    if v2:
        # hydrogen: same innovations as electricity scaled by the electricity share
        # of the hydrogen cost (structural derivation, no independent prior). With a
        # scaled innovation the analytic variance path scales by w², so the
        # mean-normalisation shift stays exact.
        w = float(h2_elec_share if h2_elec_share is not None else 1.0)
        j = FACTORS.index("elec")
        out["h2"], variance["h2"] = factor_from_innovations(z[:, :, j], w * cal.vol["elec"], proc, norm, half)
        sigma_meta["h2"], proc_meta["h2"] = w * cal.vol["elec"], proc
        # construction capex: no verified series -> deterministic multiplier 1
        out["capex"], variance["capex"] = np.ones((n_sims, T)), np.zeros(T)
        sigma_meta["capex"], proc_meta["capex"] = 0.0, "gbm"
        out["electrolyzer"], variance["electrolyzer"] = np.ones((n_sims, T)), np.zeros(T)
    else:
        ez_z = rng.standard_normal((n_sims, T))
        out["electrolyzer"], variance["electrolyzer"] = factor_from_innovations(
            ez_z, cal.electrolyzer_vol, "gbm", norm)
    return PriceShocks(out, variance, norm, {
        "schema_version": 2, "process": proc, "ou_half_life": half,
        "normalisation": norm, "years": [int(y) for y in years],
        "factor_set": "v2" if v2 else "v1",
        "factor_process": {**proc_meta, "electrolyzer": "gbm"},
        "innovation_sigma": {**sigma_meta, "electrolyzer": float(cal.electrolyzer_vol if not v2 else 0.0)},
        "h2_elec_share": (float(h2_elec_share) if v2 else None),
        "correlation_factors": FACTORS, "correlation": cal.corr.loc[FACTORS, FACTORS].to_numpy().tolist(),
        "calibration_meta": getattr(cal, "meta", None),
    })


def run(cfg: C.Config):
    ddir = C.data_dir(cfg)
    odir = C.out_dir(cfg, "e3")
    d4 = load_input(ddir, "D4_price_history")
    cal = calibrate_for(cfg, d4)
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    rng = np.random.default_rng(cfg.seed)
    factors = factor_list(cfg)
    h2_share = None
    if "co2" in factors:
        # electricity share of the delivered hydrogen cost at scenario central prices,
        # averaged over regions/scenarios/years that carry both series (D2b)
        h = prices[prices.variable == "h2_price"].set_index(["scenario", "region", "year"]).value
        e = prices[prices.variable == "elec_price"].set_index(["scenario", "region", "year"]).value
        both = pd.concat([h.rename("h2"), e.rename("elec")], axis=1).dropna()
        share = (both.elec * cfg.hydrogen.kwh_per_kg / 1000.0) / both.h2
        h2_share = float(np.clip(share.mean(), 0.0, 1.0)) if len(both) else 1.0
        cal.vol["h2"] = h2_share * cal.vol["elec"]

    shocks = simulate_factors(cal, years, cfg.simulation.n_sims, rng,
                              cfg.get('price_process'), cfg.get('ou_halflife_years'),
                              cfg.get('shock_normalisation'), factors, h2_share)

    # persist compactly: shocks are scenario-independent multipliers; scenario central
    # paths are already in e1 output. Store shocks once (sims x years x factor).
    rows = []
    for f, arr in shocks.items():
        df = pd.DataFrame(arr, columns=years)
        df.insert(0, "sim", np.arange(arr.shape[0]))
        df.insert(0, "factor", f)
        rows.append(df)
    long = pd.concat(rows).melt(id_vars=["factor", "sim"], var_name="year", value_name="mult")
    path_file = odir / "price_sims.parquet"
    long.to_parquet(path_file, index=False)
    metadata = {**shocks.metadata, "seed": cfg.seed, "n_sims": cfg.simulation.n_sims,
                "log_variance": {k: v.tolist() for k, v in shocks.log_variance.items()},
                "calibration_input_sha256": hashlib.sha256((ddir / "D4_price_history.csv").read_bytes()).hexdigest(),
                "calibration_code_sha256": hashlib.sha256(Path(__file__).with_name("calibration.py").read_bytes()).hexdigest(),
                "paths_sha256": hashlib.sha256(path_file.read_bytes()).hexdigest()}
    (odir / "price_model.json").write_text(json.dumps(metadata, indent=2) + "\n")

    corr_pairs = [(a, b) for i, a in enumerate(factors) for b in factors[i + 1:]]
    rep = pd.DataFrame({
        "param": [f"vol_{k}" for k in cal.vol] + ["electrolyzer_decline", "electrolyzer_vol"]
                 + [f"corr_{a}_{b}" for a, b in corr_pairs],
        "value": [*cal.vol.values(), cal.electrolyzer_decline, cal.electrolyzer_vol]
                 + [float(cal.corr.loc[a, b]) for a, b in corr_pairs],
    })
    # verification: simulated stats must reproduce calibration (spec E3 검증)
    for j, f in enumerate(factors):
        lr = np.diff(np.log(shocks[f]), axis=1)
        rep.loc[len(rep)] = [f"sim_vol_{f}", float(lr.std())]
    rep.to_csv(odir / "calibration_report.csv", index=False)

    # OU log increments are not the innovations; validate the actual innovations.
    for f in factors:
        state = np.log(shocks[f])
        if shocks.normalisation == "mean":
            state = state + .5 * shocks.log_variance[f]
        phi = np.exp(-np.log(2.) / shocks.metadata["ou_half_life"]) if shocks.metadata["process"] == "ou" else 1.
        innovation = state[:, 1:] - phi * state[:, :-1]
        observed, sigma = float(innovation.std()), cal.vol[f]
        if sigma > 0:
            assert abs(observed - sigma) / sigma < .05, f"sim innovation vol drift for {f}"
    return shocks, cal


def load_shocks(cfg: C.Config) -> dict[str, np.ndarray]:
    directory = C.out_dir(cfg, "e3")
    path_file = directory / "price_sims.parquet"
    metadata_file = directory / "price_model.json"
    metadata = json.loads(metadata_file.read_text()) if metadata_file.exists() else None
    if metadata is None:
        if not cfg.get("allow_legacy_price_paths", False):
            raise ValueError("Price metadata missing; rerun E3. Historical audits must explicitly allow legacy paths.")
        warnings.warn("Loading historical paths without price-model metadata for an explicit legacy audit", stacklevel=2)
    elif metadata.get("schema_version") != 2 or metadata["paths_sha256"] != hashlib.sha256(path_file.read_bytes()).hexdigest():
        raise ValueError("Price path metadata/version mismatch; rerun E3")
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    if metadata:
        input_hash = hashlib.sha256((C.data_dir(cfg) / "D4_price_history.csv").read_bytes()).hexdigest()
        code_hash = hashlib.sha256(Path(__file__).with_name("calibration.py").read_bytes()).hexdigest()
        if metadata.get("calibration_input_sha256") != input_hash or metadata.get("calibration_code_sha256") != code_hash:
            raise ValueError("Calibration input/code changed since E3; rerun price simulation")
        if metadata["years"] != years.tolist():
            raise ValueError("Price metadata dates disagree with requested dates")
        if metadata["process"] != str(cfg.get("price_process", "gbm")).lower() or metadata["normalisation"] != str(cfg.get("shock_normalisation", "mean")).lower():
            raise ValueError("Price process/normalization disagree with stored paths; rerun E3")
        if metadata["process"] == "ou" and metadata["ou_half_life"] != cfg.get("ou_halflife_years", 10.):
            raise ValueError("OU half-life disagrees with stored paths; rerun E3")
        if metadata["n_sims"] != cfg.simulation.n_sims:
            raise ValueError("Simulation count disagrees with stored paths; rerun E3")
        if metadata["seed"] != cfg.seed:
            raise ValueError("Simulation seed disagrees with stored paths; rerun E3")
        for factor, variance in metadata["log_variance"].items():
            expected = log_variance_path(metadata["innovation_sigma"][factor], len(years),
                                         metadata["factor_process"][factor], metadata["ou_half_life"])
            if not np.allclose(variance, expected, rtol=1e-12, atol=1e-15):
                raise ValueError(f"Analytic variance disagrees with declared process: {factor}")
    long = pd.read_parquet(path_file)
    if long.duplicated(["factor", "sim", "year"]).any():
        raise ValueError("Duplicate price-path cells")
    out = {}
    for f, g in long.groupby("factor"):
        out[f] = g.pivot(index="sim", columns="year", values="mult").reindex(columns=years).to_numpy()
        if not np.isfinite(out[f]).all() or (out[f] <= 0).any():
            raise ValueError(f"Missing or invalid price cells: {f}")
    if metadata:
        if set(out) != set(metadata["log_variance"]) or any(len(v) != metadata["n_sims"] for v in out.values()):
            raise ValueError("Stored factor/sample count differs from metadata")
        return PriceShocks(out, metadata["log_variance"], metadata["normalisation"], metadata)
    return out


if __name__ == "__main__":
    run(C.load())
    print("e3 ok")
