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

    # 3. 정책 wedge — 잘못된 시나리오의 계획을 들고 있을 때의 후회비용, 양방향.
    #
    #    D12까지는 한 방향뿐이었다 (NZ15 계획 × B20 실현). 역방향을 넣자 두 가지가 드러난다.
    #
    #    (a) **기준이 시나리오 간에는 비교 불가였다.** 다른 산출표와 맞추려고 `p50`은 탄소지출을
    #        뺀 자원비용 기준인데, 덜 감축하는 계획일수록 내야 할 탄소요금이 빠지므로 싸 보인다.
    #        시나리오를 가로지르는 비교는 `p50_incl_carbon`으로 해야 한다. D12가 §5.3에 적은
    #        후회비용 28,636.4는 자원비용 기준이고, 총비용 기준으로는 22,100.1이다.
    #    (b) **총비용 기준의 역방향 후회비용은 음수다.** B20 계획을 들고 NZ15가 와도 돈은 덜 든다
    #        — 예산을 초과하고 탄소요금을 내면 그만이기 때문이다. 역방향에서 실제로 다른 것은
    #        돈이 아니라 **예산 초과량**이다 (`budget_gap_tco2`).
    #
    #    그래서 초과 1톤을 얼마로 보면 역방향 후회가 0이 되는지(`breakeven_thkrw_per_tco2`)를
    #    같이 낸다. E2는 이 초과를 `max(2×탄소가격, 300천원/tCO2)`로 벌하지만 그 300은
    #    config의 모형 가정이지 실측이 아니다 — 조기 행동의 근거가 가격 전망이 아니라
    #    **예산을 수량으로 강제하는가**에 달려 있다는 것이 이 표의 요지다.
    reg = []
    for co, d in m[m.support == SUPP].groupby("company_id"):
        w = pw[pw.company_id == co]

        def _opt(scen):  # 그 시나리오 경계 위 최소비용 계획을 wedge에서 집는다
            pid = (fp[(fp.company_id == co) & (fp.scenario == scen) & (fp.support == SUPP)
                      & fp.on_frontier].sort_values("p50").plan_id.iloc[0])
            return pid, w[(w.plan_id == pid) & (w.scen_eval == scen)].iloc[0]

        nz_pid, nz_at_nz = _opt(SCEN)
        b20_pid, b20_at_b20 = _opt("B20")
        nz_at_b20 = w[(w.plan_id == nz_pid) & (w.scen_eval == "B20")].iloc[0]
        b20_at_nz = w[(w.plan_id == b20_pid) & (w.scen_eval == SCEN)].iloc[0]

        # 초과 1톤당 몇 천원이면 역방향 후회가 0인가.
        # (십억원 → 천원 = ×1e6), 분모는 NZ15에서의 초과량 차이
        d_money = float(b20_at_nz.p50_incl_carbon) - float(nz_at_nz.p50_incl_carbon)
        d_over = float(b20_at_nz.budget_gap_tco2) - float(nz_at_nz.budget_gap_tco2)
        reg.append(dict(
            company_id=co, nz15_plan_id=nz_pid, b20_plan_id=b20_pid,
            # 순방향: NZ15 계획을 들고 B20이 실현
            fwd_regret_resource=round(float(nz_at_b20.p50) - float(b20_at_b20.p50), 1),
            fwd_regret_total=round(float(nz_at_b20.p50_incl_carbon)
                                   - float(b20_at_b20.p50_incl_carbon), 1),
            # 역방향: B20 계획을 들고 NZ15가 실현
            rev_regret_total=round(d_money, 1),
            rev_budget_gap_tco2=round(d_over, 1),
            # 역방향 후회가 이미 양수면(MCI) 초과를 값매길 필요가 없으므로 비운다
            breakeven_thkrw_per_tco2=(round(-d_money * 1e6 / d_over, 1)
                                      if d_money < 0 and d_over > 0 else None),
            # 그림 6이 쓰는 꼬리위험 (자원비용 기준, D12와 동일)
            tcar_nz15=round(float(nz_at_nz.tcar), 1),
            tcar_b20=round(float(nz_at_b20.tcar), 1)))
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
    # 역방향 후회가 총비용 기준으로 음수인 기업 수 — 4면 "돈만 보면 지연이 이긴다"
    rows["m4_rev_regret_negative"] = int((reg.rev_regret_total < 0).sum())
    for r in reg.itertuples():
        rows[f"m4_regret_{r.company_id.lower()}"] = round(r.fwd_regret_resource, 1)
        rows[f"m4_regret_total_{r.company_id.lower()}"] = round(r.fwd_regret_total, 1)
        rows[f"m4_rev_regret_{r.company_id.lower()}"] = round(r.rev_regret_total, 1)
        rows[f"m4_breakeven_{r.company_id.lower()}"] = r.breakeven_thkrw_per_tco2
    # ②의 B20 열 — §0 대장은 NZ15만 들고 있는데 §5 첫 표는 두 시나리오를 나란히 놓는다
    for r in m[(m.support == SUPP) & (m.scenario == "B20")].itertuples():
        rows[f"m4_m2_b20_{r.company_id.lower()}"] = round(r.cost_per_tco2_thkrw, 1)
    pd.DataFrame(sorted(rows.items()), columns=["key", "value"]).to_csv(
        OUT / "summary.csv", index=False)
    for k, v in sorted(rows.items()):
        print(f"{k:34s} {v}")


if __name__ == "__main__":
    main()
