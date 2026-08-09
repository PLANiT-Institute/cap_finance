"""H1 내부 일관성 — 회계 항등식·질량/배출 균형·단위 왕복을 실산출물(out/)에 대해 검사.

test_pipeline.py는 합성 데이터로 "돌아가는가"를 본다. 이 파일은 실행된 실데이터
결과가 **스스로 모순되지 않는가**를 본다. 심사자가 먼저 두드리는 곳이라 산출물이
있을 때만 돌고, 없으면 skip (파이프라인 미실행 = 실패가 아님).

Run: .venv/bin/pytest tests/test_consistency.py -q
"""

import json
import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cap import config as C  # noqa: E402
from cap.plancost import auction_share  # noqa: E402
from cap.schemas import load_input  # noqa: E402

OUT = ROOT / "out"


def _read(stage: str, name: str) -> pd.DataFrame:
    p = OUT / stage / f"{name}.csv"
    if not p.exists():
        pytest.skip(f"{p.relative_to(ROOT)} 없음 — `python -m cap all` 먼저 실행")
    return pd.read_csv(p)


@pytest.fixture(scope="module")
def cfg():
    return C.load()


@pytest.fixture(scope="module")
def ddir(cfg):
    return C.data_dir(cfg)


# ---------------------------------------------------------------- 회계 항등식

def test_resource_cost_is_total_minus_carbon():
    """② 자원비용 = 총비용 − 탄소지출 델타. 지표 정의가 산출물에서 성립하는가."""
    m = _read("e5", "metrics_company")
    resid = m.p50_incl_carbon_bnkrw - m.carbon_delta_bnkrw - m.p50_bnkrw
    assert np.abs(resid).max() < 1e-6, f"자원비용 항등식 위반 최대 {np.abs(resid).max()}"


def test_tcar_is_p90_minus_p50():
    fr = _read("e5", "frontier_points")
    assert np.abs(fr.p90 - fr.p50 - fr.tcar).max() < 1e-6


def test_variance_shares_sum_to_one():
    """분산 분해는 요인별 몫이므로 계획마다 합이 1 부근.

    정확히 1이 아닌 이유: 요인별 몫을 각 요인만 흔든 부분분산으로 잡기 때문에
    교차항이 잔차로 남는다. 허용치 3%는 "분해가 성립한다"를 확인하는 선이고,
    이를 넘으면 요인 정의나 상관 처리가 깨진 것이다.
    """
    d = _read("e5", "variance_decomp")
    s = d.groupby(["plan_id", "company_id", "scenario", "support"]).variance_share.sum()
    assert np.abs(s - 1).max() < 0.03, f"분산 몫 합 최대 이탈 {np.abs(s - 1).max():.4f}"


# ---------------------------------------------------------------- 배출·질량 균형

def test_baseline_emissions_reproduce_facility_data(ddir):
    """무전환 기준선 배출 = Σ(시설 생산 × 실적 배출원단위). 원자료로 왕복 검증."""
    ep = _read("e5", "emissions_pathway")
    d1b = load_input(ddir, "D1b_facility_panel")
    d1a = load_input(ddir, "D1a_facility_static")

    recent = d1b.sort_values("year").groupby("facility_id").tail(1)
    recent = recent.merge(d1a[["facility_id", "company_id"]], on="facility_id")
    expect = recent.groupby("company_id").emissions_s1.sum()

    base = ep[(ep.plan == "baseline") & (ep.year == ep.year.min())]
    got = base.groupby("company_id").emissions_tco2.mean()   # scenario-invariant

    for cid in expect.index.intersection(got.index):
        rel = abs(got[cid] - expect[cid]) / expect[cid]
        assert rel < 0.02, f"{cid} 기준선 배출 {got[cid]:,.0f} vs 실적 {expect[cid]:,.0f} ({rel:.1%})"


def test_transition_never_raises_emissions():
    """비용최소 계획은 어느 해에도 무전환 기준선보다 많이 배출하지 않는다."""
    ep = _read("e5", "emissions_pathway")
    w = ep.pivot_table(index=["company_id", "scenario", "year"], columns="plan",
                       values="emissions_tco2")
    if "cost_min" not in w or "baseline" not in w:
        pytest.skip("cost_min/baseline 경로 없음")
    bad = w[w.cost_min > w.baseline * 1.0001]
    assert bad.empty, f"전환이 배출을 늘린 지점 {len(bad)}건\n{bad.head()}"


# ---------------------------------------------------------------- 단위·규모 왕복

def test_capex_peak_within_total_and_horizon(cfg):
    """피크연도 지출은 총액을 넘을 수 없고, 피크 연도는 모형 지평 안에 있다."""
    a = _read("e5", "affordability")
    assert (a.capex_peak_bnkrw <= a.capex_total_bnkrw + 1e-6).all()
    yrs = a.capex_peak_year.dropna()
    assert yrs.between(cfg["years"]["start"], cfg["years"]["end"]).all()


def test_capex_spreads_over_build_years(ddir, cfg):
    """공사기간 n년 기술 하나를 채택한 계획의 CAPEX는 n개 연도에 균등 분산된다.

    회귀 방지(직접): 어떤 계획이 최적이 됐는지에 의존하지 않도록 프로파일 생성기를
    합성 계획 하나로 직접 부른다. 기업 결과로 재는 방식은 '공사기간 1년 기술 한 대만
    채택한 계획'에서 피크=총액이 정상이라 거짓 실패를 낸다.
    """
    import numpy as np_

    from cap.e2_milp import _prep_company
    from cap.plancost import build_profile

    fac, d3, _ = _prep_company(cfg, ddir)
    multi = d3[d3.build_years.fillna(1) >= 2]
    if multi.empty:
        pytest.skip("공사기간 2년 이상 기술 없음")

    pick = next(((t, f) for t in multi.itertuples()
                 for f in [fac[(fac.sector == t.sector) & (fac.unit_type == t.applies_to_unit)]]
                 if not f.empty), None)
    if pick is None:
        pytest.skip("공사기간 2년 이상 기술 중 적용 가능한 시설이 있는 것이 없음")
    tk, cands = pick
    fid = cands.index[0]
    company = cands.company_id.iloc[0]
    years = np_.arange(cfg["years"]["start"], cfg["years"]["end"] + 1)
    ta = int(max(years[0] + 1, tk.avail_year))
    nb = int(tk.build_years)

    plan = pd.DataFrame([{"facility_id": fid, "tech_id": tk.tech_id, "adopt_year": ta,
                          "op_year": ta + nb, "plan_id": "TEST", "company_id": company,
                          "scenario": cfg["scenarios"][0], "ppa_share": 0.0, "epc": 0, "ccfd": 0}])
    px = {k: np_.full(len(years), v) for k, v in
          dict(elec=120000.0, re=130000.0, coal=200000.0, gas=900000.0,
               co2=50000.0, h2=3500.0).items()}
    prof = build_profile(plan, fac[fac.company_id == company], d3, px, years, cfg)
    spend = prof.capex_k[prof.capex_k > 0]
    assert len(spend) >= nb, (
        f"{tk.tech_id}(공사 {nb}년) CAPEX가 {len(spend)}개 연도에만 계상 — 일시 계상 회귀")
    i = int(ta - years[0])
    build = prof.capex_k[i:i + nb]
    assert np_.allclose(build, build.mean(), rtol=0.02), f"공사기간 분산이 균등하지 않음: {build}"


def test_affordability_ratios_reproduce():
    """비율은 구성요소에서 재계산 가능해야 한다 (표에 든 숫자의 추적성)."""
    a = _read("e5", "affordability")
    g = a[a.ebitda_ref_bnkrw > 0]
    assert not g.empty, "EBITDA 양수 기업이 하나도 없음 — D6 로딩 확인"
    assert np.abs(g.capex_peak_to_ebitda - g.capex_peak_bnkrw / g.ebitda_ref_bnkrw).max() < 1e-6
    assert np.abs(g.capex_total_to_ebitda - g.capex_total_bnkrw / g.ebitda_ref_bnkrw).max() < 1e-6
    neg = a[a.ebitda_ref_bnkrw <= 0]
    assert neg.capex_peak_to_ebitda.isna().all(), "손실 기업에 비율이 계산됨 — 의미 없는 수치"


def test_central_price_paths_are_complete_and_finite():
    """중앙 가격 경로에 NaN이 없고 모든 모형 연도를 덮는가.

    회귀 방지: D2b의 빈 앵커 하나가 보간을 통해 경로 전체를 NaN으로 만들었고,
    E2는 그 경로를 거부하고 폐기된 전해조 구조식으로 조용히 되돌아갔다. 설계
    변경이 빈 셀 하나로 무효화되는 경로를 막는다.
    """
    p = _read("e1", "price_paths_central")
    assert p.value.notna().all(), \
        f"NaN 가격 경로: {p[p.value.isna()][['scenario', 'region', 'variable']].drop_duplicates()}"
    cfg = C.load()
    need = set(range(cfg["years"]["start"], cfg["years"]["end"] + 1))
    for key, g in p.groupby(["scenario", "region", "variable"]):
        assert need <= set(g.year), f"{key}: 누락 연도 {sorted(need - set(g.year))[:5]}"


def test_hydrogen_priced_from_data_not_structural_fallback():
    """수소는 외부 조달 상품(D2b h2_price)이다 — 구조식 대체가 발동하지 않았는가."""
    p = _read("e1", "price_paths_central")
    h2 = p[p.variable == "h2_price"]
    assert not h2.empty, "h2_price 경로 없음 — E2가 구조식으로 후퇴한다"
    for key, g in h2.groupby(["scenario", "region"]):
        assert (g.value > 0).all(), f"{key}: 비양수 수소가격"


# ---------------------------------------------------------------- 정책 입력 정합

def test_auction_share_follows_confirmed_allocation_plan(cfg, ddir):
    """확정 할당계획(K-ETS 4기 발전외 15%, 2026–2030)이 config 추정 램프를 이긴다."""
    d5 = load_input(ddir, "D5_policy_support")
    rows = d5[d5.instrument == "auction_share"]
    if rows.empty:
        pytest.skip("D5에 발전외 유상할당 행 없음")
    years = np.arange(cfg["years"]["start"], cfg["years"]["end"] + 1)
    share = auction_share(years, cfg)
    for r in rows.itertuples():
        m = (years >= r.valid_from) & (years <= r.valid_to)
        assert np.allclose(share[m], r.value / 100.0), (
            f"{int(r.valid_from)}–{int(r.valid_to)} 유상할당 {share[m]} != 확정 {r.value / 100.0}")


def test_power_sector_allocation_not_applied(ddir):
    """발전부문 50% 행이 철강·석화에 새어들지 않는다 (구분 소실 회귀 방지)."""
    d5 = load_input(ddir, "D5_policy_support")
    assert "auction_share_power" in set(d5.instrument), \
        "발전부문 행이 분류되지 않음 — prepare_raw._instrument 확인"
    assert d5[d5.instrument == "auction_share"].value.max() <= 20, \
        "발전외 유상할당에 발전부문 값(50%)이 섞임"


# ---------------------------------------------------------------- 경계 정의

def test_frontier_points_are_pareto_nondominated():
    """on_frontier 표시된 점은 (p50, tcar) 평면에서 지배당하지 않는다."""
    fr = _read("e5", "frontier_points")
    for (cid, scen, supp), g in fr.groupby(["company_id", "scenario", "support"]):
        on = g[g.on_frontier]
        pool = g[~g.is_disclosed & g.budget_ok]
        for p in on.itertuples():
            dominated = pool[(pool.p50 <= p.p50 - 1e-9) & (pool.tcar <= p.tcar - 1e-9)]
            assert dominated.empty, f"{cid} {scen} {supp}: {p.plan_id}이 지배당함"


# ---------------------------------------------------------------- 산출물 격리

def test_scenario_bundles_never_write_into_shared_out():
    """시나리오 묶음 디렉터리의 링크가 공유 out/을 가리킨 채 남아 있지 않은가.

    회귀 방지: `<bundle>/e2 -> out/e2` 링크가 살아 있는 상태로 `--replan`을 걸면 E2가
    링크를 따라가 **실산출물을 덮어쓴다**. 실제로 out/e2/plans가 그렇게 파괴됐다.
    묶음이 직접 쓰는 단계(e2 replan 시)는 링크가 아니라 실디렉터리여야 한다.
    """
    root = ROOT / "out" / "scenarios"
    if not root.exists():
        pytest.skip("시나리오 산출물 없음")
    bad = []
    for b in sorted(p for p in root.iterdir() if p.is_dir()):
        for stage in ("e3", "e4", "e5"):          # 묶음이 항상 직접 쓰는 단계
            t = b / stage
            if t.is_symlink():
                bad.append(str(t.relative_to(ROOT)))
    assert not bad, f"묶음이 직접 쓰는 단계가 공유 out/을 링크한다: {bad}"


def test_production_plan_index_matches_plan_files():
    """plan_index.csv의 모든 계획 파일이 실제로 있는가 — 산출물 정합의 최소선."""
    idx = _read("e2", "plan_index")
    missing = [p for p in idx.plan_id
               if not (OUT / "e2" / "plans" / f"plan_{p}.csv").exists()]
    assert not missing, (f"plan_index에 있으나 파일이 없는 계획 {len(missing)}개 "
                         f"(예: {missing[:3]}) — out/e2가 다른 실행에 덮어쓰였을 수 있다")


def test_canonical_run_is_reproducible_not_load_dependent():
    """정본 out/은 **같은 커밋·같은 시드면 같은 수를 낸다**고 말할 수 있어야 한다.

    D11에서 같은 커밋·같은 시드의 두 실행이 정본 중복제거 계획 41 vs 42,
    surrogate_rho_nsc -0.105 vs -0.400을 냈다. 원인은 mip_gap_rel 2% 안의 **동률
    최적해 중 어느 것을 반환하는가**가 CBC 스레드 경합에 달려 있었던 것이다. 병렬은
    수치를 틀리게 하지 않는다 — 재현 불가능하게 만든다. 페이퍼 §0 대장이 기계 부하에
    따라 흔들리면 대장의 검증은 의미가 없다. 그래서 재현성은 성능 설정이 아니라 불변식이다.
    """
    cfg = C.load()
    assert int(cfg.milp["solver_threads"]) == 1, (
        "milp.solver_threads != 1 — CBC 병렬 탐색은 동률 최적해 선택을 실행마다 바꾼다. "
        "속도가 필요하면 정본이 아닌 실행(--sims 축소 등)에서만 올려라")
    p = OUT / "run_manifest.json"
    if not p.exists():
        pytest.skip("파이프라인 미실행")
    m = json.loads(p.read_text())
    off = {s: v.get("solver_threads") for s, v in m.items() if v.get("solver_threads") != 1}
    assert not off, f"out/이 병렬 solver로 만들어진 단계가 있다: {off} — `python -m cap all` 재실행"
