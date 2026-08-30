"""F2+F3 진단: 계약을 대칭 처리하고 감축량을 통제하면 frontier gap이 얼마나 남는가.

2026-08-30 점검의 두 발견을 함께 검사한다.
  F2: E5는 후보 일정마다 계약 10변형을 깔지만 공시 좌표는 ppa=epc=ccfd=0 한 점 —
      gap의 일부는 "우리가 공시점에 부여한 계약 기본값"의 가격이다.
  F3: gap이 등가 감축량에서 측정되지 않는다 — MCI B20 공시계획은 경계 위 계획보다
      6.2배 더 감축하는데 gap_risk가 공시 TCaR 전액이다.

네 gap을 병산한다 (공시 좌표가 존재하는 NSC·MCI × NZ15·B20, support=none):
  G0 현행 재현:       공시(계약 0) vs 전체 후보 경계          — out/e5/gap.csv와 대조
  G1 계약 대칭(F2):   공시 일정 x 계약격자 10의 파레토점 vs 같은 경계 (각 다리의 최소)
  G2 감축 통제(F3):   G0의 경계를 공시 감축량 ±20% 후보로 제한
  G3 둘 다:           G1 + G2 — "진짜 gap"의 1차 추정

출력: out/m9/f2f3_true_gap.csv + 요약 stdout. base는 읽기만 한다.
"""
from __future__ import annotations

import pathlib
import sys
from dataclasses import replace

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cap import config as C                                    # noqa: E402
from cap.e1_constraints import COMPANY_REGION                  # noqa: E402
from cap.e2_milp import _prep_company                          # noqa: E402
from cap.e3_prices import load_shocks                          # noqa: E402
from cap.e4_revalue import _central_px                         # noqa: E402
from cap.e5_metrics import _carbon_npv, _empty_plan, _frontier, _gap  # noqa: E402
from cap.plancost import auction_share, build_profile, simulate_cost, support_params  # noqa: E402
from cap.schemas import load_input                             # noqa: E402

CONTRACT_GRID = [(ppa, epc) for ppa in (0.0, 0.25, 0.5, 0.75, 1.0) for epc in (0, 1)]
SUPP = "none"
ABATE_BAND = 0.20


def main() -> int:
    cfg = C.load()
    ddir = C.data_dir(cfg)
    e2dir = C.out_dir(cfg, "e2")
    fac, d3, cal = _prep_company(cfg, ddir)
    d5 = load_input(ddir, "D5_policy_support")
    prices = pd.read_csv(C.out_dir(cfg, "e1") / "price_paths_central.csv")
    idx = pd.read_csv(e2dir / "plan_index.csv")
    min_slack = (idx[~idx.is_disclosed].groupby(["company_id", "scenario"])
                 .budget_slack_tco2.min().rename("min_slack"))
    idx = idx.merge(min_slack, on=["company_id", "scenario"], how="left")
    idx["budget_ok"] = idx.budget_slack_tco2 <= idx.min_slack * 1.25 + 1e6
    shocks = load_shocks(cfg)
    years = np.arange(cfg.years.start, cfg.years.end + 1)
    disc_v = (1 + cfg.discount_rate) ** -(years - years[0])
    auc_v = auction_share(years, cfg)
    sp = support_params(d5, SUPP, years)
    ref_gap = pd.read_csv(C.out_dir(cfg, "e5") / "gap.csv").query("support == @SUPP")

    out = []
    for scen in cfg.scenarios:
        for company in sorted(idx.company_id.unique()):
            g = idx[(idx.company_id == company) & (idx.scenario == scen)]
            disc_rows = g[g.is_disclosed]
            if disc_rows.empty:
                continue
            region = COMPANY_REGION[company]
            px = _central_px(prices, region, scen, years, cfg, cal)
            base_prof = build_profile(_empty_plan(company), fac, d3, px, years, cfg)
            base_sims = simulate_cost(base_prof, px, shocks, sp, cfg)
            carb_base = _carbon_npv(base_prof, px, disc_v, auc_v)

            def evaluate(prof):
                sims = simulate_cost(prof, px, shocks, sp, cfg)
                inc = sims - base_sims
                dcarb = _carbon_npv(prof, px, disc_v, auc_v) - carb_base
                p50 = float(np.median(inc)) - dcarb
                p90 = float(np.percentile(inc, 90)) - dcarb
                ab = float(((base_prof.emissions - prof.emissions) * disc_v).sum())
                return p50, p90 - p50, ab

            # 후보 경계 (E5와 동일 규칙: 예산정합 일정 x 계약격자)
            scheds = {}
            for _, pr in g[~g.is_disclosed].iterrows():
                df = pd.read_csv(e2dir / "plans" / f"plan_{pr.plan_id}.csv")
                key = tuple(sorted((r.facility_id, r.tech_id, int(r.adopt_year))
                                   for r in df.itertuples() if pd.notna(r.tech_id)))
                if key not in scheds or (bool(pr.budget_ok) and not scheds[key]["ok"]):
                    scheds[key] = dict(pid=pr.plan_id, df=df, ok=bool(pr.budget_ok))
            cand = []
            for sc_ in scheds.values():
                if not sc_["ok"]:
                    continue
                prof0 = build_profile(sc_["df"], fac, d3, px, years, cfg)
                for k, (ppa_v, epc_v) in enumerate(CONTRACT_GRID):
                    p50, tcar, ab = evaluate(replace(prof0, ppa=ppa_v, epc=epc_v, ccfd=0))
                    cand.append(dict(plan_id=f"{sc_['pid']}.c{k:02d}", p50=p50, tcar=tcar,
                                     abated=ab))
            cand = pd.DataFrame(cand)

            # 공시 일정 x 계약격자
            df_d = pd.read_csv(e2dir / "plans" / f"plan_{disc_rows.iloc[0].plan_id}.csv")
            prof_d0 = build_profile(df_d, fac, d3, px, years, cfg)
            disc = []
            for k, (ppa_v, epc_v) in enumerate(CONTRACT_GRID):
                p50, tcar, ab = evaluate(replace(prof_d0, ppa=ppa_v, epc=epc_v, ccfd=0))
                disc.append(dict(k=k, ppa=ppa_v, epc=epc_v, p50=p50, tcar=tcar, abated=ab))
            disc = pd.DataFrame(disc)
            d0 = disc[(disc.ppa == 0) & (disc.epc == 0)].iloc[0]

            fr_all = _frontier(cand)
            in_band = cand[(cand.abated >= d0.abated * (1 - ABATE_BAND)) &
                           (cand.abated <= d0.abated * (1 + ABATE_BAND))]
            fr_band = _frontier(in_band) if len(in_band) else None

            def legs(frontier, pts):
                """각 다리의 최소 (파레토 공시점들 중) — NaN은 건너뜀."""
                gc, gr = [], []
                for p in pts.itertuples():
                    c, r = _gap(frontier, p)
                    if not np.isnan(c):
                        gc.append(c)
                    if not np.isnan(r):
                        gr.append(r)
                return (min(gc) if gc else np.nan, min(gr) if gr else np.nan)

            disc_pareto = _frontier(disc)
            g0 = legs(fr_all, disc.loc[[d0.name]])
            g1 = legs(fr_all, disc_pareto)
            g2 = legs(fr_band, disc.loc[[d0.name]]) if fr_band is not None else (np.nan, np.nan)
            g3 = legs(fr_band, disc_pareto) if fr_band is not None else (np.nan, np.nan)
            ref = ref_gap[(ref_gap.company_id == company) & (ref_gap.scenario == scen)]
            out.append(dict(company_id=company, scenario=scen,
                            ref_cost=float(ref.gap_cost_bnkrw.iloc[0]),
                            ref_risk=float(ref.gap_risk_bnkrw.iloc[0]),
                            g0_cost=g0[0], g0_risk=g0[1], g1_cost=g1[0], g1_risk=g1[1],
                            g2_cost=g2[0], g2_risk=g2[1], g3_cost=g3[0], g3_risk=g3[1],
                            band_candidates=0 if fr_band is None else int(len(in_band)),
                            disclosed_abated=float(d0.abated),
                            frontier_abated_min=float(cand.abated.min()),
                            frontier_abated_max=float(cand.abated.max())))

    res = pd.DataFrame(out).round(1)
    odir = ROOT / "out" / "m9"
    odir.mkdir(parents=True, exist_ok=True)
    res.to_csv(odir / "f2f3_true_gap.csv", index=False)
    with pd.option_context("display.width", 200):
        print(res.to_string(index=False))
    print(f"\n-> {odir / 'f2f3_true_gap.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
