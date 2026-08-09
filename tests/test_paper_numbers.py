"""페이퍼 §0 수치 대장이 out/ 실산출물과 일치하는가.

논문 원고에 손으로 적은 숫자는 파이프라인이 바뀌면 조용히 낡는다. 이 테스트는
`paper/working_paper.md` §0 표를 파싱해 out/에서 다시 계산한 값과 대조한다.
불일치는 "원고를 고쳐라"라는 뜻이고, 대장에 없는 key를 본문에서 인용하는 것은 금지다.

산출물이 없으면 skip (파이프라인 미실행 = 실패가 아님) — test_consistency.py와 같은 규약.

Run: .venv/bin/pytest tests/test_paper_numbers.py -q
"""

import pathlib
import re

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "working_paper.md"
OUT = ROOT / "out"

SCEN, SUPP = "NZ15", "none"


def _out(stage: str, name: str) -> pd.DataFrame:
    p = OUT / stage / f"{name}.csv"
    if not p.exists():
        pytest.skip(f"{p.relative_to(ROOT)} 없음 — `python -m cap all` 먼저 실행")
    return pd.read_csv(p)


def _spearman(a, b) -> float:
    """순위상관. scipy가 환경에 없으므로 순위 변환 후 피어슨으로 낸다 (동점은 평균순위)."""
    return float(a.rank().corr(b.rank()))


def _ledger() -> dict[str, float]:
    """§0 표의 `| key | value | 출처 |` 행만 뽑는다."""
    rows = re.findall(r"^\|\s*([a-z0-9_]+)\s*\|\s*([-\d.]+)\s*\|", PAPER.read_text(), re.M)
    assert rows, "페이퍼 §0 수치 대장을 찾지 못했다"
    return {k: float(v) for k, v in rows}


def _computed() -> dict[str, float]:
    m = _out("e5", "metrics_company").query("scenario == @SCEN and support == @SUPP")
    m = m.set_index("company_id")
    gap = _out("e5", "gap").query("scenario == @SCEN and support == @SUPP").set_index("company_id")
    fp = _out("e5", "frontier_points")

    got: dict[str, float] = {}
    for co in m.index:
        got[f"m2_{co.lower()}"] = round(float(m.loc[co, "cost_per_tco2_thkrw"]), 1)
        got[f"tcar_{co.lower()}"] = round(float(m.loc[co, "tcar_bnkrw"]), 1)
    for co in gap.index:
        got[f"gap_cost_{co.lower()}"] = round(float(gap.loc[co, "gap_cost_bnkrw"]), 1)
        got[f"gap_risk_{co.lower()}"] = round(float(gap.loc[co, "gap_risk_bnkrw"]), 1)
    got["gap_companies"] = float(gap.index.nunique())

    # 위험 1원의 가격: 최소비용 → 최소위험 이동의 교환비
    fr = fp[(fp.scenario == SCEN) & (fp.support == SUPP) & fp.on_frontier]
    for co, d in fr.groupby("company_id"):
        a, b = d.loc[d.p50.idxmin()], d.loc[d.tcar.idxmin()]
        got[f"hedge_rate_{co.lower()}"] = round((a.tcar - b.tcar) / (b.p50 - a.p50), 2)

    # F3 불확실성 분해: ③ TCaR 중 파라미터가 만드는 몫 (추첨 폭 ±30%)
    u = _out("uncertainty", "decomposition")
    u30 = u[(u.scenario == SCEN) & (u.support == SUPP) & (u.width == 0.30)].set_index("company_id")
    for co in u30.index:
        got[f"tcar_param30_{co.lower()}"] = round(float(u30.loc[co, "tcar_param"]), 1)
        got[f"param_share30_{co.lower()}"] = round(float(u30.loc[co, "param_share_pct"]), 1)
        # L2/FC4: 탄소가격을 확률 축으로 옮겼을 때의 TCaR 증분 (폭과 무관 — 시드 평균)
        got[f"tcar_co2only_{co.lower()}"] = round(float(u30.loc[co, "tcar_co2_only"]), 1)
        got[f"co2_increment_{co.lower()}"] = round(float(u30.loc[co, "co2_increment"]), 1)

    # M2 §3.4 — E2 대리 목적함수가 E4 정본 순위를 얼마나 보존하는가.
    # 대리는 "후보를 나열하는 장치"일 뿐이라는 A-14를 숫자로 뒷받침한다. 여기서 상관이
    # 1에 가까워지면 대리를 그냥 믿어도 된다는 뜻이고, 그때는 본문 서술을 고쳐야 한다.
    s = _out("e4", "summary").query("support == @SUPP")
    pidx = _out("e2", "plan_index")[["plan_id", "risk_proxy"]]
    s = s.merge(pidx, on="plan_id")
    got["e2_plans_total"] = float(len(_out("e2", "plan_index")))
    scen = s[s.scenario == SCEN]
    for co, d in scen.groupby("company_id"):
        got[f"surrogate_rho_{co.lower()}"] = round(_spearman(d.e2_surrogate_cost, d.p50), 3)
        got[f"riskproxy_rho_{co.lower()}"] = round(_spearman(d.risk_proxy, d.tcar), 3)
    # 정본 기준으로 서로 다른 계획의 수 (중앙 경로 비용이 같으면 같은 계획)
    grp = s.groupby(["company_id", "scenario"])
    got["e2_plans_canonical"] = float(grp.central_cost.apply(lambda x: x.round(6).nunique()).sum())
    # 대리가 고른 최저비용 계획이 정본에서도 최저인 묶음 수
    got["surrogate_argmin_groups"] = float(grp.ngroups)
    got["surrogate_argmin_match"] = float(sum(
        d.loc[d.e2_surrogate_cost.idxmin(), "plan_id"] == d.loc[d.p50.idxmin(), "plan_id"]
        for _, d in grp))
    # 재정렬이 몬테카를로 탓이 아님을 보이는 대조군
    got["rho_central_p50_min"] = round(
        min(_spearman(d.central_cost, d.p50) for _, d in grp), 3)

    # §4 경계 퇴화: 경계 위 점들이 한 기술 일정만 쓰는 묶음 수
    per_group = fp[fp.on_frontier].groupby(
        ["company_id", "scenario", "support"]).base_plan_id.nunique()
    got["frontier_groups_total"] = float(len(per_group))
    got["frontier_single_schedule_groups"] = float((per_group == 1).sum())
    return got


def test_ledger_matches_outputs():
    ledger, got = _ledger(), _computed()
    missing = sorted(set(ledger) - set(got))
    assert not missing, f"대장에만 있고 out/에서 재계산되지 않는 key: {missing}"
    bad = {k: (v, got[k]) for k, v in ledger.items() if abs(v - got[k]) > max(0.05, abs(got[k]) * 5e-4)}
    assert not bad, f"페이퍼 §0 대장이 out/과 어긋난다 (paper, out): {bad}"


def test_body_quotes_only_ledger_keys():
    """§4의 서술 주장이 대장 값과 같은 사실을 말하는지 — 퇴화 묶음 수만 검사."""
    led = _ledger()
    body = PAPER.read_text()
    n, tot = int(led["frontier_single_schedule_groups"]), int(led["frontier_groups_total"])
    assert f"{tot}개 (기업×시나리오×지원) 묶음 중 **{n}개" in body, \
        "§4 본문의 경계 퇴화 서술이 §0 대장과 어긋난다"

    # 본문 §3.4 — 대리/정본 관계 서술. 여기가 낡으면 방법 절이 거짓말을 한다.
    m, g = int(led["surrogate_argmin_match"]), int(led["surrogate_argmin_groups"])
    assert f"일치 {m}/{g}" in body, "§3.4의 argmin 일치 서술이 §0 대장과 어긋난다"
    total, canon = int(led["e2_plans_total"]), int(led["e2_plans_canonical"])
    assert f"{total}개 계획 중 정본 평가에서 서로 다른 것은\n**{canon}개**" in body, \
        "§3.4의 후보 중복 서술이 §0 대장과 어긋난다"
