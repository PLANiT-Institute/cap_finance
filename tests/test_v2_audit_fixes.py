"""Regression tests for the 2026-09-10 external-audit fixes (methodology v2).

A1  risk axis on the plan's own cost distribution (es_abs / tcar_abs)
A2  incremental hedge basis: PPA fixes only the electricity the transition adds
A3  verified-series-only calibration: no priors, non-identity correlation, PSD
B3  frontier flags computed on the decision-eligible set only
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cap.calibration import FACTOR_SERIES_V2, calibrate_v2  # noqa: E402
from cap.e3_prices import simulate_factors  # noqa: E402
from cap.plancost import PlanProfile, simulate_cost  # noqa: E402
from cap.risk_metrics import loss_summary, pareto_mask  # noqa: E402


def _d4():
    rng = np.random.default_rng(1)
    rows = []
    years = list(range(2010, 2026))
    base = {"smp_krw_mwh": 90., "jepx_spot": 10., "kau_krw": 20000., "wb_coal_au_usd_t": 100., "wb_japan_lng_usd_mmbtu": 12.}
    common = rng.standard_normal(len(years)) * 0.2
    for sid, lvl in base.items():
        own = rng.standard_normal(len(years)) * 0.1
        path = lvl * np.exp(np.cumsum(common * (0.0 if sid == "kau_krw" else 1.0) + own))
        rows += [{"date": str(y), "series_id": sid, "value": float(v), "unit": "u", "source_id": "TEST"} for y, v in zip(years, path)]
    rows.append({"date": "2023", "series_id": "electrolyzer_capex", "value": 2.9e6, "unit": "KRW/kW", "source_id": "TEST"})
    return pd.DataFrame(rows)


def test_calibrate_v2_uses_only_verified_series_and_is_pd():
    cal = calibrate_v2(_d4())
    assert set(FACTOR_SERIES_V2) <= set(cal.vol)
    assert cal.vol["capex"] == 0.0 and np.isnan(cal.vol["h2"])
    c = cal.corr.loc[list(FACTOR_SERIES_V2), list(FACTOR_SERIES_V2)].to_numpy()
    assert np.linalg.eigvalsh(c).min() > 0
    assert not np.allclose(c, np.eye(4))            # common factor -> non-identity
    assert abs(c[0, 2]) > 0.3                         # elec-coal share the common shock
    assert cal.meta["n_returns"]["elec"] > 0 and "elec|coal" in cal.meta["pairwise_overlap"]


def test_calibrate_v2_refuses_priors():
    d4 = _d4()
    d4 = d4[d4.series_id != "kau_krw"]
    with pytest.raises(RuntimeError, match="refuses priors"):
        calibrate_v2(d4)


def test_v2_factor_simulation_structural_h2_and_deterministic_capex():
    cal = calibrate_v2(_d4())
    years = np.arange(2027, 2051)
    sh = simulate_factors(cal, years, 4000, np.random.default_rng(3), "gbm", 10., "mean",
                          list(FACTOR_SERIES_V2), h2_elec_share=0.6)
    assert np.allclose(sh["capex"], 1.0) and np.allclose(sh["electrolyzer"], 1.0)
    # h2 shares electricity's innovations: log(h2) = 0.6 log(elec) up to the variance shift
    lh, le = np.log(sh["h2"][:, 5]), np.log(sh["elec"][:, 5])
    assert abs(np.corrcoef(lh, le)[0, 1] - 1.0) < 1e-9
    assert abs(np.polyfit(le, lh, 1)[0] - 0.6) < 1e-9
    for f in FACTOR_SERIES_V2:
        assert abs(sh[f].mean() - 1.0) < 0.05          # mean-normalised
    assert sh.metadata["factor_set"] == "v2" and sh.metadata["h2_elec_share"] == 0.6


class _Cfg(dict):
    def __getattr__(self, k):
        v = self[k]
        return _Cfg(v) if isinstance(v, dict) else v


def _cfg():
    return _Cfg(years={"start": 2027, "end": 2030}, discount_rate=0.0,
                contracts={"ppa_premium_pct": 0.08, "epc_premium_pct": 0.1, "ccfd_fee_pct": 0.0},
                carbon_auction_share={2025: 1.0, 2050: 1.0}, carbon_accounting_mode="gross_obligation_proxy")


def _profile(grid, re, ppa, ref=None):
    T = 4
    z = np.zeros(T)
    return PlanProfile(grid_mwh=np.full(T, grid), re_mwh=np.full(T, re), h2_kg=z, other_cost_k=z, capex_k=z,
                       capex_by_tech={}, capex_unc={}, emissions=z, ppa=ppa, epc=0, ccfd=0,
                       embedded_price_basis={}, profile_years=tuple(range(2027, 2031)),
                       hedge_reference_mwh=None if ref is None else np.full(T, ref))


def _px_shocks(n=2000):
    T = 4
    px = {"elec": np.full(T, 1e8), "re": np.full(T, 1e8), "h2": np.zeros(T), "co2": np.zeros(T),
          "coal": np.zeros(T), "gas": np.zeros(T)}
    rng = np.random.default_rng(0)
    e = np.exp(rng.standard_normal((n, T)) * 0.3)
    sh = {"elec": e, "h2": np.ones((n, T)), "capex": np.ones((n, T))}
    return px, sh


def test_incremental_hedge_basis_matches_paper_algebra():
    """§3.6: baseline buys 2, transition buys 8 (6 added). Fixing share h of the
    INCREMENT leaves exposure (6-6h)P_e; fixing h of the TOTAL (v1) leaves (6-8h)P_e."""
    cfg = _cfg()
    px, sh = _px_shocks()
    sp = {"subsidy": {}, "ccfd_strike": None}
    base = simulate_cost(_profile(2., 0., 0.0), px, sh, sp, cfg)
    v1_full = simulate_cost(_profile(0., 8., 1.0), px, sh, sp, cfg) - base
    v2_full = simulate_cost(_profile(0., 8., 1.0, ref=2.), px, sh, sp, cfg) - base
    assert np.std(v1_full) > 1e-3                     # v1: −2P_e exposure survives a 100% hedge
    assert np.std(v2_full) < 1e-9                     # v2: increment fully fixed -> no residual exposure
    v1_75 = simulate_cost(_profile(0., 8., 0.75), px, sh, sp, cfg) - base
    assert np.std(v1_75) < 1e-9                       # v1's zero-exposure share is 75% (paper §3.6)
    v2_50 = simulate_cost(_profile(0., 8., 0.5, ref=2.), px, sh, sp, cfg) - base
    v2_00 = simulate_cost(_profile(0., 8., 0.0, ref=2.), px, sh, sp, cfg) - base
    assert abs(np.std(v2_50) / np.std(v2_00) - 0.5) < 1e-9


def test_absolute_risk_credits_exposure_removal():
    """A plan that removes a stochastic cost (no carbon, no grid power) must show
    LOWER absolute ES than the baseline even though its incremental TCaR is large."""
    cfg = _cfg()
    px, sh = _px_shocks()
    sp = {"subsidy": {}, "ccfd_strike": None}
    base = simulate_cost(_profile(10., 0., 0.0), px, sh, sp, cfg)
    plan = simulate_cost(_profile(0., 0., 0.0), px, sh, sp, cfg) + 0.5 * base.mean()   # fixed cost, no exposure
    inc = plan - base
    s_inc, s_abs, s_base = loss_summary(inc), loss_summary(plan), loss_summary(base)
    assert s_inc["q_alpha"] - s_inc["p50"] > 0        # v1 axis: transition looks risky (tracking error)
    assert s_abs["es_alpha"] < s_base["es_alpha"]     # v2 axis: it removed the exposure


def test_frontier_flags_exclude_sampled_dominated():
    pts = pd.DataFrame({"mean": [1., 2., 0.5], "es": [5., 4., 4.5], "dominated": [False, False, True]})
    elig = pts[~pts.dominated]
    mask = pd.Series(False, index=pts.index)
    mask.loc[elig.index] = pareto_mask(elig["mean"], elig["es"])
    assert mask.tolist() == [True, True, False]


def test_es_subadditive_tcar_not(tmp_path=None):
    """L5: ES is coherent (Artzner et al. 1999), so ES(X+Y) <= ES(X)+ES(Y) — firm-level
    ES_abs can be summed as a portfolio UPPER BOUND. The quantile gap TCaR can violate
    it (Proposition 3), so summed TCaR bounds nothing. Checked on sample estimators."""
    rng = np.random.default_rng(7)
    n = 20000
    # two firms sharing a common factor plus own tails
    common = rng.standard_normal(n)
    x = np.exp(0.4 * common + 0.3 * rng.standard_normal(n))
    y = np.exp(0.4 * common + 0.3 * rng.standard_normal(n)) + 5 * (rng.uniform(size=n) < 0.06)
    es = lambda v: loss_summary(v)["es_alpha"]
    tcar = lambda v: loss_summary(v)["q_alpha"] - loss_summary(v)["p50"]
    assert es(x + y) <= es(x) + es(y) + 1e-9
    # a disjoint-tail construction where the quantile gap adds up wrongly
    a = np.where(rng.uniform(size=n) < 0.06, 100.0, 0.0)
    b = np.where(rng.uniform(size=n) < 0.06, 100.0, 0.0)
    assert tcar(a + b) > tcar(a) + tcar(b) - 1e-9   # 0 + 0 < 100 (Proposition 3)
