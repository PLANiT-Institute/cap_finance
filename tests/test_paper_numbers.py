"""페이퍼 §0 수치 대장이 out/ 실산출물과 일치하는가.

논문 원고에 손으로 적은 숫자는 파이프라인이 바뀌면 조용히 낡는다. 이 테스트는
`paper/working_paper.md` §0 표를 파싱해 out/에서 다시 계산한 값과 대조한다.
불일치는 "원고를 고쳐라"라는 뜻이고, 대장에 없는 key를 본문에서 인용하는 것은 금지다.

산출물이 없으면 skip (파이프라인 미실행 = 실패가 아님) — test_consistency.py와 같은 규약.

Run: .venv/bin/pytest tests/test_paper_numbers.py -q
"""

import json
import pathlib
import re
import sys

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cap import config as C  # noqa: E402
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

    # M8 §6-7 — 기술 일정 축 epsilon-constraint. 강제 일정이 정본 (P50, TCaR)에서
    # 살아남는 수가 규약(탄소 결정론/확률)에 따라 갈리는 것이 이 논문의 진술을 정한다.
    m8 = _out("m8", "tech_epsilon")
    got["m8_caps_total"] = float(len(m8))
    got["m8_new_schedules"] = float(m8.schedule_is_new.sum())
    got["m8_nondominated_headline"] = float(m8.nondominated_headline.sum())
    got["m8_nondominated_l2"] = float(m8.nondominated_l2.sum())
    got["m8_groups_nondominated_l2"] = float(
        m8.groupby(["company_id", "scenario"]).nondominated_l2.any().sum())

    # §4 데이터 절 (M3): 출처·등급·무결성은 원자료에서 다시 센다
    for r in _out("m3", "summary").itertuples():
        got[r.key] = float(r.value)

    # §4.6 데이터 절 (G2, D10): 증거 밴드와 그것이 F3에 준 영향
    for r in _out("g2", "summary").itertuples():
        got[r.key] = float(r.value)

    # §5 결과 절 (M4, D12): 경계 사다리·후회비용·빈 지원 축
    for r in _out("m4", "summary").itertuples():
        got[r.key] = float(r.value)

    # §6 강건성 절 (M5, D14): 흔든 축·묶음 행렬·벌칙 바닥 값매김
    for r in _out("m5", "summary").itertuples():
        got[r.key] = float(r.value)

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
    # 어긋나면 **어느 쪽이 틀렸는지**부터 말한다. D10 뒤 어긋난 쪽은 페이퍼가 아니라
    # `--sims`를 줄인 실행으로 덮인 out/이었는데, 메시지는 페이퍼를 지목하고 있었다.
    assert not bad, f"페이퍼 §0 대장이 out/과 어긋난다 (paper, out): {bad}\n{_provenance_hint()}"


def _provenance_hint() -> str:
    p = ROOT / "out" / "run_manifest.json"
    if not p.exists():
        return "out/run_manifest.json 없음 — out/이 정본 실행인지 알 수 없다. `python -m cap all` 먼저."
    m = json.loads(p.read_text())
    cfg = C.load()
    want = {"data_dir": str(cfg.data_dir), "n_sims": cfg.simulation["n_sims"],
            "n_sims_flex": cfg.simulation["n_sims_flex"],
            "frontier_points": cfg.milp["frontier_points"], "seed": cfg.seed}
    off = [f"{s}.{k}={m[s][k]}(≠{v})" for s in m for k, v in want.items() if m[s].get(k) != v]
    return ("out/이 정본 설정이 아니다 — " + ", ".join(off[:4]) + " · 페이퍼가 아니라 out/을 고쳐라"
            if off else "out/은 정본 설정 실행이다 — 대장(페이퍼) 쪽을 고쳐라")


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

    # 본문 §4 — 데이터 절의 세 표. 여기가 낡으면 출처 주장이 거짓말을 한다.
    assert f"| **계** | **{int(led['inv_rows'])}** | **18 → {int(led['inv_banded'])}** |" in body, \
        "§4.2 등급 표 합계가 §0 대장과 어긋난다"
    assert f"열 중 {int(led['top10_t3plus'])}개만 규약을 만족한다" in body, \
        "§4.3의 상위 10 등급 서술이 §0 대장과 어긋난다"
    for label, key in ((r"등록부(`source_register.csv`)", "inv_src_registered"),
                       ("표식 — 출처 아님", "inv_src_sentinel"),
                       ("EFF 이름공간", "inv_src_eff")):
        assert f"| {label} | {int(led[key])} |" in body, \
            f"§4.4 무결성 표의 '{label}' 행이 §0 대장과 어긋난다"


def test_run_manifest_records_the_settings_a_run_actually_used(tmp_path):
    """축소 실행이 자기 이름을 남기는가 — D11의 착오가 되풀이되지 않게 하는 최소 조건.

    D10 뒤 out/e2·e4는 `--sims`를 줄인 실행으로 덮였는데 산출물 어디에도 그 사실이
    없었다. 그래서 대장 불일치가 '원고가 낡았다'로 읽혔다. 기록은 단계별로 **병합**
    되어야 한다 — e1만 다시 돌렸다고 e2의 출처가 지워지면 같은 착오가 돌아온다.
    """
    from cap.__main__ import _stamp

    small = C.load(out_dir=str(tmp_path))
    small["simulation"] = dict(small["simulation"], n_sims=7)
    _stamp(small, "e2")
    _stamp(C.load(out_dir=str(tmp_path)), "e1")

    m = json.loads((tmp_path / "run_manifest.json").read_text())
    assert set(m) == {"e1", "e2"}, "단계 기록이 병합되지 않고 덮어써졌다"
    assert m["e2"]["n_sims"] == 7, "축소 실행이 기록되지 않았다"
    assert m["e1"]["n_sims"] == C.load().simulation["n_sims"], "정본 실행이 잘못 기록됐다"
