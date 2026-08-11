"""H4 두 모형 교차대조 — 같은 기업을 독립 구현 둘이 얼마나 다르게 답하는가.

FIN(시설 MILP·계약 격자·몬테카를로)과 EFF(블록 단위·증거 레지스트리·강건 선별)는
같은 회사·같은 공시자료를 쓰지만 구조가 다르다. 차이를 재는 것이 목적이 아니라
**차이를 구조 요인별로 설명할 수 있는가**가 목적이다. 설명되지 않는 차이가 남으면
둘 중 하나에 결함이 있다.

대조 축은 넷: 입력(생산·배출) / 자본 규모·시점 / 감축 단가 / 꼬리위험.
시나리오 매핑은 `data/crosswalk_scenarios.csv`, 시설 매핑은 `crosswalk_facilities.csv`.

    .venv/bin/python scripts/cross_model_check.py
산출: docs/cross_model_check.md  (양 저장소 동일 사본 — AUTOPILOT §3)
"""

from __future__ import annotations

import pathlib
import shutil
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cap import config as C  # noqa: E402
from cap.schemas import load_input  # noqa: E402

EFF = pathlib.Path.home() / "Documents" / "cap-efficient"
DOCS = ROOT / "docs"
PAIR = {"POSCO": "POSCO_KR", "NSC": "NIPPON_STEEL_JP"}   # 양쪽에 모두 있는 기업
CAND = "outputs/candidate_scenario_metrics.csv"          # EFF 후보 지표 (트리 둘 다에 존재)


def pct(a, b):
    return float("nan") if not b else 100 * (a - b) / abs(b)


def eff_file(rel: str):
    """EFF는 별도 저장소(`~/Documents/cap-efficient`)와 이 저장소의 사본 둘 다로 존재한다.

    **커밋된 사본이 정본이다.** F22까지는 순서가 반대여서 이 문서의 감축단가 표가
    저장소 밖 파일에서 나오고 있었고, 두 사본은 실제로 어긋나 있었다 — 같은 필터에서
    NSC 실행가능 후보 상한이 152.3(사내) 대 184.6(사외)이라 FIN의 156이 한쪽에서는
    대역 안, 다른 쪽에서는 대역 밖이 된다. 재현 가능성이 판정을 바꾸는 자리다.
    """
    for base in (ROOT / "cap-efficient", EFF):
        p = base / rel
        if p.exists():
            return p
    return None


def feasible(e):
    """FIN의 선택 규칙과 같게 — 전 제약 실행가능한 후보만."""
    return e[(e.carbon_budget_feasible) & (e.scenario_feasible)
             & (e.physical_constraints_feasible) & (e.resource_constraints_feasible)]


def cost_band(path):
    """한 EFF 트리의 실행가능 후보 감축단가 대역 (company_id × min/max)."""
    x = pd.read_csv(path)
    x = x[x.scenario_id == "ACCELERATED_15C"]
    y = feasible(x)
    return (y if not y.empty else x).groupby(
        "company_id").gross_cost_p50_kkrw_per_tco2.agg(["min", "max"])


def eff_divergence(rel: str):
    """같은 EFF 파일이 두 트리에서 다르면 (정본경로, 사외경로)를, 같거나 없으면 None."""
    a, b = ROOT / "cap-efficient" / rel, EFF / rel
    if a.exists() and b.exists() and a.read_bytes() != b.read_bytes():
        return a, b
    return None


def process_rows():
    """확률과정·변동성·상관 — 두 모형이 꼬리위험을 서로 다른 난수 세계에서 잰다.

    F20: §3의 '단위가 달라 TCaR 수준 비교 불가'는 분모 이야기이고, 분모를 맞춰도 남는
    교란이 하나 더 있다. FIN은 GBM, EFF는 OU다. FIN 자신의 측정(`docs/process_alternative.md`)
    으로 과정 선택만으로 TCaR이 41~48% 움직이므로, 이 칸은 §3의 각주가 아니라 별도 요인이다.
    """
    import json

    cal = pd.read_csv(ROOT / "out" / "e3" / "calibration_report.csv").set_index("param").value
    cfg = C.load()
    p = eff_file("data/price_process.json")
    if p is None:
        return None
    e = json.loads(p.read_text(encoding="utf-8"))
    kappa, vol = e.get("mean_reversion", {}), e.get("annual_volatility", {})

    def hl(k):
        import math
        return f"반감기 {math.log(2) / kappa[k]:.1f}년 (κ={kappa[k]})" if kappa.get(k) else "없음"

    rows = [
        ["확률과정", f"`{cfg['price_process']}` — 평균회귀 없음",
         f"OU — 전력 {hl('electricity')}"],
        ["전력 연 σ", f"{cal['vol_elec']:.3f} (D4 3계열 추정)",
         f"{vol.get('electricity', float('nan')):.2f} (`{e.get('data_status', '?')}`)"],
        ["수소 연 σ", f"{cal['vol_h2']:.3f} (사전값 — D4 미달, A-17)",
         f"{vol.get('hydrogen_input', float('nan')):.2f} · {hl('hydrogen_input')}"],
        ["자본비 연 σ", f"{cal['vol_capex']:.3f} (사전값 — D4 미달, A-17)",
         f"{vol.get('construction_capex', float('nan')):.2f} · {hl('construction_capex')}"],
        ["요인 상관", "단위행렬 (추정 부재)",
         " / ".join(f"{x:.2f}" for x in (e["correlation"][0][1], e["correlation"][0][2],
                                         e["correlation"][1][2]))],
    ]
    return rows


def main() -> int:
    m = pd.read_csv(ROOT / "out" / "e5" / "metrics_company.csv").query(
        "scenario=='NZ15' and support=='none'").set_index("company_id")
    ep = pd.read_csv(ROOT / "out" / "e5" / "emissions_pathway.csv").query(
        "scenario=='NZ15' and plan=='baseline'")
    d1b = load_input(C.data_dir(C.load()), "D1b_facility_panel")
    d1a = load_input(C.data_dir(C.load()), "D1a_facility_static")
    fac = d1b.merge(d1a[["facility_id", "company_id"]], on="facility_id")
    latest = fac[fac.year == fac.year.max()].groupby("company_id").agg(
        prod_mt=("production", lambda s: s.sum() / 1e6),
        s1_mt=("emissions_s1", lambda s: s.sum() / 1e6),
        s2_mt=("emissions_s2", lambda s: s.sum() / 1e6))

    ep_path = eff_file(CAND)
    if ep_path is None:
        raise SystemExit(f"EFF 산출물 없음: {CAND}")
    e = pd.read_csv(ep_path)
    e = e[e.scenario_id == "ACCELERATED_15C"]
    # FIN의 '비용최소 계획'은 예산 실행가능 집합 안에서 고른 것이다. EFF에서도 같은 조건을
    # 걸지 않으면 실행 불가능한 이상치 후보를 집어 대조가 무의미해진다(첫 실행에서 실증:
    # 필터 없이 최소값을 잡자 POSCO 감축단가가 −5.7로 나왔다).
    feas = feasible(e)
    if feas.empty:
        feas = e
        FEAS_NOTE = "**주의**: EFF 후보 중 전 제약 실행가능한 것이 없어 전체에서 골랐다."
    else:
        FEAS_NOTE = (f"EFF 후보 {len(e)}개 중 예산·시나리오·물리·자원 제약을 모두 만족하는 "
                     f"{len(feas)}개로 좁힌 뒤 감축단가 최소를 골랐다 — FIN의 선택 규칙과 같게.")
    spread = feas.groupby("company_id").gross_cost_p50_kkrw_per_tco2.agg(["min", "median", "max"])
    e = feas.sort_values("gross_cost_p50_kkrw_per_tco2").groupby("company_id").head(1).set_index("company_id")

    L = ["# H4 두 모형 교차대조 (FIN ↔ EFF)", "",
         "> `scripts/cross_model_check.py` 자동 생성. 양 저장소 동일 사본(AUTOPILOT §3).", "",
         "**대조 대상**: FIN `NZ15`·지원없음의 비용최소 계획 ↔ EFF `ACCELERATED_15C`의 "
         "감축단가 최소 후보. 시나리오 매핑은 `data/crosswalk_scenarios.csv` — FIN 1.5℃ "
         "정합과 EFF 내부 1.5℃ 스트레스는 **정의가 다르다**(EFF는 GCAM 정합을 주장하지 "
         "않는다). 따라서 아래 차이에는 시나리오 정의 차이가 섞여 있고, 그 몫은 분리되지 "
         "않는다.", ""]

    rows = []
    for fin, eff in PAIR.items():
        if fin not in m.index or eff not in e.index:
            continue
        f_, g_ = m.loc[fin], e.loc[eff]
        base = latest.loc[fin]
        rows.append(dict(
            company=fin,
            fin_prod=base.prod_mt, eff_prod=g_.reported_production_mt,
            fin_s1=base.s1_mt, fin_s12=base.s1_mt + base.s2_mt,
            eff_s12=g_.reported_scope12_emissions_mtco2,
            fin_capex=f_.capex_total_bnkrw, eff_capex=g_.aligned_capex_bn_krw,
            fin_peak=f_.capex_peak_year, eff_peak=g_.peak_capex_year,
            fin_lcoa=f_.cost_per_tco2_thkrw, eff_lcoa=g_.gross_cost_p50_kkrw_per_tco2,
            eff_lcoa_net=g_.expected_cost_p50_kkrw_per_tco2,
            eff_lo=spread.loc[eff, "min"], eff_hi=spread.loc[eff, "max"],
            fin_tcar_bn=f_.tcar_bnkrw, eff_tcar_kkrw=g_.tcar_kkrw_per_tco2,
        ))
    df = pd.DataFrame(rows)
    if df.empty:
        raise SystemExit("대조 가능한 기업이 없다 — PAIR 매핑 확인")

    L += ["## 1. 입력 정합 — 같은 회사를 같은 크기로 보고 있는가", "",
          "| 기업 | 생산 (Mt) FIN / EFF | 차이 | 배출 (MtCO₂) FIN S1 / FIN S1+2 / EFF S1+2 | S1+2 차이 |",
          "|---|---|---|---|---|"]
    for r in df.itertuples():
        L.append(f"| {r.company} | {r.fin_prod:.1f} / {r.eff_prod:.1f} | "
                 f"**{pct(r.fin_prod, r.eff_prod):+.1f}%** | "
                 f"{r.fin_s1:.1f} / {r.fin_s12:.1f} / {r.eff_s12:.1f} | "
                 f"**{pct(r.fin_s12, r.eff_s12):+.1f}%** |")
    L += ["", "**구조 요인.** FIN의 지표는 **Scope 1만** 쓰고(A-21) EFF는 **Scope 1+2**를 쓴다. "
          "위 표는 그 경계 차이를 분리해 보이기 위해 FIN의 S1+2도 함께 적었다 — 보존만 하고 "
          "지표에는 넣지 않는 값이다. 생산량 차이는 대상 설비 집합 차이(FIN 시설 단위 ↔ "
          "EFF 블록 단위, `crosswalk_facilities.csv`)에서 온다.", ""]

    L += ["## 2. 자본 규모와 시점", "",
          "| 기업 | 총 CAPEX (십억원) FIN / EFF | 차이 | 피크 연도 FIN / EFF |",
          "|---|---|---|---|"]
    for r in df.itertuples():
        L.append(f"| {r.company} | {r.fin_capex:,.0f} / {r.eff_capex:,.0f} | "
                 f"**{pct(r.fin_capex, r.eff_capex):+.1f}%** | "
                 f"{int(r.fin_peak)} / {int(r.eff_peak)} |")
    L += ["", "**구조 요인.** (a) FIN은 BF→EAF 전면 전환을 허용하지 않고 수소환원·리트로핏만 "
          "쓴다(A-10). EFF의 후보에는 `SCRAP_EAF`·`EAF_RENEWABLE`이 들어간다 — 기술 집합 자체가 "
          "다르다. (b) FIN의 투자 시점은 재투자 창과 좌초비용이 내생적으로 정하고, EFF는 "
          "공시 캘린더에서 후보를 생성한다. (c) FIN CAPEX는 공사기간에 분산(A-18), EFF는 "
          "정렬 기준이 다르다.", ""]

    L += ["## 3. 감축 단가와 꼬리위험", "", FEAS_NOTE, "",
          "| 기업 | FIN ② (자원비용) | EFF gross | EFF net(탄소가치 차감) | EFF 실행가능 후보 범위 | FIN TCaR (십억원) | EFF TCaR (천원/tCO₂) |",
          "|---|---|---|---|---|---|---|"]
    for r in df.itertuples():
        L.append(f"| {r.company} | {r.fin_lcoa:,.0f} | {r.eff_lcoa:,.1f} | {r.eff_lcoa_net:,.1f} | "
                 f"{r.eff_lo:,.1f} ~ {r.eff_hi:,.1f} | {r.fin_tcar_bn:,.0f} | {r.eff_tcar_kkrw:,.1f} |")
    inside = [r.company for r in df.itertuples() if r.eff_lo <= r.fin_lcoa <= r.eff_hi]
    if inside:
        L += ["", f"**FIN의 값이 EFF의 실행가능 후보 분포 안에 있다** ({', '.join(inside)}). "
              "즉 두 모형은 서로 다른 '최적'을 고르지만, FIN이 고른 계획의 단가는 EFF가 "
              "실행가능하다고 본 계획들이 만드는 범위 안에 든다. 수준이 어긋나는 것이 아니라 "
              "**선택 규칙이 다른 것**이다 — FIN은 예산 제약 하 비용최소, EFF는 강건성 선별.", ""]
    L += ["", "**단, 이 대역은 넓고 한쪽으로만 열려 있다.** " + " · ".join(
        f"{r.company} {r.eff_hi / r.eff_lo:.1f}배 폭, FIN이 EFF 채택안의 "
        f"{r.fin_lcoa / r.eff_lcoa:.1f}배, 대역 안 위치 "
        f"{100 * (r.fin_lcoa - r.eff_lo) / (r.eff_hi - r.eff_lo):.0f}%"
        for r in df.itertuples()) + ". 대역의 **하단은 EFF 자신이 고른 값**이므로("
        "선택 규칙이 gross 최소) FIN은 정의상 하단 아래로 내려갈 수 없다 — 이 검사는 "
        "위쪽으로만 실패할 수 있다. 즉 '수준이 일치한다'가 아니라 "
        "'**EFF가 실행가능하다고 본 것 중 비싼 쪽에 FIN이 있다**'가 이 표가 말하는 전부다.", ""]

    div = eff_divergence(CAND)
    if div is not None:
        alt = cost_band(div[1])
        flips = []
        for r in df.itertuples():
            eid = PAIR[r.company]
            if eid not in alt.index:
                continue
            was = alt.loc[eid, "min"] <= r.fin_lcoa <= alt.loc[eid, "max"]
            now = r.eff_lo <= r.fin_lcoa <= r.eff_hi
            flips.append(f"{r.company} {alt.loc[eid, 'min']:,.1f} ~ {alt.loc[eid, 'max']:,.1f} "
                         f"({'안' if was else '**밖**'})")
            if was != now:
                flips[-1] += " ← **판정이 뒤집힌다**"
        L += ["", "**이 표가 어느 트리에서 나왔는가.** EFF는 두 벌로 존재한다 — 이 저장소에 "
              f"커밋된 `{CAND}`와 저장소 밖 `~/Documents/cap-efficient/{CAND}`. **위 표는 "
              "커밋된 사본에서 나온다**: 저장소 밖 파일에서 나온 수치는 이 저장소만으로 "
              "재현되지 않는다. 두 사본은 실제로 어긋나 있고, 같은 필터를 저장소 밖 사본에 "
              "걸면 대역이 " + " · ".join(flips) + "가 된다. F20까지 이 스크립트는 저장소 밖 "
              "사본을 읽고 있었다.", ""]

    L += ["", "**구조 요인 — 이 차이가 가장 크고 가장 설명이 필요하다.**", "",
          "1. **분모가 다르다.** FIN은 할인된 감축량(tCO₂)으로 나누고 EFF는 공통 회피배출 "
          "(`common_avoided_emissions`)로 나눈다. EFF 분모가 Scope 1+2 기반이라 더 크고, "
          "그만큼 단가가 낮게 나온다.",
          "2. **탄소비용 처리가 다르다.** FIN ②는 **자원비용 기준**으로 탄소지출 델타를 "
          "빼낸다(A-19). EFF의 `expected_cost_p50`은 그 처리를 하지 않는다 — EFF에는 "
          "`net_economic_cost`·`gross_cost` 등 별도 계열이 따로 있다.",
          "3. **기술 집합이 다르다**(위 §2-a). 스크랩 EAF가 허용되면 단가가 크게 내려간다.",
          "4. **TCaR 단위가 다르다.** FIN은 금액(P90−P50, 십억원), EFF는 단가 기준"
          "(천원/tCO₂). 직접 비교하려면 FIN TCaR을 같은 분모로 나눠야 하는데, 분모 정의가 "
          "1번 때문에 다르므로 **현재 상태에서 TCaR은 수준 비교가 불가능하다** — 순위·부호만 "
          "비교 가능하다.",
          "5. **확률과정이 다르다 — 분모를 맞춰도 남는 교란.** 4번은 단위 이야기이고 이것은 "
          "난수 세계 이야기다. FIN은 GBM(평균회귀 없음), EFF는 OU다. FIN 자신의 측정으로 "
          "**과정 선택만으로 TCaR이 41~48% 움직인다**(`docs/process_alternative.md`) — 즉 "
          "TCaR 분모를 통일하더라도 두 값의 차이에는 이 몫이 섞인 채로 남는다. 아래 표가 "
          "그 크기다.", ""]

    prow = process_rows()
    if prow is not None:
        L += ["| 항목 | FIN | EFF |", "|---|---|---|"]
        L += [f"| {a} | {b} | {c} |" for a, b, c in prow]
        L += ["", "양쪽 다 이 축에서는 데이터가 없다. FIN의 수소·자본비 σ는 D4 관측 부족으로 "
              "사전값이고(A-17), 상관은 추정 부재라 단위행렬이다 — 독립성의 발견이 아니라 "
              "추정의 부재다. EFF는 파일 전체를 `illustrative_estimate`로 표기한다. "
              "그리고 EFF의 전력 반감기 2.0년은 FIN이 대안으로 돌린 10년보다 다섯 배 빠른데, "
              "`docs/price_process_test.md`가 재어 둔 검정력으로는 **월별 120관측에서도 "
              "반감기 2년을 8.1%로만 잡아낸다** — 어느 쪽 값도 데이터가 고른 것이 아니다. "
              "따라서 이 요인은 '한쪽이 틀렸다'가 아니라 **두 모형의 꼬리위험이 서로 다른 "
              "미검증 가정 위에서 계산된다**는 뜻이고, 정량 분해 전에는 TCaR 대조에서 이 몫을 "
              "뺄 수 없다.", ""]

    L += ["## 4. 판정", "",
          "- **설명되는 차이**: 배출 경계(S1 vs S1+2), 기술 집합(BF→EAF 허용 여부), "
          "탄소비용 처리(자원비용 vs 총비용), 설비 해상도(시설 vs 블록), 시나리오 정의, "
          "**확률과정·변동성·요인상관**(위 §3-5 — 꼬리위험 대조에만 걸리고, F20까지 이 "
          "목록에 없었다).",
          "- **아직 정량 분해되지 않은 것**: 위 요인 각각이 감축단가 차이에서 몇 %를 "
          "설명하는지는 계산하지 않았다. 그러려면 한쪽 모형에서 요인을 하나씩 상대 쪽 정의로 "
          "바꿔가며 재실행해야 하고, 그것이 이 항목의 다음 단계다.",
          "- **결론 영향**: 두 모형이 **같은 방향**을 가리키는지만 현재 확인 가능하다. "
          "수준(level)의 일치는 주장할 수 없다.", ""]

    DOCS.mkdir(exist_ok=True)
    out = DOCS / "cross_model_check.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    # EFF 트리는 둘이다 — 별도 저장소와 이 저장소 안의 사본. F20까지 별도 저장소에만
    # 복사해서, 커밋되는 쪽(`cap-efficient/docs/`)이 조용히 낡아 있었다.
    copied = []
    for eff_docs in (EFF / "docs", ROOT / "cap-efficient" / "docs"):
        if eff_docs.exists():
            shutil.copy(out, eff_docs / "cross_model_check.md")
            copied.append(str(eff_docs))
    if copied:
        print(f"[cross] {out.relative_to(ROOT)} + EFF 사본 {len(copied)}개")
    else:
        print(f"[cross] {out.relative_to(ROOT)} (EFF docs 없음 — 사본 미생성)")
    print(df.round(1).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
