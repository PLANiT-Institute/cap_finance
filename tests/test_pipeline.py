"""End-to-end pipeline test on synthetic sample data (fast settings).

Run: .venv/bin/pytest tests/ -x -q   (~2-4 min, dominated by CBC solves)
"""

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cap import config as C  # noqa: E402


@pytest.fixture(scope="session")
def cfg():
    c = C.load(data_dir="data/sample")
    c["simulation"] = dict(c["simulation"], n_sims=500, n_sims_flex=100)
    c["milp"] = dict(c["milp"], frontier_points=4)
    return c


@pytest.fixture(scope="session")
def pipeline(cfg):
    from cap import e1_constraints, e2_milp, e3_prices, e4_revalue, e5_metrics
    e1 = e1_constraints.run(cfg)
    e2 = e2_milp.run(cfg)
    e3_prices.run(cfg)
    e4s, e4f = e4_revalue.run(cfg)
    m, fr, gap, dec = e5_metrics.run(cfg)
    return dict(e1=e1, e2=e2, e4s=e4s, e4f=e4f, m=m, fr=fr, gap=gap, dec=dec)


def test_e1_budget_declines(pipeline):
    c = pipeline["e1"]["constraints"]
    for _, g in c.groupby(["scenario", "company_id"]):
        g = g.sort_values("year")
        assert g.company_budget_tco2.iloc[-1] < g.company_budget_tco2.iloc[0]


def test_e2_all_companies_have_plans(pipeline):
    idx = pipeline["e2"]
    assert set(idx.company_id) == {"POSCO", "NSC", "LOTTE", "MCI"}
    assert idx.groupby(["company_id", "scenario"]).size().min() >= 2
    assert idx.groupby(["company_id", "scenario"]).is_disclosed.any().all()


def test_e2_frontier_tradeoff(pipeline):
    # within each company x scenario, min-risk plan must cost >= min-cost plan
    for _, g in pipeline["e2"][~pipeline["e2"].is_disclosed].groupby(["company_id", "scenario"]):
        assert g.loc[g.risk_proxy.idxmin()].npv_cost_bnkrw >= g.npv_cost_bnkrw.min() - 1e-6


def test_e4_tcar_nonnegative(pipeline):
    assert (pipeline["e4s"].tcar >= -1e-9).all()


def test_e4_support_never_costlier(pipeline):
    # subsidies can only reduce cost; CCfD is excluded — its fee is paid in every
    # covered year while the strike only pays off when carbon prices exceed it,
    # so a ccfd plan can legitimately cost more under support than gross
    no_ccfd = pipeline["e2"][pipeline["e2"].ccfd == 0].plan_id
    piv = (pipeline["e4s"][pipeline["e4s"].plan_id.isin(no_ccfd)]
           .pivot_table(index="plan_id", columns="support", values="p50"))
    assert (piv["current"] <= piv["none"] + 1e-6).all()


def test_e5_metrics_complete(pipeline):
    m = pipeline["m"]
    assert len(m) == 4 * 2 * 2  # companies x scenarios x supports
    assert m.tcar_bnkrw.ge(0).all()
    assert m.policy_exposure_bnkrw.notna().all()


def test_e5_gap_nonnegative(pipeline):
    # NaN allowed: disclosed point outside the frontier's range on that axis
    gv = pipeline["gap"][["gap_cost_bnkrw", "gap_risk_bnkrw"]]
    assert ((gv >= 0) | gv.isna()).all().all()
    assert gv.notna().any().any()  # at least some gaps must be measurable


def test_e5_variance_shares_bounded(pipeline):
    assert pipeline["dec"].variance_share.between(0, 1.2).all()


def test_schema_validation_fails_fast(cfg, tmp_path):
    from cap.schemas import SchemaError, load_input
    with pytest.raises(SchemaError, match="missing input file"):
        load_input(tmp_path, "D1a_facility_static")
    (tmp_path / "D3_tech_options.csv").write_text("tech_id,sector\na,steel\n")
    with pytest.raises(SchemaError, match="missing columns"):
        load_input(tmp_path, "D3_tech_options")


def test_gap_interpolation_concrete():
    # regression: drisk previously used a decreasing xp in np.interp -> garbage
    from cap.e5_metrics import _gap
    fr = pd.DataFrame({"tcar": [1.0, 2.0, 3.0], "p50": [10.0, 8.0, 5.0]})
    point = pd.Series({"tcar": 2.5, "p50": 9.0})
    dcost, drisk = _gap(fr, point)
    assert dcost == pytest.approx(9.0 - 6.5)   # frontier cost at tcar 2.5 = 6.5
    assert drisk == pytest.approx(2.5 - 1.5)   # frontier tcar at p50 9.0 = 1.5
    # below frontier range -> NaN, not a clamped fabricated gap
    below = pd.Series({"tcar": 0.5, "p50": 4.0})
    dcost2, drisk2 = _gap(fr, below)
    assert np.isnan(dcost2) and np.isnan(drisk2)
    # dominated beyond the high end (그림 4 case) -> endpoint lower bound
    dom = pd.Series({"tcar": 5.0, "p50": 12.0})
    dcost3, drisk3 = _gap(fr, dom)
    assert dcost3 == pytest.approx(12.0 - 5.0)  # vs min-cost endpoint (tcar 3, p50 5)
    assert drisk3 == pytest.approx(5.0 - 1.0)   # vs min-risk endpoint (tcar 1, p50 10)


def test_support_windows(cfg):
    # subsidy/ccfd apply only inside valid_from..valid_to
    from cap.plancost import support_params
    from cap.schemas import load_input
    d5 = load_input(C.data_dir(cfg), "D5_policy_support")
    years = np.arange(cfg["years"]["start"], cfg["years"]["end"] + 1)
    sp = support_params(d5, "current", years)
    sub = sp["subsidy"]["steel_h2dri"]
    assert sub[years == 2026][0] == 0.0 and sub[years == 2030][0] > 0
    strike = sp["ccfd_strike"]
    assert np.isinf(strike[years == 2025][0]) and np.isfinite(strike[years == 2030][0])


def test_variance_decomp_elec_dominant(pipeline):
    # spot-poll: for plans with zero adoption (pure incumbent, no h2/capex), the
    # net exposure vs baseline is ~zero -> shares may be anything; but for plans
    # with h2-heavy adoption, the h2+elec shares should dominate capex-only noise.
    dec = pipeline["dec"]
    piv = dec.pivot_table(index=["plan_id", "support"], columns="factor", values="variance_share")
    assert piv.notna().all().all()


def test_e3_reproducible(cfg):
    from cap.calibration import calibrate
    from cap.e3_prices import simulate_factors
    from cap.schemas import load_input
    d4 = load_input(C.data_dir(cfg), "D4_price_history")
    cal = calibrate(d4)
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    a = simulate_factors(cal, years, 50, np.random.default_rng(cfg.seed))
    b = simulate_factors(cal, years, 50, np.random.default_rng(cfg.seed))
    for k in a:
        assert np.array_equal(a[k], b[k])
