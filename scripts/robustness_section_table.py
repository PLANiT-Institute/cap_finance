"""M5 강건성 절의 재료 — §6이 인용하는 표를 out/에서 다시 만든다.

§4(M3)·§5(M4)와 같은 규약이다. "결론이 흔들리지 않는다"는 주장은 원고가 아니라 산출물에서
재생성돼야 한다. 넷을 낸다.

1. `out/m5/checks.csv`       — 저장소에 이미 있는 강건성 검증 하나에 한 줄. 무엇을 흔들었고
                               순위가 보존되는가, 헤드라인이 몇 배 움직이는가.
2. `out/m5/bundle_matrix.csv`— `scripts/run_scenarios.py` 묶음별 base 대비 변화. **E2를 공유한
                               채 돌린 묶음은 정의상 변화가 0이므로 `inert`로 표시한다.**
3. `out/m5/penalty_axis.csv` — `milp.budget_violation_floor_thkrw`(§5.3.1의 결론이 매달린
                               무출처 T5 가정)를 값매김 축으로 훑는다.
4. `out/m5/summary.csv`      — §0 대장 스칼라.

2번이 이 사이클의 검사다. 시나리오 묶음 넷(`carbon_slow`·`carbon_fast`·`ppa_costly`·
`retire_free`)이 **헤드라인 ②③을 한 자리도 바꾸지 않는 수**를 요약표에 싣고 있었다. 이 축들은
E2에서만 계획 선택에 닿는데 묶음은 E2를 심볼릭 링크로 공유하기 때문이다. 모형 결함이 아니라
실행 규약의 결함이고, D12의 빈 지원 축과 같은 종류다 — 표에 행이 있으면 독자는 "흔들어 봤다"고
읽는다. 흔든 적이 없다.

**다만 둘로 갈린다.** `ppa_costly`·`retire_free`는 모든 열에서 base와 같다(완전 무력).
`carbon_slow`·`carbon_fast`는 계획을 못 바꾸지만 E5의 탄소지출에는 닿아 탄소 포함 P50이
22~24조원 움직인다 — "낼 돈은 바뀌는데 할 일은 못 바꾼다"는 것이고, 계획 메뉴가 고정된
탓이므로 강건성의 증거가 아니다. `run_scenarios.py`의 `REPLAN_REQUIRED`가 이제 재계획 없는
실행을 막는다.

3번은 D13 인계다. E4 정본 비용은 E2의 예산위반 벌칙을 **일부러 제외**하므로(e5_metrics.py의
주석), 초과 1톤을 얼마로 값매기는가는 사후 축이 된다 — 재실행 없이 훑을 수 있다. 벌칙이
계획 **탐색**을 바꾸는 통로는 이 축으로 잡히지 않는다. 그쪽은 `penalty_none` 묶음이 잡는다.

Run: .venv/bin/python scripts/robustness_section_table.py
"""

import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "m5"
SCEN, SUPP = "NZ15", "none"
# 값매김 축: 0 = 별도 제재 없음(탄소요금 2배만), 300 = config 정본, [150,600] = 인벤토리 밴드
PENALTY_GRID = [0.0, 50.0, 150.0, 300.0, 600.0]
# p50_incl_carbon을 빼면 안 된다. D14에서 처음 이 표를 만들 때 뺐다가 carbon_slow·
# carbon_fast를 "아무것도 안 바꾼다"로 잘못 판정했다 — 유상할당 램프는 계획 선택(E2)에는
# 못 닿아도 E5의 탄소지출에는 닿으므로, 낼 돈은 두 배 넘게 움직인다. 무력한 축과 헤드라인에만
# 안 닿는 축은 다른 것이고, §6.2가 그 둘을 갈라 적는다.
KEYS = ["p50_bnkrw", "cost_per_tco2_thkrw", "tcar_bnkrw", "capex_total_bnkrw",
        "p50_incl_carbon_bnkrw"]


def _rank(df, col="cost_per_tco2_thkrw"):
    return list(df.sort_values(col).company_id)


def checks(reg) -> pd.DataFrame:
    """저장소에 이미 있는 검증들을 한 표로. 값은 전부 CSV에서 다시 읽는다."""
    rows = []
    fr = pd.read_csv(ROOT / "out/e5/frontier_points.csv").query(
        "scenario==@SCEN and support==@SUPP and not is_disclosed and budget_ok")
    m = pd.read_csv(ROOT / "out/e5/metrics_company.csv").query(
        "scenario==@SCEN and support==@SUPP")
    base_rank = _rank(m)

    # I2 구조 대안 — 위험중립(P50) 대신 위험회피(P90)로 고르면
    def lcoa(basis):
        b = fr.sort_values(basis).groupby("company_id").head(1)
        return (b.assign(l=b[basis] * 1e6 / b.abated_tco2_disc)
                .rename(columns={"l": "cost_per_tco2_thkrw"}))
    p50, p90 = lcoa("p50"), lcoa("p90")
    tail = (p90.set_index("company_id").cost_per_tco2_thkrw
            / p50.set_index("company_id").cost_per_tco2_thkrw)
    rows.append(dict(check="I2 결정기준 P50→P90", varies="위험선호",
                     rank_preserved=int(_rank(p50) == _rank(p90)),
                     magnitude=f"② ×{tail.min():.1f}~×{tail.max():.1f}",
                     source="docs/robustness_structural.md"))

    # I4 표본 안정성 — 시드만 바꿔 E3–E5 재실행
    ss = pd.read_csv(ROOT / "docs/seed_stability.csv").query(
        "scenario==@SCEN and support==@SUPP")
    cv = ss.groupby("company_id")[["cost_per_tco2_thkrw", "tcar_bnkrw"]].agg(
        lambda s: s.std() / s.mean())
    rows.append(dict(check=f"I4 시드 {ss.seed.nunique()}개", varies="난수",
                     rank_preserved=int(all(
                         _rank(ss[ss.seed == s]) == base_rank for s in ss.seed.unique())),
                     magnitude=f"CV ② ≤{cv.cost_per_tco2_thkrw.max():.2%} / ③ ≤{cv.tcar_bnkrw.max():.2%}",
                     source="docs/seed_stability.md"))

    # F3 파라미터 불확실성 전파 — 상위 10개를 동시에 추첨.
    # 폭을 섞으면 안 된다: 파라미터 몫은 추첨 폭에 거의 비례하므로(한계 9), 페이퍼가
    # 인용하는 ±30% 규약만 남긴다. 폭 전체를 섞으면 13~44%처럼 넓어 보이는데 그 폭은
    # 불확실성이 아니라 우리가 고른 추첨 폭의 목록이다.
    for tag, lbl in [("", "±30% 규약"), ("_bands", "문헌 밴드")]:
        u = pd.read_csv(ROOT / f"out/uncertainty/decomposition{tag}.csv").query(
            "scenario==@SCEN and support==@SUPP and width==0.30")
        rows.append(dict(check=f"F3 파라미터 전파 ({lbl})", varies="상위 10 파라미터",
                         rank_preserved="",
                         magnitude=f"③의 파라미터 몫 {u.param_share_pct.min():.0f}~{u.param_share_pct.max():.0f}%",
                         source="docs/uncertainty_propagation.md"))

    # L1 확률과정 대안 — GBM 대신 OU
    g, o = (pd.read_csv(ROOT / f"out/process/{k}/e5/metrics_company.csv").query(
        "scenario==@SCEN and support==@SUPP").set_index("company_id") for k in ("gbm", "ou"))
    r = (o.tcar_bnkrw / g.tcar_bnkrw).dropna()
    rows.append(dict(check="L1 확률과정 GBM→OU", varies="가격 확률과정",
                     rank_preserved=int(_rank(o.reset_index()) == _rank(g.reset_index())),
                     magnitude=f"③ ×{r.min():.2f}~×{r.max():.2f}",
                     source="docs/process_alternative.md"))

    # M8 후보집합 강제 확장 — 기술 일정 축에 epsilon-constraint
    m8 = pd.read_csv(ROOT / "out/m8/summary.csv")
    rows.append(dict(check="M8 후보집합 강제 확장", varies="기술 일정 상한",
                     rank_preserved="",
                     magnitude=f"강제 {int(m8.caps_tried.sum())}개 중 비지배 "
                               f"헤드라인 {int(m8.nondominated_headline.sum())} / "
                               f"L2규약 {int(m8.nondominated_l2.sum())}",
                     source="docs/frontier_degeneracy.md"))

    # H2 후향 검증 — 주입 표준값이 실적을 재현하는가
    bt = pd.read_csv(ROOT / "docs/validation_backtest.csv")
    rows.append(dict(check="H2 후향 검증 2020–24", varies="—(대조)",
                     rank_preserved="",
                     magnitude=f"배출강도 오차 최대 {bt.err_pct.abs().max():.1f}% "
                               f"({bt.loc[bt.err_pct.abs().idxmax()].company_id})",
                     source="docs/validation_backtest.md"))

    # D14 신규: §5.3.1의 결론이 매달린 벌칙 바닥
    be = reg.breakeven_thkrw_per_tco2.dropna()
    rows.append(dict(check="D14 예산위반 벌칙 바닥", varies="milp.budget_violation_floor_thkrw",
                     rank_preserved="",
                     magnitude=f"역방향 후회 부호 전환점 {be.min():.1f}~{be.max():.1f} 천원/tCO2 "
                               f"(인벤토리 밴드 150–600의 아래)",
                     source="out/m5/penalty_axis.csv"))
    return pd.DataFrame(rows)


def bundle_matrix() -> pd.DataFrame:
    """묶음별 base 대비 변화. 0이면 그 묶음은 아무것도 흔들지 않았다."""
    s = pd.read_csv(ROOT / "out/scenarios/summary.csv")
    idx = ["company_id", "scenario", "support"]
    b = s[s.bundle == "base"].set_index(idx)[KEYS]
    rows = []
    for n, d in s[s.bundle != "base"].groupby("bundle"):
        x = d.set_index(idx)[KEYS]
        diff = (x - b).abs().max().max()
        v = d.query("scenario==@SCEN and support==@SUPP")
        rows.append(dict(
            bundle=n, replanned=bool(d.replanned.iloc[0]),
            # 부동소수 잡음(1e-9 이하)은 변화가 아니다
            inert=int(diff <= 1e-6),
            max_abs_delta=round(float(diff), 3),
            d_m2_pct=round(float(((v.set_index("company_id").cost_per_tco2_thkrw
                                   / b.xs((SCEN, SUPP), level=(1, 2)).cost_per_tco2_thkrw - 1)
                                  * 100).abs().max()), 1),
            d_tcar_pct=round(float(((v.set_index("company_id").tcar_bnkrw
                                     / b.xs((SCEN, SUPP), level=(1, 2)).tcar_bnkrw - 1)
                                    * 100).abs().max()), 1),
            # 헤드라인에 안 닿아도 낼 돈은 움직일 수 있다 (유상할당 램프가 그렇다)
            d_p50carbon_bnkrw=round(float((v.set_index("company_id").p50_incl_carbon_bnkrw
                                           - b.xs((SCEN, SUPP), level=(1, 2)).p50_incl_carbon_bnkrw
                                           ).abs().max()), 1),
            rank_preserved=int(_rank(v) == _rank(
                s[s.bundle == "base"].query("scenario==@SCEN and support==@SUPP")))))
    return pd.DataFrame(rows).sort_values("bundle")


def penalty_axis(reg) -> pd.DataFrame:
    """초과 1톤을 φ 천원으로 값매기면 역방향 후회의 부호가 어디서 뒤집히는가.

    역방향 후회(총비용) + φ × 초과량. 부호가 +면 지연이 지고, −면 지연이 이긴다.
    E4는 E2의 벌칙을 비용에 넣지 않으므로 이 축은 재실행 없이 정확하다.
    """
    rows = []
    for r in reg.itertuples():
        for phi in PENALTY_GRID:
            v = r.rev_regret_total + phi * r.rev_budget_gap_tco2 / 1e6
            rows.append(dict(company_id=r.company_id, floor_thkrw_per_tco2=phi,
                             rev_regret_penalised_bnkrw=round(v, 1),
                             early_action_wins=int(v > 0)))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reg = pd.read_csv(ROOT / "out/m4/regret.csv")

    ck = checks(reg)
    ck.to_csv(OUT / "checks.csv", index=False)
    bm = bundle_matrix()
    bm.to_csv(OUT / "bundle_matrix.csv", index=False)
    pa = penalty_axis(reg)
    pa.to_csv(OUT / "penalty_axis.csv", index=False)

    wins = pa.groupby("floor_thkrw_per_tco2").early_action_wins.sum()
    rows = {
        "m5_checks_total": len(ck),
        "m5_checks_rank_preserved": int(sum(c == 1 for c in ck.rank_preserved if c != "")),
        "m5_bundles_total": len(bm) + 1,          # +base
        "m5_bundles_inert": int(bm.inert.sum()),
        # 헤드라인 ②③에만 안 닿는 축 — 무력한 것과 다르다 (§6.2)
        "m5_bundles_headline_inert": int(((bm.d_m2_pct == 0) & (bm.d_tcar_pct == 0)).sum()),
        "m5_bundles_replanned": int(bm.replanned.sum()),
        "m5_bundle_rank_reversals": int((bm.rank_preserved == 0).sum()),
        # 벌칙 바닥을 치우면(φ=0) 조기 전환이 몇 회사에서 이기는가 / 정본 300에서는
        "m5_penalty0_early_wins": int(wins.get(0.0, 0)),
        "m5_penalty300_early_wins": int(wins.get(300.0, 0)),
        "m5_penalty_band_low_early_wins": int(wins.get(150.0, 0)),
        "m5_breakeven_max_thkrw": float(reg.breakeven_thkrw_per_tco2.max()),
    }
    for r in bm.itertuples():
        rows[f"m5_d_m2_pct_{r.bundle}"] = r.d_m2_pct
    pd.DataFrame(sorted(rows.items()), columns=["key", "value"]).to_csv(
        OUT / "summary.csv", index=False)
    print(ck.to_string(index=False), "\n")
    print(bm.to_string(index=False), "\n")
    print(pa.pivot(index="company_id", columns="floor_thkrw_per_tco2",
                   values="rev_regret_penalised_bnkrw").to_string(), "\n")
    for k, v in sorted(rows.items()):
        print(f"{k:32s} {v}")


if __name__ == "__main__":
    main()
