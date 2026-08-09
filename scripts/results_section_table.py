"""M4 결과 절의 재료 — §5가 인용하는 표를 out/에서 다시 만든다.

§4(M3)와 같은 규약이다. 결과 절이 "이런 값이 나왔다"를 주장하려면 그 표가 원고가 아니라
산출물에서 재생성돼야 한다. 여기서 넷을 낸다.

1. `out/m4/headline.csv`        — 기업×시나리오 ②③ + CAPEX + gap (지원 축은 접는다, 아래 3번 참조)
2. `out/m4/frontier_ladder.csv` — NZ15·none 경계 위 점들: 무엇이 다음 칸으로 옮기는가
3. `out/m4/regret.csv`          — NZ15 계획을 B20이 실현될 때 들고 있는 비용 (정책 wedge)
4. `out/m4/summary.csv`         — 페이퍼 §0 대장에 등록할 스칼라

3번이 이 사이클의 검사다. `support` 축(`none`/`current`)이 모든 산출표에 있지만
**헤드라인을 한 자리도 바꾸지 않는다.** 원인은 D5에 `subsidy_capex`·`ccfd` 행이 하나도
없다는 것이다 (`support_params`가 읽는 것은 그 둘뿐이고, K-ETS 유상할당·가격 collar는
지원 시나리오와 무관하게 `auction_share`로 항상 적용된다). 즉 지원 축은 지금 비어 있고,
표를 두 배로 부풀리면서 "지원 정책을 봤다"는 인상만 준다. 값을 지어내 채우지 않고
그 사실을 세어서 §5가 적는다 — D5에 보조금 행이 들어오는 순간 `m4_support_cells_identical`이
떨어지고 테스트가 그것을 알린다.

Run: .venv/bin/python scripts/results_section_table.py
"""

import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "m4"
PREP = ROOT / "data" / "prepared"
SCEN, SUPP = "NZ15", "none"
# ②가 오름차순으로 이 순서면 순위가 보존된 것 (NZ15 기준 순위)
KEYS = ["cost_per_tco2_thkrw", "tcar_bnkrw", "p50_bnkrw", "capex_total_bnkrw",
        "flex_value_bnkrw", "policy_exposure_bnkrw"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = pd.read_csv(ROOT / "out/e5/metrics_company.csv")
    fp = pd.read_csv(ROOT / "out/e5/frontier_points.csv")
    gap = pd.read_csv(ROOT / "out/e5/gap.csv")
    pw = pd.read_csv(ROOT / "out/e5/policy_wedge.csv")
    d5 = pd.read_csv(PREP / "D5_policy_support.csv")

    # 1. 헤드라인 — 지원 축이 정말로 비어 있는지 먼저 세고, 비어 있으면 접는다
    piv = m.pivot_table(index=["company_id", "scenario"], columns="support", values=KEYS)
    same = [(c, s) for (c, s) in piv.index
            if all(abs(piv.loc[(c, s), (k, "none")] - piv.loc[(c, s), (k, "current")]) <= 1e-9
                   for k in KEYS)]
    head = m[m.support == SUPP].drop(columns=["support"])
    head = head.merge(gap[gap.support == SUPP][["company_id", "scenario",
                                                "gap_cost_bnkrw", "gap_risk_bnkrw"]],
                      on=["company_id", "scenario"], how="left")
    head.round(1).to_csv(OUT / "headline.csv", index=False)

    # 2. 경계 사다리 — 한 칸 옮길 때 무엇이 바뀌고 위험 1원이 얼마인가
    fr = fp[(fp.scenario == SCEN) & (fp.support == SUPP) & fp.on_frontier].copy()
    rungs = []
    for co, d in fr.groupby("company_id"):
        d = d.sort_values("p50").reset_index(drop=True)
        for i, r in d.iterrows():
            prev = d.loc[i - 1] if i else None
            rungs.append(dict(
                company_id=co, rung=i, plan_id=r.plan_id, base_plan_id=r.base_plan_id,
                ppa_share=r.ppa_share, epc=int(r.epc), ccfd=int(r.ccfd),
                p50=round(r.p50, 1), tcar=round(r.tcar, 1),
                # 이 칸으로 오면서 위험 1원을 몇 원에 샀는가 (작을수록 싸다).
                # 위험 감소가 보고 정밀도(0.1십억원) 아래면 비운다 — LOTTE 0.25→0.5처럼
                # TCaR이 사실상 같은 칸에서는 분모가 0에 가까워 비가 수천이 된다.
                price_of_risk=None if prev is None or prev.tcar - r.tcar < 0.1
                else round((r.p50 - prev.p50) / (prev.tcar - r.tcar), 3)))
    pd.DataFrame(rungs).to_csv(OUT / "frontier_ladder.csv", index=False)

    # 3. 정책 wedge — NZ15 최소비용 계획을 B20이 실현될 때 들고 있는 후회비용.
    #    같은 계획을 두 시나리오에서 평가한 것(pw)과, 각 시나리오의 최적 계획(m)의 차.
    reg = []
    for co, d in m[m.support == SUPP].groupby("company_id"):
        nz_plan = fp[(fp.company_id == co) & (fp.scenario == SCEN) & (fp.support == SUPP)
                     & fp.on_frontier].sort_values("p50").iloc[0]
        w = pw[(pw.company_id == co) & (pw.plan_id == nz_plan.plan_id)].set_index("scen_eval")
        b20_opt = float(d[d.scenario == "B20"].p50_bnkrw.iloc[0])
        reg.append(dict(
            company_id=co, plan_id=nz_plan.plan_id,
            p50_nz15=round(float(w.loc["NZ15", "p50"]), 1),
            p50_b20=round(float(w.loc["B20", "p50"]), 1),
            tcar_nz15=round(float(w.loc["NZ15", "tcar"]), 1),
            tcar_b20=round(float(w.loc["B20", "tcar"]), 1),
            b20_optimal_p50=round(b20_opt, 1),
            regret_bnkrw=round(float(w.loc["B20", "p50"]) - b20_opt, 1)))
    reg = pd.DataFrame(reg)
    reg.to_csv(OUT / "regret.csv", index=False)

    # 4. 대장 스칼라
    rows = {
        "m4_frontier_points": len(fr),
        "m4_support_cells_identical": len(same),
        "m4_support_cells_total": len(piv),
        "m4_d5_subsidy_rows": int((d5.instrument == "subsidy_capex").sum()),
        "m4_d5_ccfd_rows": int((d5.instrument == "ccfd").sum()),
        # 엄격한 시나리오가 같은 계획의 꼬리위험을 낮추는가 (기업 수)
        "m4_tcar_lower_under_nz15": int((reg.tcar_nz15 < reg.tcar_b20).sum()),
        # ② 순위가 두 시나리오에서 같은가 (1/0)
        "m4_m2_rank_preserved": int(
            list(m[(m.support == SUPP) & (m.scenario == SCEN)]
                 .sort_values("cost_per_tco2_thkrw").company_id)
            == list(m[(m.support == SUPP) & (m.scenario == "B20")]
                    .sort_values("cost_per_tco2_thkrw").company_id)),
    }
    for r in reg.itertuples():
        rows[f"m4_regret_{r.company_id.lower()}"] = round(r.regret_bnkrw, 1)
    # ②의 B20 열 — §0 대장은 NZ15만 들고 있는데 §5 첫 표는 두 시나리오를 나란히 놓는다
    for r in m[(m.support == SUPP) & (m.scenario == "B20")].itertuples():
        rows[f"m4_m2_b20_{r.company_id.lower()}"] = round(r.cost_per_tco2_thkrw, 1)
    pd.DataFrame(sorted(rows.items()), columns=["key", "value"]).to_csv(
        OUT / "summary.csv", index=False)
    for k, v in sorted(rows.items()):
        print(f"{k:34s} {v}")


if __name__ == "__main__":
    main()
