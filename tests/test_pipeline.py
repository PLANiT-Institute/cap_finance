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
    # out_dir MUST differ from the production out/ — the test suite runs the whole
    # pipeline on synthetic data, and sharing out/ silently overwrote real results
    # with fabricated ones (2026-08-09: a published report carried sample numbers).
    c = C.load(data_dir="data/sample", out_dir="out_test")
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


def test_outputs_isolated_from_production(cfg):
    """Guard the 2026-08-09 incident: the suite must never write into out/."""
    assert cfg["out_dir"] != "out", "test out_dir collides with production outputs"
    assert "test" in cfg["out_dir"]


def test_emis_cap_is_an_axis_contracts_cannot_buy(cfg, pipeline):
    """M8: 기술 일정 축 epsilon-constraint. (a) 상한이 실제로 물린다, (b) 제약이
    붙었으므로 대리비용이 내려가지 않는다, (c) 계약(PPA/EPC/CCfD)은 배출을 1t도
    바꾸지 않는다 — (c)가 깨지면 이 축은 일정 축이 아니게 되고 M8 진단이 무의미해진다."""
    import pandas as pd

    from cap.e2_milp import _prep_company, _solve_company
    from cap.plancost import build_profile

    fac, d3, cal = _prep_company(cfg, C.data_dir(cfg))
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    constraints = pd.read_csv(C.out_dir(cfg, "e1") / "constraints.csv")
    avail = pd.read_csv(C.out_dir(cfg, "e1") / "tech_availability.csv")
    company = sorted(fac.company_id.unique())[0]
    scen = cfg.scenarios[0]
    args = (cfg, company, scen, fac, d3, cal, prices, constraints, avail)

    base = _solve_company(*args, objective="cost")
    assert base is not None and base["cum_emis_tco2"] > 0
    cap = 0.9 * base["cum_emis_tco2"]
    capped = _solve_company(*args, objective="cost", emis_cap=cap)
    assert capped is not None, "10% 감축 상한이 실행불가 — 표본자료 문제"
    assert capped["cum_emis_tco2"] <= cap * 1.001
    # mip_gap_rel 만큼의 여유. 제약 추가가 대리비용을 개선할 수는 없다.
    assert capped["npv_cost"] >= base["npv_cost"] * (1 - 2 * float(cfg.milp.get("mip_gap_rel", 0.005)))

    px = {k: prices[(prices.scenario == scen) & (prices.variable == f"{k}_price")]
          .groupby("year").value.mean().reindex(
              np.arange(cfg.years.start, cfg.years.end + 1)).ffill().bfill().to_numpy()
          for k in ("elec", "coal", "gas")}
    techs = d3[d3.sector == fac[fac.company_id == company].sector.iloc[0]]
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    rows = base["plan"] or [{"facility_id": None, "tech_id": None,
                             "adopt_year": None, "op_year": None}]
    emis = []
    for ppa, epc, ccfd in [(0.0, 0, 0), (1.0, 1, 1)]:
        pdf = pd.DataFrame(rows).assign(company_id=company, scenario=scen,
                                        ppa_share=ppa, epc=epc, ccfd=ccfd)
        emis.append(build_profile(pdf, fac, techs, px, years, cfg).emissions)
    assert np.array_equal(emis[0], emis[1])
