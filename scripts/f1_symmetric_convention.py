"""F1 진단: hedge_rate의 부호가 '비헤지 기준선 대비 증분' 규약의 산물인가.

2026-08-30 점검 F1: 모든 보고 비용은 무전환 기준선 대비 증분(inc = sims - base_sims)인데
기준선은 ppa=0으로 고정된다. PPA는 계획 쪽 확률 전력항만 결정론으로 바꾸므로, 전환 후
전력 소비가 기준선과 비슷한 기업(석화)은 차분에서 상쇄되던 기준선 전력 분산이 PPA를 걸면
통째로 증분에 남는다. 이 스크립트는 헤드라인 셀(NZ15, support=none)의 후보 집합을 E5와
동일하게 재구성하고, 세 규약으로 hedge_rate(최소비용→최소위험 이동의 ΔTCaR/ΔP50)를 병산한다.

  A 현행:   inc = sims(plan, ppa=x) - base(ppa=0)
  B 대칭:   inc = sims(plan, ppa=x) - base(ppa=x)   — 기준선도 같은 계약을 갖는 세계
  C 총비용: sims(plan, ppa=x) 자체의 분포           — 차분 규약 자체를 제거

출력: out/m9/f1_convention.csv + 요약 stdout. base(out/e2·e5)는 읽기만 한다.
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
from cap.e5_metrics import _carbon_npv, _empty_plan            # noqa: E402
from cap.plancost import auction_share, build_profile, simulate_cost, support_params  # noqa: E402
from cap.schemas import load_input                             # noqa: E402

CONTRACT_GRID = [(ppa, epc) for ppa in (0.0, 0.25, 0.5, 0.75, 1.0) for epc in (0, 1)]
SCEN, SUPP = "NZ15", "none"


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

    rows = []
    for company in sorted(idx.company_id.unique()):
        region = COMPANY_REGION[company]
        px = _central_px(prices, region, SCEN, years, cfg, cal)
        base0 = build_profile(_empty_plan(company), fac, d3, px, years, cfg)
        # 기준선 시뮬을 PPA 수준별로 한 번씩 — 대칭 규약(B)의 반쪽
        base_by_ppa = {v: simulate_cost(replace(base0, ppa=v), px, shocks, sp, cfg)
                       for v in (0.0, 0.25, 0.5, 0.75, 1.0)}
        carb_base = _carbon_npv(base0, px, disc_v, auc_v)

        g = idx[(idx.company_id == company) & (idx.scenario == SCEN) & (~idx.is_disclosed)]
        scheds = {}
        for _, pr in g.iterrows():
            df = pd.read_csv(e2dir / "plans" / f"plan_{pr.plan_id}.csv")
            key = tuple(sorted((r.facility_id, r.tech_id, int(r.adopt_year))
                               for r in df.itertuples() if pd.notna(r.tech_id)))
            if key not in scheds or (bool(pr.budget_ok) and not scheds[key]["ok"]):
                scheds[key] = dict(pid=pr.plan_id, df=df, ok=bool(pr.budget_ok))

        for sc_ in scheds.values():
            if not sc_["ok"]:
                continue
            prof0 = build_profile(sc_["df"], fac, d3, px, years, cfg)
            dcarb0 = None
            for k, (ppa_v, epc_v) in enumerate(CONTRACT_GRID):
                prof = replace(prof0, ppa=ppa_v, epc=epc_v, ccfd=0)
                sims = simulate_cost(prof, px, shocks, sp, cfg)
                if dcarb0 is None:
                    dcarb0 = _carbon_npv(prof, px, disc_v, auc_v) - carb_base
                for conv, ref in (("A_current", base_by_ppa[0.0]),
                                  ("B_symmetric", base_by_ppa[ppa_v]),
                                  ("C_total", None)):
                    d = sims if ref is None else sims - ref
                    p50 = float(np.median(d)) - (dcarb0 if ref is not None else 0.0)
                    tcar = float(np.percentile(d, 90) - np.median(d))
                    rows.append(dict(company_id=company, plan_id=f"{sc_['pid']}.c{k:02d}",
                                     base_plan_id=sc_["pid"], ppa=ppa_v, epc=epc_v,
                                     convention=conv, p50=round(p50, 1), tcar=round(tcar, 1)))

    out = pd.DataFrame(rows)
    odir = ROOT / "out" / "m9"
    odir.mkdir(parents=True, exist_ok=True)
    out.to_csv(odir / "f1_convention.csv", index=False)

    print(f"# F1 규약 진단 — {SCEN}, support={SUPP}, 후보 = 예산정합 일정 x 계약격자 10")
    print(f"{'firm':6} {'conv':12} {'cost-min plan':>16} {'risk-min plan':>16} "
          f"{'ΔTCaR':>10} {'ΔP50':>9} {'hedge_rate':>10}  PPA↑=TCaR?")
    for company in sorted(out.company_id.unique()):
        for conv in ("A_current", "B_symmetric", "C_total"):
            s = out[(out.company_id == company) & (out.convention == conv)]
            cm = s.loc[s.p50.idxmin()]
            rm = s.loc[s.tcar.idxmin()]
            dt, dp = cm.tcar - rm.tcar, rm.p50 - cm.p50
            hr = dt / dp if dp > 0 else float("nan")
            # 같은 일정 안에서 PPA 0 -> 1.0 (epc=0) 이동이 TCaR을 올리는가
            sch = s[(s.base_plan_id == cm.base_plan_id) & (s.epc == 0)]
            up = float(sch[sch.ppa == 1.0].tcar.iloc[0] - sch[sch.ppa == 0.0].tcar.iloc[0])
            print(f"{company:6} {conv:12} {cm.plan_id:>16} {rm.plan_id:>16} "
                  f"{dt:10.1f} {dp:9.1f} {hr:10.2f}  {'+' if up > 0 else '-'}{abs(up):.1f}")
    print(f"\n-> {odir / 'f1_convention.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
